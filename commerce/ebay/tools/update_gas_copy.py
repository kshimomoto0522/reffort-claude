# ================================================================
# gas_shiire_tool.js → gas_copy.html 変換スクリプト
# HTMLエスケープ処理をしてtextareaに埋め込む
# 使い方: python update_gas_copy.py
# ================================================================
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, 'gas_shiire_tool.js')
dst_path = os.path.join(script_dir, 'gas_copy.html')

with open(src_path, 'r', encoding='utf-8') as f:
    js = f.read()

# HTMLエスケープ（&を最初に処理する必要がある）
escaped = (js.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace("'", '&#x27;')
             .replace('"', '&quot;'))

html = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>GAS Code</title></head>
<body>
<textarea id="code" style="width:100%;height:90vh;font-family:monospace;font-size:12px">''' + escaped + '''</textarea>
<button onclick="document.getElementById('code').select();document.execCommand('copy');alert('Copied!')">Copy All</button>
</body></html>'''

with open(dst_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'OK: {dst_path} を更新しました（{len(js)} 文字）')
