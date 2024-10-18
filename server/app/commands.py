from config import timer_task_config, task_config, SERVER_TOKEN
from utils import *
from fastapi import APIRouter, Depends, HTTPException, Header, Query, Request
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
        is_chunked = task.get("is_chunked", False)  # 获取是否分块的参数，默认为 False
        task_manager.update_task(task_id, status=PENDING)  # 设置任务为PENDING状态
        return {"code": 200, "message": f"Commands for task fetched successfully", "data": {"taskId": task_id, "commands": commands, "is_chunked": is_chunked }}
    else:
        return {"code": 200, "message": "No ready commands available", "data": None}


@router.post("/chunked_report", response_model=StandardResponseModel, dependencies=[Depends(token_required)])
async def receive_chunked_report(request: Request, chunked: int = Query(-1, description="是否为分块上传，1表示开始，0表示结束，>1 表示继续上传")):
    """
    接收客户端的任务执行后的结果, 仅用于分块上传
    """
    try:
        body = await request.body()  # OC返回数据为GBK，直接使用pydantic解析会报400错误
        decoded_body = decode_request_body(body)
        json_data = json.loads(decoded_body)
        command_result = CommandResultModel(**json_data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {str(e)}")
        raise HTTPException(status_code=400, detail="JSON 格式错误")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task_id = command_result.task_id
    results = command_result.results

    if not task_manager.task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    # 如果 chunked == 1，则开始接收分块任务，覆盖已有数据，并将状态设置为 UPLOADING
    if chunked == 1:
        task = task_manager.get_task(task_id)
        if task:
            logger.debug(f"Task {task_id} already exists, resetting task with new data.")
        # 重置任务数据并设置状态为 UPLOADING
        task_manager.update_task(task_id, status=UPLOADING, results=results)
        return {"code": 200, "message": f"Chunked data for task received and reset successfully", "data": {"taskId": task_id}}

    # 如果 chunked > 1，则继续接收分块数据，添加进已有的任务里
    elif chunked > 1:
        task = task_manager.get_task(task_id)
        if task.get("status") != UPLOADING:
            return {"code": 200, "message": f"Task status is not uploading", "data": {"taskId": task_id}}
        if task and "results" in task:
            existing_results = task.get("results", [])
            if isinstance(existing_results, list) and isinstance(results, list):
                existing_results.extend(results)  # 添加到已有的结果里
            task_manager.update_task(task_id, status=UPLOADING, results=existing_results)
            return {"code": 200, "message": f"Chunked data for task added successfully", "data": {"taskId": task_id}}
        else:
            return {"code": 400, "message": f"task results is none", "data": {"taskId": task_id}}

    # 为0时，表示接收完成，合并数据并更新任务状态为 COMPLETED
    elif chunked == 0:
        task = task_manager.get_task(task_id)
        if task and "results" in task:
            existing_results = task.get("results", [])
            if isinstance(existing_results, list) and isinstance(results, list):
                existing_results.extend(results)  # 合并数据
            task_manager.update_task(task_id, status=COMPLETED, results=existing_results)
        else:
            # 没有数据，直接保存结果并完成任务
            task_manager.update_task(task_id, status=COMPLETED, results=results)

        for config in [timer_task_config, task_config]:
            if task_id in config:
                handle = config.get(task_id, {}).get("handle")
                if handle:
                    results = handle(results)
                callback = config.get(task_id, {}).get("callback")
                if callback:
                    callback(results)

        return {"code": 200, "message": f"Task result received and completed", "data": {"taskId": task_id}}

    else:
        raise HTTPException(status_code=400, detail="Invalid value for chunked. Must be 0 or 1 or greater than 1")


@router.post("/report", response_model=StandardResponseModel, dependencies=[Depends(token_required)])
async def receive_report(request: Request):
    """
    接收客户端的任务执行后的结果
    """
    try:
        body = await request.body()  # OC返回数据为GBK，直接使用pydantic解析会报400错误
        decoded_body = decode_request_body(body)
        json_data = json.loads(decoded_body)
        command_result = CommandResultModel(**json_data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {str(e)}")
        raise HTTPException(status_code=400, detail="JSON 格式错误")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task_id = command_result.task_id
    results = command_result.results

    if not task_manager.task_exists(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

    for config in [timer_task_config, task_config]:
        if task_id in config:
            handle = config.get(task_id, {}).get("handle")
            if handle:
                results = handle(results)
            callback = config.get(task_id, {}).get("callback")
            if callback:
                callback(results)

    task_manager.update_task(task_id, status=COMPLETED, results=results)
    return {"code": 200, "message": f"Task result received", "data": {"taskId": task_id}}


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
        return {"code": 404, "message": f"Task config not found for task name: {task_id}", "data": {"taskId": task_id}}

    commands = task_config_entry.get("commands", [])
    if len(commands) != 1:
        return {"code": 400, "message": f"Commands error for task name: {task_id}", "data": {"taskId": task_id}}
    is_chunked = task_config_entry.get("is_chunked", False)

    if not commands:
        return {"code": 400, "message": f"No commands found for task name: {task_id}", "data": {"taskId": task_id}}

    # 将任务加入任务管理器
    if task_config_entry.get('cache', False):
        if not task_manager.update_task(task_id, status=READY):
            # 没有任务则创建新任务
            task_manager.add_task(task_id, client_id, commands, READY, is_chunked=is_chunked)
    else:
        task_manager.add_task(task_id, client_id, commands, READY, is_chunked=is_chunked)

    return {"code": 200, "message": f"Task added with {len(commands)} command(s)", "data": {"taskId": task_id}}
