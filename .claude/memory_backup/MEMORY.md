# Memory Index

## ユーザー
- [社長プロフィール](user_profile.md) — Reffort代表のスキル・目標・Claudeへの期待
- [思考パターン観察ノート](user_patterns.md) — 強み・盲点・コミュニケーション傾向（ありのまま記録）

## 意思決定
- [意思決定ログ](decisions_log.md) — 主要な経営判断と根拠の記録（Campers引継ぎ・Cowatech継続・BayPack非公開理由・フォルダ再編成・竹案リファクタ等）

## フィードバック（最重要・姿勢）
- [口調と分析の徹底度](feedback_tone_and_depth.md) — 敬語厳守・指摘される前に徹底的に考え抜く・最初から徹底版
- [経営パートナーとしての在り方](feedback_proactive_partner.md) — 言いなり禁止・指示の目的を理解し先回り提案
- [常にベストから逆算する思考ルール](feedback_best_first_thinking.md) — ハードル/コストで切り捨てず松竹梅でベストを推奨
- [宣言は必ず実装とセット](feedback_declaration_to_implementation.md) — 時間トリガー宣言→scheduled-task/hook/スクリプトに落とすまで完了しない
- [BayChat AI Reply 進行時のスタンス](feedback_baychat_ai_reply_stance.md) — 設計図理解前提・Cowatech前に自力解決・5原則厳守

## フィードバック（コミュニケーション・報告）
- [コミュニケーション・運用スタイル](feedback_communication.md) — Chatwork確認運用・報告先の好み・作業可視性
- [Chatwork運用ルール（統合）](feedback_chatwork.md) — AI宛て返信のみ反応＋社長個人DM(426170119)は[info][title]形式箱型カード必須
- [Slack対応ルール](feedback_slack_rules.md) — スレッド構造・送信前GO厳守・1時間チェック後判定フロー
- [読めない時は諦めず読む手段を探す](feedback_fetch_fallback.md) — WebFetchで取れなくてもChromeツールで読む

## フィードバック（運用・セキュリティ）
- [セキュリティルール（統合）](feedback_security.md) — APIトークン.env管理・.env出力禁止・settings.json deny判断基準・トークン管理
- [.envファイルの作成・入力方法](feedback_env_file_handling.md) — Claudeがファイル作成→社長が直接入力（チャット入力禁止）
- [スケジュールタスク運用ルール（統合）](feedback_scheduled_tasks.md) — 実行厳守・プロンプト同期・Run now承認焼き込み・チェックポイント先行更新
- [スケジュールタスク アクティベート必須](feedback_task_activation.md) — 新規タスク必ずアクティベートテスト→承認→本番プロンプト更新
- [Claude Code 運用ルール（統合）](feedback_claude_code_operation.md) — Progressive Disclosure＋4点セット（archive・biweekly-maintenance・index.md・/隔週メンテナンス）＋effort_booster厳選
- [管理方法統一](feedback_management_unification.md) — 3層管理原則（ソース/バックアップ/スマホ参照）

## フィードバック（ツール・作業）
- [ASICSブロック誤判定ミス](feedback_asics_block.md) — Bot検出をIPブロックと誤認する繰り返しミス・無限監視ループ禁止
- [ファイル作成後は即座に開く](feedback_file_delivery.md) — startコマンドで開くかエクスプローラーで見える状態にする
- [モデル判断は社長・Effortは自動調整](feedback_model_effort_policy.md) — モデル切替は提案しない・Opus基本
- [事業実践のコンテンツ記録ルール](feedback_content_recording.md) — AI運用の発見・テスト・結果をSNS/Note/コンサル向け記録
- [商品言及時は必ずSKU付き](feedback_sku_required.md) — 必ず【SKU】タイトル形式
- [本番HP変更は必ずOK確認後に公開](feedback_hp_publish_rule.md) — プレビュー→社長OK→公開
- [BayChat UI設計原則](feedback_baychat_ui_design.md) — 紫ベース配色・信号機色禁止・英日併記・シンプルイズザベスト

## フィードバック（サーバー・デプロイ）
- [サーバーデプロイの教訓](feedback_server_deploy.md) — VPS失敗の教訓・PaaS優先・社長に手作業させない
- [ダイレクト販売テスト・デプロイ運用](feedback_local_test_workflow.md) — ローカルテスト→社長OK→本番push・営業時間中push禁止

## プロジェクト
- [コンサル事業ビジョン](project_consulting.md) — 将来のコンサルコミュニティ事業の方針・記録場所
- [eBay広告最適化プロジェクト](project_ad_optimization.md) — PLG/PLP/Offsite最適化・Marketing API活用・コンテンツ化
- [高橋Claude Code導入](project_takahashi_claude.md) — 高橋さんへのClaude Code環境共有・段階的AI活用計画
- [ダイレクト販売ツール](project_direct_sales.md) — Render公開済・技術構成・課題
- [Campersウェビナー4/26](project_campers_webinar.md) — eBay×AI運営ウェビナー・AIコース案内・草案作成済み
- [X情報ダイジェスト](project_x_digest.md) — X投稿自動収集→Claude要約→Chatwork個人DM配信（毎日9:40）

## 参照なし（archive/・通常ロードしない）
- `archive/README.md` — archive/ 配下のルール
- `archive/project_asics_tool.md` — ASICSツール memory（commerce/ebay/tools/CLAUDE.md＋development-history.md で情報保全済み）
- `archive/project_baychat_ai_reply.md` — BayChat AI Reply memory（services/baychat/ai/ai-reply-status.md で情報保全済み）
- `archive/project_shiire_gas_tool.md` — 仕入管理表GAS memory（gas-shiire-tool-spec.md で情報保全済み）
- `archive/project_ebay_report.md` — 週次レポートv3 memory（weekly-report-spec.md＋本番稼働で完了）
- `archive/feedback_remotion_video.md` — Remotion動画制作失敗教訓（過去参照用）

## 外部ファイル（memoryから移動）
- `.claude/rules/reference_nodejs_install.md` — Node.jsインストール手順（旧 memory/reference_nodejs_install.md を2026-04-24に移動）
