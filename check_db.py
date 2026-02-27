import sqlite3
import os

db_path = 'db.sqlite3'

if os.path.exists(db_path):
    print(f"База данных найдена: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\nТаблицы в базе данных ({len(tables)}):")
    for table in tables:
        print(f"  - {table[0]}")
        
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"    Записей: {count}")
        except:
            pass
    
    conn.close()
else:
    print(f"База данных не найдена: {db_path}")