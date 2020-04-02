import config.conn
import time
conn=config.conn

# 1、签名cookie   有用户信息，用户id等信息，还有签名
# 2、令牌cookie   一串随机字节

# 用一个散列存储登录cookie令牌和已登录用户之间的映射

def  check_token(conn,token):
    return conn.hget('login:',token)

# 更新令牌方法
def update_token(conn,token,user,item=None):
    timestamp=time.time()
    conn.hset('login:',token,user)
    conn.zadd('recent:',token,timestamp)
    if item:
        # 增加浏览记录
        conn.zadd('viewed:'+token,item,timestamp)
        # 只保留前25个浏览记录
        conn.zremrangebyrank('viewed:'+token,0,-26)

# 限制会话数据的数量，只保留最新的1000万个会话。
# 在本地以守护进程运行，比网络请求要快很多
QUIT=False
LIMIT=1000000
def clean_sessions(conn):
    while not QUIT:
        size=conn.zcard('recent:')
        if size<=LIMIT:
            time.sleep(1)

            continue
        end_index=min(size-LIMIT,100)
        tokens=conn.zrange('recent:',0,end_index-1)

        session_keys=[]
        for token in tokens:
            session_keys.append('viewed:'+token)
        # 删除超过最大限制的旧数据 浏览数据
        conn.delete(*session_keys)
        # 删除旧数据的登录信息
        conn.hdel('login:',*tokens)
        # 删除旧数据的最近登录记录
        conn.zrem('recent:'*tokens)

        