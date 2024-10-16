from config import timer_task_config, task_config, SERVER_TOKEN
from utils import *
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from models import *
import uuid
from typing import Optional


router = APIRouter()


async def token_required(x_server_token: str = Header(...)):
    """Token 验证依赖"""
    if x_server_token != SERVER_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized, invalid token")


@router.get("/get", response_model=StandardResponseModel, dependencies=[Depends(token_required)])
async def get_commands(x_client_id: Optional[str] = Header(None, description="客户端id")):
    """
    获取任务中的指令，返回第一个处于 READY 状态的任务
    """
    task_id = None
    task_list = task_manager.list_tasks()

    for tid in task_list:
        task = task_manager.get_task(tid)
        if task:
            task_client_id = task.get("client_id")
            if task["status"] == READY and (not task_client_id or not x_client_id or task_client_id == x_client_id):
                task_id = tid
                break

    if task_id:
        task = task_manager.get_task(task_id)
        commands = task.get("commands", [])
        task_manager.update_task(task_id, status=PENDING)  # 设置任务为PENDING状态
        return {"code": 200, "message": f"Commands for task {task_id} fetched successfully", "data": {"taskId": task_id, "commands": commands}}
    else:
        return {"code": 200, "message": "No ready commands available", "data": None}


@router.post("/report", response_model=StandardResponseModel, dependencies=[Depends(token_required)],)
async def receive_report(command_result: CommandResultModel):
    """
    接收客户端的任务执行后的结果
    """
    task_id = command_result.task_id
    results = command_result.results

    if not task_manager.task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    if task_id in timer_task_config:
        callback = timer_task_config.get(task_id).get("callback")
        callback(results)

    task_manager.update_task(task_id, status=COMPLETED, results=results)
    return {"code": 200, "message": f"Task {task_id} result received", "data": {"taskId": task_id}}


@router.post("/add", response_model=StandardResponseModel, dependencies=[Depends(token_required)])
async def add_command(data: AddCommandModel):
    """新建任务，可自定义taskId，否则返回随机taskId"""
    task_id = data.task_id or str(uuid.uuid4())
    new_commands = data.commands
    client_id = data.client_id

    if not new_commands or not isinstance(new_commands, list) or len(new_commands) == 0:
        return {"code": 400, "message": "No commands provided or invalid format", "data": None}

    task_manager.add_task(task_id, client_id, new_commands, READY)
    return {"code": 200, "message": f"Task added with {len(new_commands)} command(s)", "data": {"taskId": task_id}}


@router.get("/status", response_model=StandardResponseModel, dependencies=[Depends(token_required)])
async def get_task_status(task_id: str = Query(..., description="任务id")):
    """
    获取指定task_id的任务状态
    """
    task = task_manager.get_task(task_id)
    if not task:
        return {"code": 404, "message": "Task not found", "data": None}

    status = task.get("status")
    if status == COMPLETED:
        if task_id not in timer_task_config and task_id not in task_config:
            task_manager.remove_task(task_id)
    return {
        "code": 200,
        "message": "Task is still in progress",
        "data": {
            "taskId": task_id,
            "status": status,
            "result": task.get("results", None),
            "created_time": task.get("created_time"),
            "pending_time": task.get("pending_time"),
            "completed_time": task.get("completed_time"),
        },
    }


@router.post("/task", response_model=StandardResponseModel, dependencies=[Depends(token_required)])
async def add_task_by_name(data: AddTaskByNameModel):
    """
    以任务的形式添加命令组，任务需要在配置文件中设置
    """
    task_id = data.task_id
    client_id = data.client_id

    # 从 task_config 中查找相应的任务
    task_config_entry = task_config.get(task_id)
    if not task_config_entry:
        return {"code": 404, "message": f"Task config not found for task name: {task_id}", "data": None}

    commands = task_config_entry.get("commands", [])

    if not commands:
        return {"code": 400, "message": f"No commands found for task name: {task_id}", "data": None}

    # 将任务加入任务管理器
    task_manager.add_task(task_id, client_id, commands, READY)

    return {"code": 200, "message": f"Task '{task_id}' added with {len(commands)} command(s)", "data": {"taskId": task_id}}
