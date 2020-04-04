import config.conn
import time
conn=config.conn

# 网页缓存

# def cache_request(conn,request,callback):
#     # 不能被缓存的请求，直接调用回调函数
#     if not can_cache(conn,request):
#         return callback(request)
#     page_key='cache:'+hash_request(request)
#     content=conn.get(page_key)
#     # 如果页面没有缓存，那么生成页面
#     if not content:
#         content=callback(request)
#         # 将新生成的页面放到缓存里面
#         conn.setex(page_key,content,300)
#     return content


# 网页分析
# user_cookie中对商品的浏览进行了记录，并按浏览次数进行了排序
# 为了让商品的浏览次数排行榜保持最新，需要定期修剪有序集合的长度并调整已有元素的分值
# ZINTERSTORE可以组合一个或多个有序集合，并将有序集合包含的每个分值都乘以一个给定的数值（用户可以为每个有序集合分别指定不同的相乘数值）
# 每隔五分钟，删除所有排名在20000名之后的商品，并将删除之后剩余的所有的商品浏览次数减半

# 守护进程
QUIT=False
def rescale_viewed(conn):
    while not  QUIT:
            conn.zremrangebyrank('viewed:',0,-20001)
            # 将浏览次数减少为原来的一半
            conn.zinterstore('viewed:',{'viewed:':.5})
            # 五分钟之后再次执行
            time.sleep(300)

# 页面是否需要被缓存
def can_cache(conn,request):
    # 尝试从页面中取出商品id
    item_id=extract_item_id(request)
    # 检查这个页面能否被缓存以及这个页面是否为商品页面
    if  not item_id or is_dynamic(request):
        return False
    # 取得商品浏览次数排名
    rank=conn.zrank('viewed:',item_id)
    # 根据商品的浏览次数排名来判断是否需要缓存这个页面
    return rank is not None or rank<10000

# 如果我们想以最少的代价来存储更多的页面
# 那可以考虑先对页面进行压缩，然后再缓存到redis里面
# 或者使用 edge side includes 技术移除页面中的部分内容
# 又或者对模板进行提前优化（pre-optimize）,移除所有非必要的空格字符