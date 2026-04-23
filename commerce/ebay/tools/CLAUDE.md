# eBayツール開発部門 — 部門ドキュメント
> 親ドキュメント: `/reffort/CLAUDE.md` を必ず先に読むこと。
> このフォルダでは「eBay輸出事業を支えるツールの開発・改善・新規構築」に特化して動く。

---

## この部門の目的

スタッフが手作業でやっている業務をツールで自動化し、最終的には「半分AI・半分スタッフ」の体制を実現する。

| ツール領域 | 概要 | 優先度 |
|-----------|------|--------|
| 在庫管理ツール（ASICS）| Firefox/Selenium版・稼働中 | ✅ 稼働中 |
| 在庫管理ツール（adidas）| Firefox/Selenium版・稼働中 | ✅ 稼働中 |
| 商品リサーチツール | 売れ筋・仕入れ候補の自動抽出 | 高 |
| 競合リサーチツール | ライバルセラーの出品・価格収集 | 高 |
| 価格調整ツール | 自動価格提案 | 中 |
| HIROUNエクセル精査ツール | 仕入候補リスト自動生成 | 中 |

---

## 開発優先順位（2026年3月21日更新）

| 優先度 | ツール | 状態 | 次のアクション |
|--------|--------|------|--------------|
| ⚠️ 改善中 | **ASICSツール** | **旧exe暫定稼働中 / v2.3待機** | v2の成功率改善・旧ツールとの差分分析 |
| ✅ 稼働中 | **adidasツール（scrape_adidas_v1.py）** | **テスト完了・タスク登録済み** | 商品追加に応じてモニタリング |
| 🟠 高 | HIROUNエクセル精査ツール | 未着手 | HIROUNのエクセル形式を確認してClaudeで試作 |
| 🟠 高 | 競合リサーチツール（eBay API版） | 未着手 | eBay Finding APIで試作 |
| 🟡 中 | 価格調整ツール（提案型） | 未着手 | 競合リサーチツール完成後 |
| 🟢 将来 | 出品補助ツール（AIタイトル生成） | 未着手 | BayChat AI Reply完成後 |

---

## 在庫管理ツール — ツールフォルダ

`C:\Users\KEISUKE SHIMOMOTO\Desktop\eBay在庫調整ツール（アシックス）\`

### ファイル一覧

| ファイル | 役割 | 対象 |
|---------|------|------|
| `scrape_data_v2.py` | メインツール（Firefox/Selenium版） | ASICS |
| `test_3rows.py` | 3件テスト用 | ASICS |
| `run_v2.bat` | タスクスケジューラ用（→ run_asics.ps1を呼ぶ） | ASICS |
| `scrape_adidas_v1.py` | メインツール（Firefox/Selenium版） | adidas |
| `test_adidas_3rows.py` | 3件テスト用 | adidas |
| `run_adidas.bat` | タスクスケジューラ用（→ run_adidas.ps1を呼ぶ） | adidas |
| `run_asics.ps1` | PowerShellランチャー（ツールフォルダ内） | ASICS |
| `run_adidas.ps1` | PowerShellランチャー（ツールフォルダ内） | adidas |
| `fix_status.py` | ステータスを「編集OK」に手動リセット | ASICS |
| `stop_tool.bat` | ツール手動停止 | 共通 |
| `config.xlsx` | APIキー・設定 | 共通 |
| `multivariations-8bd0cb82d2e1.json` | Google認証ファイル | 共通 |
| `geckodriver.exe` | Firefox用ドライバ | ASICS・adidas共通 |

### デスクトップのランチャーファイル（重要）

タスクスケジューラの日本語パス問題を回避するため、以下のps1ファイルをデスクトップに配置。
**これらは絶対に削除しないこと。**

| ファイル | 場所 | 役割 |
|---------|------|------|
| `run_asics.ps1` | `C:\Users\KEISUKE SHIMOMOTO\Desktop\` | ASICSツール起動（UTF-8 BOM） |
| `run_adidas.ps1` | `C:\Users\KEISUKE SHIMOMOTO\Desktop\` | adidasツール起動（UTF-8 BOM） |

### 日本語パス問題（解決済み・経緯記録）

- タスクスケジューラはcmd.exe経由でbatファイルを実行する
- ツールフォルダ名に日本語（アシックス）が含まれている
- cmd.exeのタスクスケジューラ環境では日本語パスが文字化けする
- **解決策**: bat → デスクトップのps1（日本語なしパス）→ PowerShell内で日本語パスを処理
- ps1ファイルはUTF-8 BOM形式で保存する必要がある（PowerShellがBOMを認識して正しく読む）

---

## ASICSツール（稼働中）

### 仕様
- **方式**: Firefox/Selenium（ヘッドレス）
  - 当初Scrapling版で開発したが、ASICS.comのBot検出で403エラーが頻発
  - ブラウザで同じURLを開くと正常 → ボット検出が原因（IPブロックではない）
  - Firefox/Seleniumに切り替えて403を解消
- **待機時間**: 240秒（固定）— 10〜20秒だとAkamaiにBot検出される
- **バッチ書き込み**: 15件ごとにスプレッドシートに途中保存（カウンター方式）
- **シート名**: `eBay在庫調整`（旧ツール互換のため元の名前に戻した）
- **SPREADSHEET_KEY**: `12SGD4RLze25JC6PWCFCOTxbk2qtL5UGp0D3B_mklK68`

### タスクスケジューラ（登録済み）
| タスク名 | 実行時刻 | 呼び出し先 |
|---------|---------|-----------|
| ASICS_v2_01ji | 毎日 01:00 | run_v2.bat → Desktop\run_asics.ps1 |
| ASICS_v2_09ji | 毎日 09:00 | run_v2.bat → Desktop\run_asics.ps1 |
| ASICS_v2_17ji | 毎日 17:00 | run_v2.bat → Desktop\run_asics.ps1 |

### スプレッドシート構造
- **行1**: ヘッダー行（旧ツール互換のためステータス行を撤廃）
- **行2以降**: データ
- ※ v2のA1ステータス書き込み機能は旧ツールのヘッダーを破壊するため注意

### 運用ルール
| 操作 | タイミング |
|------|----------|
| 行削除・途中挿入 | ツール停止中のみ（行番号ズレでデータ破損） |
| 一番下への追加 | いつでもOK |
| End商品の削除 | 行ごと削除（セルだけ消さない） |

### Scrapling → Selenium 移行の経緯（2026年3月20-21日）
1. Scrapling版で稼働開始 → 最初の数件後に403 Forbidden連発
2. 遅延を5-15秒→30-60秒に変更 → 依然として403
3. ブラウザでは同じURLが正常に開ける → IPブロックではなくBot検出
4. adidas用に作ったFirefox/Selenium方式をASICSにも適用 → 403解消
5. テスト: 以前403だった3URLすべてで200 OK確認

### 並列化失敗の教訓（2026年3月26日）
1. 240秒・1台で安定動作（22件成功・Access Denied 0件）
2. 高速化のため120秒・3台並列を試行 → Akamaiにブロックされた
3. ヘッドレスFirefoxでの確認を繰り返し、状況を悪化させた
4. **教訓**: 安定動作を急激に変更しない。変更は段階的に（1パラメータずつ）
5. **教訓**: Access Denied = IPブロックとは限らない。ブラウザで開ければBot検出が原因

### v2.3修正（2026年3月27日）— Access Denied過剰防御の是正
**問題**: v2.2はAccess Deniedのたびに Firefox再起動+240秒追加待機+累計10件で強制終了 → 5.5時間で11件しか処理できない
**旧ツールとの比較**: 旧ツール（exe）は同じFirefox+240秒間隔で2日で600件全件処理できていた

**v2.3の変更点**:
1. Access DeniedでFirefox再起動しない（セッション維持で30-60秒待機リトライ）
2. 累計失敗10件の強制終了を撤廃（時間制限まで続行）
3. 連続失敗クールダウンを10分→3分に短縮
4. configのdelay値をそのまま使用（ハードコード廃止）

**v2.3実行結果**: 84件成功 / 102件エラー（成功率45%）/ 14時間稼働
→ v2.2比で処理件数9倍、成功件数7.6倍に改善。ただしAccess Denied率は依然55%

### 旧ツール（exe）の現状（2026年3月30日更新）
- `scrape_data.exe` はPyInstaller製（Python 3.8）
- **起動不可の根本原因**: v2開発時にシート名を `'eBay在庫調整'` → `'【ASICS】在庫管理'` にリネームしたこと
- 旧exeは `'eBay在庫調整'` をハードコードしており修正不可
- **解決**: シート名を `'eBay在庫調整'` に戻して起動成功（2026/3/30）
- **現在**: 土日の暫定運用として旧exeで稼働中
- **注意**: config.xlsxのD-G列（eBay APIトークン）は旧exeも使用する。値を変更しないこと
- **次のステップ**: v2の成功率を改善し、旧exeから移行する

---

## adidasツール（稼働中）

### 仕様
- **方式**: Selenium + Firefox（ヘッドレス）
  - adidas.jpはAkamai Bot Managerで強力に保護
  - Scraplingは完全ブロック → Firefoxなら突破できることを確認済み
  - ヘッドレス = 画面に表示されない（バックグラウンド動作）
- **待機時間**: 10〜15秒ランダム
- **シート名**: `【adidas】在庫管理`（同じスプレッドシートの別タブ）
- **現在の商品数**: 1件（テスト済み・正常動作確認）

### HTMLパース仕様
```
サイズ取得: soup.select('button[role="radio"]')
在庫判定: '現在ご購入いただけません。' が含まれていない → 在庫あり
```

### タスクスケジューラ（登録済み）
| タスク名 | 実行時刻 | 呼び出し先 |
|---------|---------|-----------|
| ASICS_adidas_01ji | 毎日 01:00 | run_adidas.bat → Desktop\run_adidas.ps1 |
| ASICS_adidas_09ji | 毎日 09:00 | run_adidas.bat → Desktop\run_adidas.ps1 |
| ASICS_adidas_17ji | 毎日 17:00 | run_adidas.bat → Desktop\run_adidas.ps1 |

---

## スクレイピング技術メモ

| サイト | 方式 | 結果 |
|--------|------|------|
| ASICS.com | Scrapling（HTTP） | ❌ 数件後に403（Bot検出） |
| ASICS.com | Selenium + Firefox | ✅ 安定動作 |
| adidas.jp | Scrapling（HTTP） | ❌ Akamaiブロック |
| adidas.jp | Selenium + Firefox | ✅ 突破可能 |

**結論**: 両サイトともFirefox/Seleniumが必要。Scraplingは使わない。

---

## SKU・在庫管理ルール（ASICS・adidas共通）

### Zフラグシステム
- 在庫あり: `S05288-25Z`（末尾にZ）
- 在庫なし: `S05288-25`（Zなし）
- 0→1更新時: 連番インクリメント（`S05288-25Z` → `S05288-26Z`）

### 在庫状況フォーマット
| 表示 | 意味 |
|------|------|
| `X/在Y` | サイト在庫X件 / eBay有在庫Y件 |
| `在庫切れ` | サイト・eBay両方ゼロ |
| `在庫処理停止` | 14日以上在庫切れ継続 |
| `出品無し` | eBayに出品なし |
| `End` | eBayリスティングが終了 |

---

## Claudeがスプレッドシートを直接読める

ツールと同じGoogle Sheets APIの認証情報を使えば、Claudeがスプレッドシートを直接読み取り可能。
スクリーンショットは不要。

```python
# 読み取りコード例
from scrape_data_v2 import SpreadsheetClass, read_config
_, _, KEY, _, _, _, _ = read_config()
ss = SpreadsheetClass(KEY)
ws = ss._get_worksheet('【ASICS】在庫管理')
rows = ws.get_all_values()
```

---

## Claudeへの重要ルール（ツール開発部門専用）

- **スクレイピングは必ず対象サイトのrobots.txtを確認してから行うこと**
- **本番データへのアクセス・eBayへの自動操作は必ず社長確認を取ること**
- **ツール実行中にコードを変更してもOK**（Pythonはすでにメモリに読み込み済み、次回実行から反映）
- **繰り返しアクセスでIPブロックされないよう注意すること**
- eBay APIのレート制限に注意（特にTrading API）
- コードには日本語コメントを必ず入れること
- 提案は「今すぐClaudeで作れるもの」と「Cowatechに依頼が必要なもの」を分けて提示すること

---

## 仕入管理表 GASツール（gas_shiire_tool.js）

### 概要
eBay Trading API（GetOrders）から新規オーダーを自動取得し、仕入管理表スプレッドシートに反映するGoogle Apps Scriptツール。

### ファイル・環境
| 項目 | 値 |
|------|-----|
| マスターファイル | `commerce/ebay/tools/gas_shiire_tool.js` |
| 本番Apps Script | `1EGuRaF3Hj1Uhayek4jCIgGQcxzKEJxLaqZmqfsgZbRph_RYUNZRgCNNf` |
| テストApps Script | `1s52yu6RVQ3kCPk0MIvR4Gst-bG_DcmXD3jFLjrFBfqNNbbAtb24hlusv` |
| 本番スプレッドシート | `1B1kFIiu8M5Pw8U8YuERK8ApKUa4S--GfIzBkW53kY3g` |
| テストスプレッドシート | `1vkhstYuPhgQJecDfSdMjL67mWsdthtkHJ6HjnXF-KAk` |
| トリガー | 毎朝9:45頃（nearMinute(45)）本番設定済み |
| APIキー | Script Propertiesに保存（EBAY_DEV_ID / APP_ID / CERT_ID / USER_TOKEN） |

### 主な機能（2026-04-22 大改修後）
- eBay Trading API GetOrders で**過去2日**分のオーダーを取得（FETCH_DAYS_BACK=2）
- `OrderStatus=All` で取得（Cancelled/CancelPendingも含む → キャンセル検知漏れ防止）
- **前回処理時刻（LAST_PROCESSED_CREATED_TIME）以降のみ処理**（Refunded蘇り防止）
- OrderNo + 正規化SKU の組み合わせで重複排除（Z除去正規化で過去データと共存）
- 過去の仕入履歴から型番・仕入先・仕入値を自動参照
- タイトルから型番・**Width（New Balance）**を自動抽出
- キャンセル検知4系統（OrderStatus・CancelStatus・BuyerRequestedCancel・CancelReason）
- **多言語サイズラベル対応**（Schuhgröße / Pointure / Taglia 等 + US/JP/UK/EU値パターン検出）
- O列にタイトル（eBay商品ページハイパーリンク付き）
- E3に赤文字太字の処理中通知（スタッフ向け）
- LockService排他ロック（2重実行防止）
- **Z除去はしない**（シートにZ付きSKUを維持、有在庫判定は `hasStock` フラグで）
- 同一オーダー複数商品 → E列（送料）セル結合

### 重複バグ対策（3層防御）
- **対策A（根本）**: `normalizeSkuForCompare_` でシート側・API側の両方をZ除去正規化して比較
- **対策G（検出）**: 同一orderNumberが既存にあるのに新規判定された場合、実行ログに警告
- **対策H（事前検査）**: 🛡️ 重複安全チェックメニューで既存重複・Z混在を事前洗い出し

### 新設メニュー
- 🛡️ 重複安全チェック（本番反映前に推奨）
- 🔍 特定オーダーのXMLを確認（デバッグ用・特定オーダーIDで生XML取得）
- ⏮️ 前回処理時刻をリセット

### SKU Zフラグルール
- サイズ部分のZ = 有在庫（例: `V0126-8.5Z-30`）
- 親SKU先頭のZ ≠ 有在庫（例: `Z0196-11-23` は無在庫）
- 有在庫判定正規表現: `/-\d+\.?\d*Z(?:-|$)/`
- 重複比較時の正規化正規表現: `/(\d+\.?\d*)Z(?=-|$)/`（書き込み時は除去しない）

### 本番既存の重複4組（放置・社長指示で削除しない）
過去のZ除去バグによる重複。新コードでは発生しない。
- 行 7233/7597、7242/7363、7361/7776、7568/7792

### コード更新手順（2026-04-22 実証済み）
1. `gas_shiire_tool.js`をローカルで編集
2. PowerShellで `Get-Content gas_shiire_tool.js -Raw -Encoding UTF8 | Set-Clipboard`
3. Apps Scriptエディタを開いて `textarea.inputarea` にフォーカス
4. JS実行で `monaco.editor.getModels()[0].setValue('')` で空にする
5. Ctrl+V で貼り付け → **8秒以上wait**（Monaco大規模ペーストは遅い）
6. `monaco.editor.getModels()[0].getValue().length` で文字数・関数存在を検証
7. Ctrl+S で保存

---

*最終更新: 2026年4月22日未明*
*ASICSツール: v2.3稼働中*
*adidasツール: 稼働中*
*仕入管理表GASツール: 本番反映完了（1331行・4大改修・明朝自動実行で最終検証待ち）*
