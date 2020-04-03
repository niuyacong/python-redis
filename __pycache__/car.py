import config.conn
import time
conn=config.conn

# 购物车功能
def add_to_cart(conn,session,item,count):
    if  count<=0:
        conn.hrem('cart:'+session,item)
    else:
        conn.hset('cart:'+session,item,count)
    
