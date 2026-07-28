import sqlite3
from pathlib import Path

def add_content_index(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS content_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT,
            sha256 TEXT UNIQUE,
            md5 TEXT,
            canonical_path TEXT,
            size INTEGER,
            mtime_ns INTEGER
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_content_sha256 ON content_index(sha256)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_content_id ON content_index(content_id)")
    conn.commit()
    conn.close()
    print("✅ Tabela content_index criada")

if __name__ == "__main__":
    import sys
    db = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../eddy.db")
    add_content_index(db)
