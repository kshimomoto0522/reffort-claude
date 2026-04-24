# Memory Index

## ユーザー
- [社長プロフィール](user_profile.md) — Reffort代表のスキル・目標・Claudeへの期待
- [思考パターン観察ノート](user_patterns.md) — 強み・盲点・コミュニケーション傾向（ありのまま記録）

## フィードバック
- [口調と分析の徹底度（最重要）](feedback_tone_and_depth.md) — 敬語厳守（タメ口禁止）・指摘される前に徹底的に考え抜く・最初から徹底版を出す
- [経営パートナーとしての在り方（最重要）](feedback_proactive_partner.md) — 言いなり禁止。指示の目的を理解し先回り提案。経営を同じ目線で考える存在であること
- [宣言は必ず実装とセット](feedback_declaration_to_implementation.md) — 「〜します」「1時間ごとに」等の時間トリガー宣言は、その場でscheduled-task/hook/スクリプトに落とすまで完了しない
- [常にベストから逆算する思考ルール](feedback_best_first_thinking.md) — 全事業共通。ハードル・コストで切り捨てず、ゴールから逆算したベストを松竹梅で提示する根本ルール
- [コミュニケーション・運用スタイル](feedback_communication.md) — Chatwork確認の運用・報告先の好み・作業可視性
- [Chatwork返信ルール](feedback_chatwork_rules.md) — AI宛てのメンション・返信のみ反応。それ以外はスルー
- [Slack対応ルール](feedback_slack_rules.md) — #baychat-ai導入のスレッド構造・送信前GO厳守・1時間チェック後の判定フロー・承認依頼はChatwork社長DMへ
- [Chatwork社長個人DM通知フォーマット](feedback_chatwork_dm_format.md) — 個人DM(426170119)への通知は必ず[info][title]...[/title]...[/info]の箱型カード形式で送る
- [セキュリティルール](feedback_security.md) — APIトークンは.env管理必須。コード直書き禁止
- [セキュリティ設定の考え方](feedback_security_settings.md) — deny設定・トークン管理・.envブロックの判断基準
- [ASICSブロック誤判定ミス](feedback_asics_block.md) — ヘッドレスBot検出をIPブロックと誤認する繰り返しミス。無限監視ループ禁止
- [スケジュールタスク実行の厳守ルール](feedback_scheduled_task_execution.md) — できない処理をスキップして続行は絶対禁止。イレギュラーは即中断・報告。口頭指示はプロンプトに転記必須。
- [スケジュールタスク作成時のアクティベート必須](feedback_task_activation.md) — 新規タスクは必ずアクティベートテスト→承認→本番プロンプト更新の3ステップ。テンプレートはeducation/campers/member-removal-template.md
- [タスク単位の承認キャッシュ](feedback_scheduled_task_approval_cache.md) — settings.local.jsonとは別にタスク単位の承認を持つ。新規/改修時は「今すぐ実行」で焼き込み必須
- [チェックポイント先行更新の原則](feedback_checkpoint_first_design.md) — ts/cursor的な定期タスクは処理より先にチェックポイントを保存。無限停止ループの防止

## 意思決定
- [意思決定ログ](decisions_log.md) — 主要な経営判断と根拠の記録（Campers引継ぎ・Cowatech継続・BayPack非公開理由等）

## プロジェクト
- [コンサル事業ビジョン](project_consulting.md) — 将来のコンサルコミュニティ事業の方針・記録場所
- [eBay週次レポートv3の現状](project_ebay_report.md) — スクリプト完成状態・APIキャッシュ・次のタスク
- [eBay広告最適化プロジェクト](project_ad_optimization.md) — PLG/PLP/Offsite最適化・Marketing API活用・コンテンツ化
- [ASICSツール再作成プロジェクト](project_asics_tool.md) — Scrapling版への再作成・調査結果・ソースコード待ち中
- [BayChat AI Reply プロジェクト](project_baychat_ai_reply.md) — モデル選定（Gemini 2.5 Flash採用方針）・プロンプトv2.1・テスト状況・Cowatech依頼状況
- [高橋Claude Code導入](project_takahashi_claude.md) — 高橋さんへのClaude Code環境共有・段階的AI活用計画

## フィードバック（追加）
- [事業実践のコンテンツ記録ルール](feedback_content_recording.md) — AI運用の発見・テスト・結果をSNS/Note/コンサル向けに記録するルール
- [商品言及時は必ずSKU付き](feedback_sku_required.md) — タイトルだけでは特定不可。必ず【SKU】タイトル形式で
- [.envファイルの作成・入力方法](feedback_env_file_handling.md) — 機密情報はClaudeがファイル作成→社長が直接入力。チャット上での入力案内禁止
- [スケジュールタスクのプロンプト同期](feedback_scheduled_task_sync.md) — スクリプト変更時にタスクプロンプトも必ず更新。聞かれる前にやる
- [本番HP変更は必ずOK確認後に公開](feedback_hp_publish_rule.md) — プレビューを見せてOKをもらうまで公開ボタンは絶対に押さない
- [CLAUDE.md構造最適化ルール](feedback_claude_md_structure.md) — 100行以下のコアルールのみ。参照情報は.claude/rules/に分離徹底
- [BayChat UI設計原則](feedback_baychat_ui_design.md) — 紫ベース配色・信号機色(緑/赤/黄)禁止・英日併記必須・シンプルイズザベスト
- [BayChat AI Reply 進行時のスタンス（最重要）](feedback_baychat_ai_reply_stance.md) — 設計図は理解済み前提・Cowatech前に自力解決・論点リスト機械消化禁止・議論結論を草案に正確反映

- [X情報ダイジェスト](project_x_digest.md) — X投稿自動収集→Claude要約→Chatwork個人DM配信（毎日9:40）

## プロジェクト（追加）
- [ダイレクト販売ツール](project_direct_sales.md) — Render公開済(https://reffort-direct-sales.onrender.com)・技術構成・課題
- [Campersウェビナー4/26](project_campers_webinar.md) — eBay×AI運営ウェビナー・AIコース案内・草案作成済み
- [仕入管理表GASツール](project_shiire_gas_tool.md) — eBay API→スプレッドシート自動反映。Z除去重複バグ未修正

## フィードバック（サーバー・デプロイ）
- [サーバーデプロイの教訓](feedback_server_deploy.md) — VPS失敗の教訓。事前調査・PaaS優先・社長に手作業させない
- [ダイレクト販売テスト・デプロイ運用](feedback_local_test_workflow.md) — ローカルテスト→社長OK→本番push。営業時間中push禁止
- [ファイル作成後は即座に開く](feedback_file_delivery.md) — 「フォルダに作りました」禁止。startコマンドで直接開くかエクスプローラーで見える状態にする
- [読めない時は諦めず読む手段を探す](feedback_fetch_fallback.md) — WebFetchで取れなくてもChromeツールで読む。代替記事は「代わり」ではなく「上乗せ」で使う
- [モデル判断は社長・Effortは自動調整](feedback_model_effort_policy.md) — モデル切替は提案しない。基本Opus。Effortはhighデフォ＋キーワードで自動Maxブースト
- [Remotion動画制作の失敗教訓](feedback_remotion_video.md) — 実画面録画×Remotionは砂嵐問題で使えない。機能紹介動画はCap.so推奨

## フィードバック（Claude Code運用）
- [Claude Code運用の持続可能性ルール](feedback_claude_code_persistent_maintenance.md) — 4点セット（archive/・biweekly-maintenance・index.md・/隔週メンテナンス）＋Progressive Disclosure＋effort_booster厳選＋コンテンツ素材化

## 参照先
- [Node.jsインストール手順](reference_nodejs_install.md) — バージョン選択FAQ（LTS版を選ぶ）。スタッフ・生徒向け
