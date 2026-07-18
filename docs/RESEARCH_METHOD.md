# Research Method v0.1

最終更新: 2026-07-18

## 1. 目的

競合調査、技術調査、顧客課題、製品仮説を混同せず、根拠、不確実性、更新時点を明示して意思決定する。

## 2. 記述区分

各重要記述は、可能な限り次の区分を付ける。

| Code | 区分 | 意味 |
|---|---|---|
| `F` | Fact | 一次情報で確認できる事実 |
| `I` | Inference | 複数事実から導いた分析・解釈 |
| `H` | Hypothesis | 今後検証すべき仮説 |
| `D` | Decision | プロジェクトとして採用した判断 |
| `U` | Unknown | 調査未完了・情報非公開・判断不能 |

推論を事実として、仮説を製品要件として記載しない。

## 3. 証拠レベル

市場・顧客仮説には次の証拠レベルを用いる。

| Level | 内容 |
|---|---|
| `E0` | 内部仮説。外部根拠なし |
| `E1` | 公式資料、標準、論文、公開製品情報による裏付け |
| `E2` | 対象顧客へのインタビューで課題を確認 |
| `E3` | 実データに近い技術PoCで成立を確認 |
| `E4` | 顧客が試用、共同PoC、契約、支払いのいずれかを実施 |
| `E5` | 複数顧客・複数案件で再現し、運用指標を取得 |

市場適合性について、ae-frameworkのテスト成功、形式検証成功、暗号実装成功を `E2` 以上の証拠として扱わない。

## 4. 情報源の優先順位

1. 標準化団体、公的機関、法令・規制当局
2. 査読論文、著者版論文、正式な技術報告
3. 製品の公式ドキュメント、セキュリティ文書、監査報告
4. 公式GitHubリポジトリとRelease
5. 顧客事例、導入事例
6. 公式プレスリリース
7. マーケティングページ
8. 信頼できる二次資料
9. SNS、掲示板、未確認の第三者説明

技術の安全性評価はマーケティングページだけで確定しない。

## 5. 時点管理

変更され得る情報には次を記録する。

```yaml
observed_at: 2026-07-18
last_verified_at: 2026-07-18
source_status: current | superseded | unavailable
next_review_at: 2026-10-18
```

製品機能、価格、企業状態、ライセンス、保守状態、標準のstatusは定期的に再確認する。

## 6. 競合分類

| Class | 定義 |
|---|---|
| `direct` | 同じbuyer、同じtrigger、同じ主要成果を狙う製品 |
| `adjacent` | 類似の課題をより広い／異なる手段で解く製品 |
| `substitute` | 暗号技術を使わず同じ意思決定を可能にする手段 |
| `building-block` | 当製品または競合が利用し得る技術・OSS・標準 |
| `potential` | 公開情報不足で分類未確定 |

Data Clean RoomやPET基盤を自動的にdirect competitorと扱わない。buyer、導入trigger、導入期間、出力、価格モデルを比較して分類する。

## 7. 競合レコード必須項目

- 調査日、最終確認日
- 企業・製品・URL
- 分類
- buyer / user / trigger
- 解決するjob
- 入力と出力
- 使用技術または公開された信頼モデル
- attacker / trust assumptions（公開されている範囲）
- デプロイ形態
- データ移動・保持
- 最小開示制御
- クエリ・反復照会制御
- 監査・保証の公開度
- 価格情報
- 導入期間・前提環境
- 強み
- 制約・未確認事項
- Private Match仮説への影響
- 一次ソース
- confidence: `high | medium | low`

## 8. 技術評価必須項目

- security model: semi-honest / malicious / TEE trust / other
- party model: 2-party / multi-party / client-server
- supported result: membership / intersection / cardinality / sum / general function
- data profile: balanced / unbalanced / low entropy identifiers
- cryptographic assumptions
- metadata leakage
- repeated-query considerations
- input authenticity and omission resistance
- computation and communication cost
- implementation maturity
- external audit / formal analysis
- license and patent considerations
- language/runtime/deployment compatibility
- maintenance and release activity

## 9. 公開分類

### Public

- 一次情報に基づく事実
- 一般化した市場分類
- 公開済み技術の比較
- 再現可能なベンチマーク
- 匿名化された知見
- 公開済みの脅威モデルと保証証跡

### Embargoed

- 公開予定だが知財・セキュリティレビュー待ち
- 未発表ベンチマーク
- 新規プロトコル案
- 修正中の脆弱性

### Private

- 顧客名、インタビュー原文、営業パイプライン
- 価格戦略、受注確度、競合攻略
- 未出願の差別化要素
- サービス実装、インフラ、運用シークレット

## 10. 公開ゲート

公開候補は最低限、次を満たす。

- `source_check`: 事実の一次ソース確認
- `freshness_check`: 時点と更新可能性の確認
- `ip_review`: 特許、著作権、ライセンス確認
- `security_review`: 攻撃手順・内部情報・未修正脆弱性の除去
- `privacy_review`: 個人・顧客・組織の特定可能性確認
- `claims_review`: 「証明済み」「安全」「世界初」等の過大表現除去
- `reproducibility_review`: 再現手順、環境、範囲、失敗条件の明記

## 11. 更新・訂正

公開情報に誤りが判明した場合は、履歴を消さずに訂正する。

- 何が誤っていたか
- いつ訂正したか
- 判断にどの影響があったか
- どの証拠に置き換えたか

を記録する。
