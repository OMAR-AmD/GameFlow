import sqlite3
import pandas as pd

conn = sqlite3.connect('data/processed/gameflow.db')
df = pd.read_sql("SELECT * FROM games WHERE name LIKE '%Panzer Strategy%'", conn)
print(df)
conn.close()
