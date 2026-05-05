# eBayツール開発 — 解決済み履歴・経緯

> 親: `commerce/ebay/tools/CLAUDE.md` から「必要時ロード」として参照される詳細ファイル。
> 過去に解決した技術課題・移行経緯・失敗から得た教訓をまとめる。開発者向けの学習資料。

---

## ASICS v9 並列ワーカー実装（進行中・2026-05-05夜）

### 背景
v8 が1周40時間以上かかり遅すぎる課題。240秒待機を縮められない（Akamai Bot Manager に弾かれる）。

### 解決アプローチ
**ローカル + AdsPower(Onitsuka) 2並列構成**で半分の時間に短縮:
- Worker1: 既存ローカルFirefox・240秒待機（実績温存）
- Worker2: AdsPower経由Chrome・120秒待機・DECODO日本住宅IP（別IP・別指紋）
- 比率分割で「パイ（総件数）が変わっても両ワーカーが同時刻に終わる」

### PoC結果（2026-05-05 夜）
- AdsPower Local API（v6+ Bearer認証）疎通成功
- Selenium debuggerAddress 経由で Chrome 接続成功
- ASICS 5件連続取得（120秒待機）→ Bot検出ゼロ・1件のみDECODO瞬断（リトライ対応）
- 605件想定で **40時間 → 15.9時間（2.5倍速）**

### 技術的な落とし穴
1. **AdsPower Local API は Bearer 認証必須**（v6+）。`Authorization: Bearer <api_key>` ヘッダ。
2. **DECODO 住宅プロキシは性質上たまに切断される**（`ERR_TUNNEL_CONNECTION_FAILED`）。短時間リトライで救済可能。
3. **AdsPower Chrome の close(); ではブラウザを閉じない**。`driver.quit()` でセッション切断のみ。
4. **比率分割の数式**: n1:n2 = (1/t1):(1/t2) （各ワーカーの処理能力に比例）
5. **WORKER_CONFIG の avg_fetch_seconds は実測値**で運用しながら更新する想定。

### 次セッション課題
1. 単独モード互換テスト → worker2単体テスト → 2並列テスト
2. process_one_item の driver.get → safe_get 化（DECODO瞬断対策）
3. PyInstaller spec 更新 → exe 再ビルド
4. .env 移行（AdsPower API Key・user_id）

詳細: `handoff_20260505_evening_parallel_v9.md`

---

## 日本語パス問題（解決済み・2026年3月）

### 背景
- タスクスケジューラはcmd.exe経由でbatファイルを実行する
- ツールフォルダ名に日本語（アシックス）が含まれている
- cmd.exeのタスクスケジューラ環境では日本語パスが文字化けする

### 解決策
- bat → デスクトップのps1（日本語なしパス）→ PowerShell内で日本語パスを処理
- ps1ファイルはUTF-8 BOM形式で保存する必要がある（PowerShellがBOMを認識して正しく読む）

### 配置
| ファイル | 場所 | 役割 |
|---------|------|------|
| `run_asics.ps1` | `C:\Users\KEISUKE SHIMOMOTO\Desktop\` | ASICSツール起動（UTF-8 BOM） |
| `run_adidas.ps1` | `C:\Users\KEISUKE SHIMOMOTO\Desktop\` | adidasツール起動（UTF-8 BOM） |

**これらps1ファイルは絶対に削除しないこと。**

---

## Scrapling → Selenium 移行の経緯（2026年3月20-21日・ASICS）

1. Scrapling版で稼働開始 → 最初の数件後に403 Forbidden連発
2. 遅延を5-15秒→30-60秒に変更 → 依然として403
3. ブラウザでは同じURLが正常に開ける → IPブロックではなくBot検出
4. adidas用に作ったFirefox/Selenium方式をASICSにも適用 → 403解消
5. テスト: 以前403だった3URLすべてで200 OK確認

---

## 並列化失敗の教訓（2026年3月26日）

1. 240秒・1台で安定動作（22件成功・Access Denied 0件）
2. 高速化のため120秒・3台並列を試行 → Akamaiにブロックされた
3. ヘッドレスFirefoxでの確認を繰り返し、状況を悪化させた

### 教訓
- 安定動作を急激に変更しない。変更は段階的に（1パラメータずつ）
- Access Denied = IPブロックとは限らない。ブラウザで開ければBot検出が原因

---

## v2.3修正（2026年3月27日）— Access Denied過剰防御の是正

### 問題
v2.2はAccess Deniedのたびに Firefox再起動+240秒追加待機+累計10件で強制終了 → 5.5時間で11件しか処理できない

### 旧ツールとの比較
旧ツール（exe）は同じFirefox+240秒間隔で2日で600件全件処理できていた

### v2.3の変更点
1. Access DeniedでFirefox再起動しない（セッション維持で30-60秒待機リトライ）
2. 累計失敗10件の強制終了を撤廃（時間制限まで続行）
3. 連続失敗クールダウンを10分→3分に短縮
4. configのdelay値をそのまま使用（ハードコード廃止）

### v2.3実行結果
84件成功 / 102件エラー（成功率45%）/ 14時間稼働
→ v2.2比で処理件数9倍、成功件数7.6倍に改善。ただしAccess Denied率は依然55%

---

*最終退避: 2026-04-24（竹案T4実施時に`CLAUDE.md`から退避）*

---

## ASICSツール v8 完成への道のり（2026-05-01〜05）

### v3 → v4 のバグ（safe_write_check オフセット）
新シート構造（行1=status, 行2=header, 行3+=data）への移行で、`safe_write_check` の `len - 1`（旧構造）を `len - 2` に修正し忘れ → 全書き込みスキップ。約4時間ロス。  
**教訓**: 構造変更時は安全機構（バリデーション系）の全関数も新構造で動くか必ず確認。`feedback_test_before_handoff.md` 強化。

### v3 デプロイ時の charset_normalizer 抜け落ち
PyInstaller 4.6 が requests の隠れ依存を見落とし → exe 起動即クラッシュ。  
**対策**: spec で `collect_all('requests')` 等を使って明示的に同梱。

### gspread 引数順問題
`ws.update([[val]], 'Q2')` 形式が新構造で機能しない → `ws.update_acell('Q2', val)` に統一（5/5）。

### Policy違反商品（IPR violation）の挙動検証（5/5）
- GetItem: Failure ack でも Item要素は含まれる → 処理続行可能
- ReviseFixedPriceItem: Warning ack（成功扱い）で在庫更新可
- EndItem: 同上で削除可（権限的拒否なし）
- 検出: `ON_HOLD_FIXABLE` or ErrorCode `21920397/21920396`

### Apps Script API による bound project 自動作成
clasp の OAuth トークン (`~/.clasprc.json`) を流用して Apps Script API を直接叩き、bound project 作成 + コード push を完全自動化。  
社長作業は「Apps Script API を一度オンにする」のみ（ブラウザ自動操作で実施）。

### 完成した v8 の構造（2026-05-05）
- フェーズ1: メインパス（resume 開始位置〜最終行）
- フェーズ2: リトライパス（最大5回・進捗ゼロで打ち切り）
- 完了 → resume クリア → 1時間休憩（30秒ごとに削除キューポーリング） → 次の周

詳細は `handoff_20260505_asics_v8_complete.md` 参照。
