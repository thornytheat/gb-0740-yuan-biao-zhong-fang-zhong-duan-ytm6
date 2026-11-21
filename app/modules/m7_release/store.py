import json
import sqlite3
from contextlib import closing
from pathlib import Path


class Catalog:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connection()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS plans (id TEXT PRIMARY KEY, document TEXT NOT NULL)")

    def connection(self):
        return sqlite3.connect(self.path, timeout=10)

    def get(self, key):
        with closing(self.connection()) as db:
            row = db.execute("SELECT document FROM plans WHERE id=?", (key,)).fetchone()
            return json.loads(row[0]) if row else None

    def save(self, key, result):
        with closing(self.connection()) as db, db:
            op = db.execute(
                "INSERT OR IGNORE INTO plans VALUES (?,?)", (key, json.dumps(result, ensure_ascii=False))
            )
            record = db.execute("SELECT document FROM plans WHERE id=?", (key,)).fetchone()[0]
            return json.loads(record), not op.rowcount

    def latest(self):
        with closing(self.connection()) as db:
            return [
                json.loads(row[0])["批次"]
                for row in db.execute("SELECT document FROM plans ORDER BY rowid DESC LIMIT 30")
            ]
