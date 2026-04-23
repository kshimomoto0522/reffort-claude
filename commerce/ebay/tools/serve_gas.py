# ================================================================
# CORS対応HTTPサーバー（gas_shiire_tool.js配信用）
# ポート8765で起動。localhost:8765/gas_shiire_tool.js でアクセス可能
# ================================================================
import http.server
import socketserver
import os

PORT = 8765
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # CORS許可ヘッダーを追加
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

with socketserver.TCPServer(("127.0.0.1", PORT), CORSHandler) as httpd:
    print(f"Serving {DIRECTORY} on http://127.0.0.1:{PORT}/")
    httpd.serve_forever()
