import config
import sentry_sdk
sentry_sdk.init("https://928cc37ab8624323b9c20e4481def629@o377359.ingest.sentry.io/5199440")

conn=config.conn
conn.set("name","nyc")

division_by_zero = 1 / 0
val = conn.get("name")
print( val)