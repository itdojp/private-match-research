from __future__ import annotations

import io
import socket
import unittest
import urllib.error
from contextlib import redirect_stderr
from email.message import Message
from pathlib import Path
from unittest import mock

import yaml

from scripts.validate_research import (
    MAX_URL_REDIRECTS,
    MAX_URL_RESPONSE_BYTES,
    check_url,
    check_urls,
    main,
    validate_url_references,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ADDRESS = "93.184.216.34"


class FakeResponse:
    def __init__(
        self,
        status: int = 200,
        body: bytes = b"",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self.body = body
        self.headers = headers or {}

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self.body if size < 0 else self.body[:size]


class FakeOpener:
    def __init__(self, *effects: object) -> None:
        self.effects = list(effects)
        self.requests: list[object] = []

    def open(self, request: object, *, timeout: float) -> FakeResponse:
        self.requests.append(request)
        if not self.effects:
            raise AssertionError("unexpected HTTP request")
        effect = self.effects.pop(0)
        if callable(effect):
            effect = effect(request)
        if isinstance(effect, BaseException):
            raise effect
        if not isinstance(effect, FakeResponse):
            raise AssertionError(f"invalid fake HTTP effect: {effect!r}")
        return effect


def http_error(
    url: str, status: int, location: str | None = None
) -> urllib.error.HTTPError:
    headers = Message()
    if location is not None:
        headers["Location"] = location
    return urllib.error.HTTPError(url, status, f"HTTP {status}", headers, io.BytesIO())


def public_resolver(_host: str, _port: int) -> list[str]:
    return [PUBLIC_ADDRESS]


class UrlObservationSafetyTests(unittest.TestCase):
    def test_local_reference_validation_never_resolves_hostnames(self) -> None:
        with mock.patch("scripts.validate_research.socket.getaddrinfo") as mocked_dns:
            findings = validate_url_references(
                [
                    "https://public.example/source",
                    "https://127.0.0.1/private",
                ]
            )

        mocked_dns.assert_not_called()
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "error")
        self.assertEqual(findings[0].code, "unsafe-url-reference")
        self.assertEqual(findings[0].path, "https://127.0.0.1/private")

    def test_public_https_hostname_is_observed_with_mocked_dns_and_http(self) -> None:
        opener = FakeOpener(FakeResponse(status=200))

        status, detail = check_url(
            "https://example.com/source",
            5.0,
            resolver=public_resolver,
            opener=opener,
        )

        self.assertEqual((status, detail), ("ok", "HTTP 200"))
        self.assertEqual(len(opener.requests), 1)

    def test_non_public_literals_and_localhost_are_rejected_without_http(self) -> None:
        unsafe_urls = [
            "https://localhost/",
            "https://127.0.0.1/",
            "https://[::1]/",
            "https://10.1.2.3/",
            "https://192.168.1.10/",
            "https://169.254.1.2/",
            "https://169.254.169.254/latest/meta-data/",
            "https://224.0.0.1/",
            "https://0.0.0.0/",
            "https://192.0.2.10/",
        ]
        for url in unsafe_urls:
            with self.subTest(url=url):
                opener = FakeOpener()
                status, _detail = check_url(url, 5.0, opener=opener)
                self.assertEqual(status, "unsafe-destination")
                self.assertEqual(opener.requests, [])

    def test_public_hostname_resolving_to_private_address_is_rejected(self) -> None:
        opener = FakeOpener()

        status, _detail = check_url(
            "https://public.example/source",
            5.0,
            resolver=lambda _host, _port: ["10.0.0.8"],
            opener=opener,
        )

        self.assertEqual(status, "unsafe-destination")
        self.assertEqual(opener.requests, [])

    def test_any_private_answer_rejects_a_mixed_dns_result(self) -> None:
        status, _detail = check_url(
            "https://public.example/source",
            5.0,
            resolver=lambda _host, _port: [PUBLIC_ADDRESS, "192.168.1.8"],
            opener=FakeOpener(),
        )

        self.assertEqual(status, "unsafe-destination")

    def test_redirect_from_public_url_to_private_address_is_rejected(self) -> None:
        opener = FakeOpener(
            http_error(
                "https://example.com/start",
                302,
                "https://169.254.169.254/latest/meta-data/",
            )
        )

        status, _detail = check_url(
            "https://example.com/start",
            5.0,
            resolver=public_resolver,
            opener=opener,
        )

        self.assertEqual(status, "unsafe-destination")
        self.assertEqual(len(opener.requests), 1)

    def test_url_userinfo_is_rejected_and_redacted_from_findings(self) -> None:
        status, _detail = check_url(
            "https://user:secret@example.com/source",
            5.0,
            resolver=public_resolver,
            opener=FakeOpener(),
        )
        self.assertEqual(status, "unsafe-destination")

        with mock.patch(
            "scripts.validate_research.check_url",
            return_value=("unsafe-destination", "URL userinfo is not allowed"),
        ):
            findings = check_urls(
                ["https://user:secret@example.com/source"],
                timeout=5.0,
                policy="warn",
            )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "error")
        self.assertNotIn("secret", findings[0].path)
        self.assertEqual(findings[0].path, "https://example.com/source")

    def test_unsupported_port_is_rejected(self) -> None:
        status, detail = check_url(
            "https://example.com:8443/source",
            5.0,
            resolver=public_resolver,
            opener=FakeOpener(),
        )

        self.assertEqual(status, "unsafe-destination")
        self.assertIn("port", detail)

    def test_excessive_redirect_chain_is_rejected(self) -> None:
        def redirect(request: object) -> urllib.error.HTTPError:
            request_url = getattr(request, "full_url")
            return http_error(request_url, 302, "/next")

        opener = FakeOpener(*(redirect for _ in range(MAX_URL_REDIRECTS + 1)))

        status, detail = check_url(
            "https://example.com/start",
            5.0,
            resolver=public_resolver,
            opener=opener,
        )

        self.assertEqual(status, "redirect-limit")
        self.assertIn(str(MAX_URL_REDIRECTS), detail)
        self.assertEqual(len(opener.requests), MAX_URL_REDIRECTS + 1)

    def test_get_fallback_limits_response_size_and_does_not_report_body(self) -> None:
        secret_body = b"sensitive-body" + b"x" * MAX_URL_RESPONSE_BYTES
        opener = FakeOpener(
            http_error("https://example.com/source", 405),
            FakeResponse(status=200, body=secret_body),
        )

        status, detail = check_url(
            "https://example.com/source",
            5.0,
            resolver=public_resolver,
            opener=opener,
        )

        self.assertEqual(status, "response-too-large")
        self.assertNotIn("sensitive-body", detail)

    def test_http_and_dns_failures_are_distinct(self) -> None:
        http_status, _http_detail = check_url(
            "https://example.com/missing",
            5.0,
            resolver=public_resolver,
            opener=FakeOpener(http_error("https://example.com/missing", 404)),
        )

        def failing_resolver(_host: str, _port: int) -> list[str]:
            raise socket.gaierror("mocked DNS failure")

        network_status, _network_detail = check_url(
            "https://example.invalid/source",
            5.0,
            resolver=failing_resolver,
            opener=FakeOpener(),
        )

        self.assertEqual(http_status, "http-failure")
        self.assertEqual(network_status, "network-failure")

    def test_pull_request_event_cannot_enable_network_observation(self) -> None:
        with (
            mock.patch.dict("os.environ", {"GITHUB_EVENT_NAME": "pull_request"}),
            mock.patch("scripts.validate_research.check_urls") as mocked_check_urls,
            redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as raised,
        ):
            main(
                [
                    "--root",
                    str(ROOT),
                    "--check-urls",
                    "--trusted-url-observation",
                ]
            )

        self.assertEqual(raised.exception.code, 2)
        mocked_check_urls.assert_not_called()

    def test_workflows_keep_pull_requests_local_only(self) -> None:
        quality = yaml.load(
            (ROOT / ".github/workflows/research-quality.yml").read_text(
                encoding="utf-8"
            ),
            Loader=yaml.BaseLoader,
        )
        observation = yaml.load(
            (ROOT / ".github/workflows/research-url-observation.yml").read_text(
                encoding="utf-8"
            ),
            Loader=yaml.BaseLoader,
        )

        self.assertIn("pull_request", quality["on"])
        self.assertNotIn("pull_request_target", quality["on"])
        quality_commands = "\n".join(
            str(step.get("run", "")) for step in quality["jobs"]["validate"]["steps"]
        )
        self.assertNotIn("--check-urls", quality_commands)

        self.assertNotIn("pull_request", observation["on"])
        self.assertNotIn("pull_request_target", observation["on"])
        self.assertEqual(
            set(observation["on"]),
            {"push", "schedule", "workflow_dispatch"},
        )
        observation_commands = "\n".join(
            str(step.get("run", "")) for step in observation["jobs"]["observe"]["steps"]
        )
        self.assertIn("--check-urls", observation_commands)
        self.assertIn("--trusted-url-observation", observation_commands)


if __name__ == "__main__":
    unittest.main()
