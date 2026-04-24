---
name: X情報ダイジェストプロジェクト
description: X（Twitter）フォロー中投稿を毎日自動収集→Claude要約→Chatwork個人DM配信の仕組み
type: project
---

X（Twitter）のフォロー中アカウントの投稿を毎日自動収集し、Claudeが要約してChatwork個人DM（下元 敬介 room_id: 426170119）に毎朝9:40に配信する仕組みを構築済み。

**Why:** SNSを手動で追うのは非効率。AIに情報収集・要約を任せ、社長は取捨選択だけに集中する。

**スクリプト:** `management/x-digest/x_digest.py`
**設定ファイル:** `management/x-digest/.env`
**X APIアカウント:** 情報収集専用の新規Xアカウント（BayPackアカウントとは別）
**X API料金:** 従量課金（Pay-Per-Use）・$5チャージ済み
**配信先:** Chatwork 下元 敬介 個人DM（room_id: 426170119）
**配信時刻:** 毎日9:40

**How to apply:** スクリプト修正・フォロー追加・配信内容の調整依頼があれば `management/x-digest/x_digest.py` と `.env` を参照する。
