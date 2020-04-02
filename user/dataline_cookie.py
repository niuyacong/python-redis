# 数据行缓存
# 对于一些不能缓存的页面（用户账户页面，记录用户以往购买商品的页面，促销页面，需要看到真实的库存）
# 可以通过缓存页面载入时所需的数据库行来减少载入页面所需的时间

# 具体做法
# 编写一个持续运行的守护进程函数，让这个函数将指定的数据行缓存到redis里面，并不定期的对这些缓存进行更新
# 缓存函数将会将数据行进行编码（encode）为json字典并存储在redis的字符串里面
# 数据列（column）的名字被映射为json字典的键，而数据行的值则会被映射为json字典的值
# 例
# 键：inv:273  值（字符串）：{"qty":926,"name":"gtab","description":"..."}

# 程序使用了两个有序集合来记录应该在何时对缓存进行更新  
# 第一个有序集合为调度有序集合，他的成员为数据行的行id,分值是一个时间戳，时间戳记录了应该在何时将指定的数据行缓存到redis里面
# 第二个有序集合为延时有序集合，它的成员也是数据行id,分值记录了指定数据行的缓存需要每隔多少秒更新一次

import config.conn
import time
conn=config.conn
import json

# 复制调度缓存和终止缓存的函数
def schedule_row_cache(conn,row_id,delay):
    conn.zadd('delay:',row_id,delay)
    conn.zadd('schedule:',row_id,time.time())

# 守护进程 缓存数据
# 发现一个需要立即进行更新的数据行时，缓存函数会检查这个数据行的延迟值
# 如果数据行的延迟值小于或等于0，那么缓存函数会从延迟有序集合和调度有序集合中移除这个数据行的id
# 并从缓存里面删除这个数据行已有的缓存，然后重新进行检查
# 对于延迟值大于0的数据行来说，缓存函数会从数据库里面取出这些行，将他们编码成json格式并存储到redis里面，然后更新调度时间
QUIT=False
def cache_rows(conn):
    while not QUIT:
        next=conn.zrange('schedule:',0,0,withscores=True)
        now=time.time()
        if not next or next[0][1]>now:
            # 休眠50毫秒
            time.sleep(.05)
            continue
        row_id=next[0][0]
        # 提前获取下一次调度的延迟时间
        delay=conn.zscore('delay:',row_id)
        # 什么时候delay会小于等于0？？？
        if delay<=0:
            conn.zrem('delay:',row_id)
            conn.zrem('schedule:',row_id)
            conn.delete('inv:'+row_id)
            continue
        # 读取数据行
        row=Inventory.get(row_id)
        conn.zadd('schedule:',row_id,now+delay)
        conn.set('inv:'+row_id,json.dumps(row.to_dict()))





