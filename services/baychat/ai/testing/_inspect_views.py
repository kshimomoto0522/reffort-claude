"""
view_chat_ebay と view_order_ebay のスキーマ詳細確認
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from db_connect import get_tunnel_and_connection

SELLER_UID = "05698b31-d523-4004-8dbc-be1c4483c41d"

with get_tunnel_and_connection(database="ebay_stg") as (tunnel, conn):
    cur = conn.cursor()

    print("=== view_chat_ebay カラム ===")
    cur.execute("DESCRIBE view_chat_ebay")
    for col in cur.fetchall():
        print(f"  {col['Field']:30s} {col['Type']}")

    print("\n=== view_order_ebay カラム ===")
    cur.execute("DESCRIBE view_order_ebay")
    for col in cur.fetchall():
        print(f"  {col['Field']:30s} {col['Type']}")

    print("\n=== view_chat_ebay レコード数 ===")
    cur.execute("SELECT COUNT(*) as cnt FROM view_chat_ebay")
    print(cur.fetchone())

    print("\n=== senderId ごとの件数（SELLER UID=shimomoto） ===")
    cur.execute("""
        SELECT senderId, COUNT(*) as cnt
        FROM view_chat_ebay
        GROUP BY senderId
        ORDER BY cnt DESC
        LIMIT 15
    """)
    for row in cur.fetchall():
        mark = " ← SELLER(shimomoto)" if row['senderId'] == SELLER_UID else ""
        print(f"  {row['senderId']}: {row['cnt']}{mark}")

    print("\n=== view_chat_ebay サンプル1件（SELLER発信） ===")
    cur.execute("""
        SELECT *
        FROM view_chat_ebay
        WHERE senderId = %s
        LIMIT 1
    """, (SELLER_UID,))
    row = cur.fetchone()
    if row:
        for k, v in row.items():
            val_preview = str(v)[:120] if v is not None else "NULL"
            print(f"  {k}: {val_preview}")

    print("\n=== view_chat_ebay サンプル1件（バイヤー発信） ===")
    cur.execute("""
        SELECT *
        FROM view_chat_ebay
        WHERE senderId != %s
        LIMIT 1
    """, (SELLER_UID,))
    row = cur.fetchone()
    if row:
        for k, v in row.items():
            val_preview = str(v)[:120] if v is not None else "NULL"
            print(f"  {k}: {val_preview}")

    print("\n=== view_chat_ebay サンプル1件（system JSON） ===")
    cur.execute("""
        SELECT *
        FROM view_chat_ebay
        WHERE messages LIKE '{%'
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        for k, v in row.items():
            val_preview = str(v)[:250] if v is not None else "NULL"
            print(f"  {k}: {val_preview}")

    print("\n=== view_order_ebay サンプル1件 ===")
    cur.execute("SELECT * FROM view_order_ebay LIMIT 1")
    row = cur.fetchone()
    if row:
        for k, v in row.items():
            val_preview = str(v)[:120] if v is not None else "NULL"
            print(f"  {k}: {val_preview}")
