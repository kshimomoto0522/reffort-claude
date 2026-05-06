---
name: BayChat と Campers のユーザー数を混同しない
description: BayChat は約500セラー（SaaS有料顧客）・Campers は約70名（スクール生徒）・全く別の母数として扱う
type: feedback
---

# BayChat と Campers のユーザー数を混同しない

| サービス | ユーザー数 | 性質 |
|---|---|---|
| **BayChat** | **約 500 セラー（2026-02 で 527 active）** | 有料 SaaS 顧客（STANDARD 322 / PREMIUM 180 / PREMIUM+ 12 / 無料 25） |
| **Campers** | **約 70 名** | eBay 輸出スクールの受講生・コミュニティメンバー |

**Why:** Claude が両者を取り違えると、コスト試算（外部 SaaS 連携・配信コスト・サポート工数等）の規模感が大きく狂う。500 と 70 では桁レベルで違う。2026-05-06 に AfterShip コスト試算で実際に取り違え発生・社長指摘。

**How to apply:**
- BayChat の話題でユーザー数を言うときは `services/baychat/ai/user-growth.md` を確認する
- Campers は `education/campers/` 配下を参照
- 「○○セラー」と言うときは BayChat 側、「○○名のメンバー」「生徒」は Campers 側、を意識する
- 外部 SaaS 連携やコスト試算で「BayChat 全ユーザー展開」と書くときは必ず約500を前提にする
