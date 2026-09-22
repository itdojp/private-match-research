# Private Match Research

Private Matchの市場、ユースケース、代替手段、プライバシー強化技術（PETs）を、
一次情報と再現可能な方法に基づいて調査する公開リポジトリです。
株式会社アイティードゥ（ITDO Inc.）が管理します。

> **状態：pre-alpha / research baseline。**
> 調査レコード、比較資料、実験計画、合成入力の生成・検証ツールを公開しています。
> PET候補のローカル実行結果はありません。市場需要、暗号学的安全性、法令適合、
> production readinessを証明するものではありません。

## はじめに読むもの

| 知りたいこと | 入口 |
| --- | --- |
| 調査対象・証拠の扱い | [調査範囲](docs/RESEARCH_SCOPE.md)・[調査方法](docs/RESEARCH_METHOD.md) |
| 競合・隣接製品・OSS構成要素 | [構造化競合インデックス](landscape/competitor-index.md) |
| PETを使わない代替手段 | [代替手段の比較](landscape/substitutes/README.md) |
| 技術ごとの信頼モデルと限界 | [技術比較](technologies/README.md) |
| 今後の実験と未実行の項目 | [実験計画](benchmarks/README.md)・[技術選択ADR](decisions/ADR-0001-first-technology-bakeoff.md) |
| 編集・検証・公開の手順 | [CONTRIBUTING](CONTRIBUTING.md)・[品質検証](docs/QUALITY_CHECKS.md) |

## プロジェクトの目的と調査境界

Private Matchは、当事者が秘密データや秘密条件を保持したまま、合意した最小限の
判定結果だけを受け取り、追加の相互同意が成立した場合に限って情報を段階的に
開示する仕組みを検討するプロジェクトです。

このリポジトリは、技術的に可能なことと、事業として採用すべきことを分離する
ための判断材料を提供します。製品の優先順位や顧客への提供条件は決定しません。

主な調査領域は次のとおりです。

- 利益相反・関係者重複のpreflightと、提携・M&A前の顧客基盤重複判定
- Data Clean Room、PETプラットフォーム、privacy-first matching製品との違い
- 契約下でのデータ共有や既存業務など、非PETの代替手段
- PSI／OPRF・VOPRF、MPC、TEE、ZKP等の信頼モデル・実装条件・残余漏えい
- 少数intersection、反復照会、正規化、入力真正性・完全性の問題

[初期市場マップ](landscape/2026-07-initial-market-map.md)は2026年7月時点の資料です。
各レコードの調査日・最終確認日・次回レビュー日を確認し、過去の観測を現在の
製品能力やローカル再現結果として扱わないでください。

## ローカル検証

レビュー済みCI環境はUbuntu 24.04 / x86_64 / CPython **3.12.13**です。
リポジトリルートで、対応するPythonを使用します。

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements-build.txt
python -m pip install --require-hashes --no-build-isolation -r requirements-dev.txt
python -m unittest discover -s tests -p 'test_*.py'
python scripts/generate_competitor_index.py --root . --check
python scripts/validate_research.py \
  --root . --report-dir artifacts --stale-policy warn
reuse lint
```

依存関係のインストールにはパッケージ取得が必要です。上記の検証では外部URLの
可用性観測やPET候補の実行を行いません。期限超過の調査レコードは警告として
表示されますが、検証成功によって情報が最新であると認定されるわけではありません。

レコードを変更した場合の再生成、hash lock更新、信頼された環境での外部URL観測は
[品質検証手順](docs/QUALITY_CHECKS.md)を参照してください。

## ディレクトリ構成

| パス | 内容 |
| --- | --- |
| `records/` | 競合、代替手段、技術の構造化レコード |
| `landscape/` | 市場マップ、競合インデックス、代替手段の分析 |
| `technologies/` | 技術・信頼モデルの比較 |
| `benchmarks/` | 実験計画、合成入力生成、結果Schema |
| `decisions/` | 公開可能な技術実験の判断記録 |
| `schema/`・`scripts/`・`tests/` | レコードSchema、品質検証、回帰テスト |
| `templates/` | 調査レコードと仮説のテンプレート |

## 調査・公開の原則

1. 事実、推論、仮説、意思決定、分からないことを分けて記録する。
2. 一次情報を優先し、変更され得る情報には確認日を付ける。
3. ベンダーの主張、外部ベンチマーク、自ら再現した結果を区別する。
4. 「競合が見つからない」を「競合が存在しない」と扱わない。
5. ツールやテストの成功を、市場需要や技術全体の安全性の証拠にしない。
6. 公開前にIP、セキュリティ、プライバシー、主張表現、ライセンスを確認する。

顧客名、インタビュー原文、価格・営業戦略、非公開実装・インフラ、未公開発明、
未修正の脆弱性情報は含めません。公開・非公開の判断と変更手順は
[GOVERNANCE](GOVERNANCE.md)、今後の作業は[ROADMAP](ROADMAP.md)を参照してください。

## 関連リポジトリ

| Repository | 公開範囲 | 役割 |
| --- | --- | --- |
| [private-match-research](https://github.com/itdojp/private-match-research) | Public | 市場・技術・ユースケース調査（本リポジトリ） |
| [private-match-protocol](https://github.com/itdojp/private-match-protocol) | Public | 公開プロトコル、Schema、適合試験 |
| [private-match-assurance](https://github.com/itdojp/private-match-assurance) | Public | 公開保証の契約、検証ツール、主張と限界 |
| `private-match-product` | Private | 商用実装と非公開Evidenceの生成 |
| `private-match-strategy` | Private | 事業・顧客・IP・法務・公開判断 |

[ae-framework](https://github.com/itdojp/ae-framework)はEvidenceと判断を整理する
assurance control planeです。その利用自体が製品の安全性や需要の証明にはなりません。

## License

Narrative research material and structured research records use **CC-BY-4.0**.
Executable/reference artifacts, schemas, validators, tests, workflows, and build
inputs use **Apache-2.0**. See [LICENSE.md](LICENSE.md),
[REUSE.toml](REUSE.toml),
and [ADR-0001](docs/decisions/ADR-0001-PUBLIC-LICENSING.md) for file-specific
allocation and the patent/publication boundary.
