import config

conn=config.conn
conn.set("name","nyc")

val = conn.get("name")
print( val)