import os
from dotenv import load_dotenv
from callback import *


# 加载 .env 文件中的环境变量
load_dotenv()


# 定时任务设置
timer_task_config = {
    "timer_task_1": {  # 键名为任务名，用于查询，可自定义
        'interval': 15,  # 定时器间隔(秒)
        'client_id': 'client_01',  # 指定执行命令的OC客户端id
        'commands': [  # 远程执行的命令列表
            "return 114514",
        ],
        'cache': False,  # 是否缓存数据，即创建新任务时上次任务的数据不会清空
        'handle': None,  # 命令执行后的处理函数，results = handle(results: list)，应有返回值，不需要则None
        'callback': test,  # 命令执行后的回调函数，callback(results: list)，其中results是经过处理过的(handle)，不需要则None
    },
}


# 任务组设置，该任务执行结束后会调用callback
task_config = {
    "echo": {  # 键名为任务名，用于发起任务，可自定义
        'client_id': 'client_01',  # 指定执行命令的OC客户端id
        'commands': [  # 远程执行的命令列表
            "return echo(114514)",
        ],
        'cache': False,  # 是否缓存数据，即创建新任务时上次任务的数据不会清空
        'handle': None,  # 命令执行后的处理函数，results = handle(results: list)，应有返回值，不需要则None
        'callback': test,  # 命令执行后的回调函数，callback(results: list)，其中results是经过处理过的(handle)，不需要则None
    },
}



SERVER_TOKEN = os.getenv('SERVER_TOKEN')
