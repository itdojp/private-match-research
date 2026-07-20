# Private Match Research

Private Matchに関する市場、競合、ユースケース、プライバシー強化技術（PETs）を、一次情報と再現可能な方法に基づいて調査する公開リポジトリです。

本リポジトリは株式会社アイティードゥが管理します。

## 目的

Private Matchは、当事者が秘密データや秘密条件を保持したまま、合意した最小限の判定結果だけを受け取り、追加の相互同意が成立した場合に限って情報を段階的に開示する仕組みを検討するプロジェクトです。

このリポジトリでは、次を明らかにします。

- どの業務課題に経済的価値があるか
- 既存製品・代替手段とどこが重なるか
- PSI、OPRF/VOPRF、MPC、ZKP、TEE、FHE、VC等をどの条件で使い分けるか
- 技術的に可能なことと、事業として採用すべきことをどう分離するか
- 公開可能な主張を、どの証拠と不確実性に基づいて行うか

## このリポジトリに含むもの

- 公式資料・標準・論文に基づく競合分析
- PET技術と信頼モデルの比較
- 一般化・匿名化したユースケース分析
- 再現可能な公開ベンチマーク
- 公開可能なArchitecture Decision Record（ADR）
- 調査方法、証拠レベル、主張管理ルール

## 含まないもの

- 顧客名、商談、顧客インタビュー原文
- 価格戦略、営業パイプライン、受注確度
- サービス本体のソースコードとインフラ構成
- 未出願の発明候補
- 修正前の脆弱性や攻撃可能な運用情報

これらは非公開の `itdojp/private-match-strategy` または `itdojp/private-match-product` で管理します。

## 関連リポジトリ

| Repository | Visibility | Responsibility |
|---|---|---|
| `itdojp/private-match-protocol` | Public | プロトコル、脅威モデル、参照実装、適合試験 |
| `itdojp/private-match-research` | Public | 市場、競合、技術、ユースケース調査 |
| `itdojp/private-match-assurance` | Public | 公開可能な保証主張と検証証跡 |
| `itdojp/private-match-product` | Private | 商用サービス本体 |
| `itdojp/private-match-strategy` | Private | 製品戦略、顧客、価格、知財、公開判断 |
| `itdojp/ae-framework` | Public | Assurance Control Plane |

## 調査原則

1. 事実、推論、仮説、意思決定を分けて記録する。
2. 変更され得る情報には調査日と最終確認日を付ける。
3. 原則として一次情報を優先する。
4. 「競合が見つからない」を「競合が存在しない」と扱わない。
5. ae-frameworkのテスト成功を市場需要の証拠として扱わない。
6. 暗号方式の名称だけで安全性や優位性を主張しない。
7. 公開前に知財、セキュリティ、プライバシー、主張表現を確認する。

詳細は [`docs/RESEARCH_METHOD.md`](docs/RESEARCH_METHOD.md) を参照してください。

## 公開リサーチ成果物

- [構造化競合インデックス](landscape/competitor-index.md) — 競合・隣接製品・代替手段・OSS構成要素の分類、確認日、次回レビュー日
- [初期市場マップ](landscape/2026-07-initial-market-map.md) — 2026年7月時点の予備的な市場解釈
- [品質検証手順](docs/QUALITY_CHECKS.md) — スキーマ、日付、公開ゲート、リンク、主張表現の検証方法

## 現在の重点領域

- 利益相反・関係者重複のPrivate Preflight
- 提携・M&A前の顧客基盤重複判定
- 既存Data Clean Room／PETプラットフォームとの差分
- 非PET代替手段を含む構造化競合レコードの定期レビュー
- 少数intersection、反復照会、正規化、入力真正性による漏えい・誤判定
- PSI／OPRF系、MPC、TEEの比較

## 状態

`pre-alpha / research baseline`

現時点の文書は調査基盤であり、製品の安全性、法令適合、暗号学的安全性、顧客需要を証明するものではありません。

## License

Narrative research material and structured research records use CC-BY-4.0.
Executable/reference artifacts, schemas, validators, tests, workflows, and build
inputs use Apache-2.0. See [`LICENSE.md`](LICENSE.md), `REUSE.toml`, and
[`ADR-0001`](docs/decisions/ADR-0001-PUBLIC-LICENSING.md) for the file-specific
allocation and patent/publication boundary.
