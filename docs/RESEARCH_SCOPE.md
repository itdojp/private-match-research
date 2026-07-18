# Research Scope v0.1

最終更新: 2026-07-18

## 1. 中心課題

Private Matchは「ゼロ知識証明を使う製品」を探索するのではなく、次の課題を検証する。

> 当事者が秘密データや秘密条件を保持したまま、意思決定に必要な最小結果だけを相互に確認することへ、誰が、どの状況で、どれだけの価値を認めるか。

## 2. 調査ワークストリーム

### W1: Market Landscape

- 既存Data Clean Room、PETプラットフォーム、秘密計算サービス
- Private matching、identity matching、conflict checking
- 個別開発、NDA、監査法人・コンサルティング等の代替手段
- 導入期間、buyer、価格、前提環境

### W2: Use-case Discovery

初期候補:

1. 利益相反・関係者重複Preflight
2. 提携・M&A前のCustomer Overlap
3. 非公開採用マッチング
4. Fraud / AML consortium
5. Consumer private matching

各候補についてbuyer、user、trigger、current workaround、損失、必要な結果、許容誤差、導入障壁を確認する。

### W3: Technology Landscape

- PSI / PSI Cardinality / Private Join and Compute
- OPRF / VOPRF
- 2PC / MPC
- ZKP / zkVM / credential proof
- TEE / confidential computing
- FHE
- Differential Privacy
- Verifiable Credentials

技術名ではなく、脅威モデル、漏えい、運用、性能、保守性で比較する。

### W4: Privacy and Abuse

- low-entropy identifier attacks
- small intersection leakage
- repeated adaptive queries
- input omission / poisoning
- identity resolution and normalization errors
- result asymmetry
- replay / session confusion
- metadata leakage
- collusion

### W5: Assurance and Public Claims

- 公開仕様と非公開実装の検証可能性
- conformance suite
- test vectors
- evidence manifest
- external review
- ae-frameworkによる証拠集約
- 公開してよい主張と禁止表現

## 3. 初期意思決定質問

### Market

- Data Clean Room導入前の「一回限り・最小判定」に独立した予算があるか。
- buyerは法務、営業、M&A、監査、情報システムの誰か。
- 現在はどの段階でNDA、データ共有、外部委託が必要になるか。
- YES/NOまたは件数bandだけで次の意思決定ができるか。
- 導入準備に許容される時間は何日／何時間か。

### Protocol

- どの結果を公開してよいか。
- 正確なcountは本当に必要か。
- minimum set sizeとminimum intersectionは何件か。
- 一つのinput commitmentに何回照会を許可するか。
- 入力が真正・完全であることを誰が保証するか。

### Technology

- semi-honest securityで開始可能か、malicious securityが必須か。
- participant-controlled environmentの範囲はどこまでか。
- TEEへの信頼はbuyerに受け入れられるか。
- OSSライブラリの保守・監査状態は本番利用に足りるか。
- 大規模balanced setとunbalanced setを同一方式で扱うべきか。

### Assurance

- 公開ソースなしで、どの程度のblack-box conformanceを提供できるか。
- 公開client/verifierはどの信頼ギャップを縮小するか。
- 外部暗号レビューの対象をどこまで限定できるか。
- releaseごとに公開すべき証拠は何か。

## 4. 初期Go/No-Go基準

サービスpilotへ進むには、最低限次を満たす。

- 対象課題について顧客証拠 `E2` 以上
- 技術方式について実データ相当PoC `E3` 以上
- raw identifier non-egressを実測で確認
- leakage contractを定義し、反復照会を含む試験を実施
- 本番経路にmock／silent fallbackが存在しない
- 公開主張、仮定、未検証事項を分離可能
- 外部レビュー対象と予算を定義

## 5. 非目標

初期段階では次を目標にしない。

- 汎用Data Clean Roomの再実装
- 任意SQL・任意分析基盤
- 「ZKPを使用していること」自体による差別化
- あらゆるユースケースを一つの暗号方式で処理すること
- 完全な匿名性や絶対安全の主張
- 顧客需要を技術デモだけで判断すること
