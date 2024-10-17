import threading
from utils import task_manager, READY
from config import timer_task_config

timers = {}

def add_task_periodically(task_id, content):
    """
    添加任务到队列并根据任务的间隔继续递归调用自己
    """
    # 将任务添加到队列中
    if content.get('cache', False):
        task_manager.update_task(task_id, status=READY)
    else:
        task_manager.add_task(
            task_id,
            content.get('client_id', None),
            content.get('commands', {}),
            READY
        )
    
    # 创建一个新的定时器
    interval = content.get('interval', 30)
    timer = threading.Timer(interval, add_task_periodically, args=[task_id, content])

    # 保存定时器对象，方便后续取消
    timers[task_id] = timer

    # 启动定时器
    timer.start()


def start_scheduler():
    """
    启动任务调度，为每个 task_id 创建独立的定时器
    """
    for task_id, content in timer_task_config.items():
        interval = content.get('interval', 30)

        # 创建定时器，并在指定间隔时间后调用 add_task_periodically 函数
        timer = threading.Timer(interval, add_task_periodically, args=[task_id, content])

        # 保存定时器对象，便于后续取消
        timers[task_id] = timer

        # 启动定时器
        timer.start()


def stop_scheduler():
    """
    停止所有定时任务，取消所有活跃的定时器
    """
    for task_id, timer in timers.items():
        # 取消定时器
        if timer is not None:
            timer.cancel()

    # 清空字典
    timers.clear()

