# -*- coding: utf-8 -*-
broker_url = 'redis://localhost'    # 使用Redis作为消息代理

result_backend = 'redis://localhost:6379/0'  # 把任务结果存在了Redis

# CELERY_TASK_SERIALIZER = 'msgpack'  # 任务序列化和反序列化使用msgpack方案

# CELERY_RESULT_SERIALIZER = 'json'   # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON

result_expires = 60 * 60 * 24   # 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显

accept_content = ['json', 'msgpack']     # 指定接受的内容类型

worker_concurrency = 10    # 并发worker数

broker_connection_retry_on_startup = True