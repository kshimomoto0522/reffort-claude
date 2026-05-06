"""
BayChat STG データベース接続ユーティリティ
=========================================
VPS（固定IP）を踏み台にしてSSHトンネル経由でSTG MariaDBに接続する。

使い方:
  from db_connect import get_connection, get_tunnel_and_connection

  # 自動でトンネル+接続（with文で安全に閉じる）
  with get_tunnel_and_connection() as (tunnel, conn):
      cursor = conn.cursor()
      cursor.execute("SHOW TABLES")
      print(cursor.fetchall())
"""

import os
import subprocess
import time
import pymysql
from dotenv import dotenv_values

# ===== パス設定 =====
# このスクリプトの1つ上のフォルダ（baychat-ai）に.envがある
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_BAYCHAT = os.path.join(BASE_DIR, ".env")
ENV_VPS_CANDIDATES = [
    os.path.join(os.path.dirname(BASE_DIR), ".env.vps"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), ".env.vps"),
]
ENV_VPS = next((p for p in ENV_VPS_CANDIDATES if os.path.exists(p)), ENV_VPS_CANDIDATES[0])
SSH_KEY = os.path.expanduser(r"~\.ssh\id_ed25519_vps_baychat")

# ===== SSHトンネル用のローカルポート =====
LOCAL_PORT = 13306


def load_env():
    """
    .envファイルからDB接続情報とVPS情報を読み込む。
    返り値: (baychat_env, vps_env) の辞書タプル
    """
    baychat = dotenv_values(ENV_BAYCHAT)
    vps = dotenv_values(ENV_VPS)
    return baychat, vps


def start_ssh_tunnel(vps_host, db_host, db_port=3306):
    """
    SSHトンネルをバックグラウンドで起動する。
    ローカルの13306ポート → VPS → RDS(db_host:db_port)

    返り値: subprocess.Popen オブジェクト
    """
    cmd = [
        "ssh", "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=no",
        "-L", f"{LOCAL_PORT}:{db_host}:{db_port}",
        "-N",  # コマンドを実行しない（トンネルのみ）
        f"root@{vps_host}"
    ]

    # バックグラウンドで起動
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # トンネルが確立するまで少し待つ
    time.sleep(2)

    # プロセスが生きているか確認
    if proc.poll() is not None:
        stderr = proc.stderr.read().decode("utf-8", errors="replace")
        raise ConnectionError(f"SSHトンネルの起動に失敗しました: {stderr}")

    return proc


def connect_to_db(user, password, database=None, port=LOCAL_PORT):
    """
    ローカルポート経由でMariaDBに接続する。
    SSHトンネルが起動済みであることが前提。

    返り値: pymysql.Connection オブジェクト
    """
    conn = pymysql.connect(
        host="127.0.0.1",
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        connect_timeout=10,
        # 辞書形式でデータを返す（カラム名でアクセスできて便利）
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn


class get_tunnel_and_connection:
    """
    SSHトンネル + DB接続をまとめて管理するコンテキストマネージャー。

    使い方:
      with get_tunnel_and_connection() as (tunnel, conn):
          cursor = conn.cursor()
          cursor.execute("SELECT 1")

    withブロックを抜けると自動的にDB接続とSSHトンネルが閉じる。
    """

    def __init__(self, database=None):
        """
        database: 接続先DB名。Noneの場合はDB指定なし（SHOW DATABASESなどが可能）
        """
        self.database = database
        self.tunnel_proc = None
        self.conn = None

    def __enter__(self):
        # .env読み込み
        baychat, vps = load_env()

        vps_host = vps.get("VPS_HOST")
        db_host = baychat.get("BAYCHAT_STG_DB_HOST")
        db_port = int(baychat.get("BAYCHAT_STG_DB_PORT", "3306"))
        db_user = baychat.get("BAYCHAT_STG_DB_USER")
        db_pass = baychat.get("BAYCHAT_STG_DB_PASSWORD")
        db_name = self.database or baychat.get("BAYCHAT_STG_DB_NAME") or None

        # SSHトンネル起動
        self.tunnel_proc = start_ssh_tunnel(vps_host, db_host, db_port)

        # DB接続
        self.conn = connect_to_db(db_user, db_pass, db_name)

        return (self.tunnel_proc, self.conn)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # DB接続を閉じる
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass

        # SSHトンネルを終了
        if self.tunnel_proc:
            try:
                self.tunnel_proc.terminate()
                self.tunnel_proc.wait(timeout=5)
            except Exception:
                self.tunnel_proc.kill()

        return False  # 例外を再送出


# ===== 直接実行時のテスト =====
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=== BayChat STG DB 接続テスト ===")
    print()

    with get_tunnel_and_connection() as (tunnel, conn):
        cursor = conn.cursor()

        # データベース一覧
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("【利用可能なデータベース】")
        for db in databases:
            # DictCursorなのでキーでアクセス
            for key, val in db.items():
                print(f"  - {val}")

        print()
        print("接続テスト成功！")

    print("切断完了。")
