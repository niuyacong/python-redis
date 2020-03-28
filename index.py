import config

config.conn.set("x1","hello")

val = config.conn.get("x1")
print( val)