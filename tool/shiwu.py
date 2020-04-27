# 使用事务来处理命令的并行执行问题
import config.conn
import time
import threading
import xrange
conn=config.conn


def trans():
    pipeline=conn.pipeline()
    pipeline.incr('trans:')
    time.sleep(.1)

    pipeline.incr('trans:',-1)
    # redis要在接收到exec命令之后，才会执行那些位于mutil和exec命令之间的入队命令
    print(pipeline.execute()[0])

if 1:
    for i in xrange(3):
        threading.Thread(target=trans).start()
    time.sleep(.5)