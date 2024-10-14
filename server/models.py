from pydantic import BaseModel, Field
from typing import List, Optional, Any

# 定义标准化响应模型
class StandardResponseModel(BaseModel):
    code: int = Field(..., description="状态码，200 表示成功")
    message: str = Field(..., description="返回的状态信息，用于描述操作结果")
    data: Optional[Any] = Field(None, description="包含具体返回数据的字段，根据不同接口内容不同")

# 定义命令执行结果的模型
class CommandResultModel(BaseModel):
    taskId: str = Field(..., description="任务的唯一标识符")
    results: List[str] = Field(..., description="任务执行的结果，通常是输出的文本或数据")

# 定义添加命令的请求模型
class AddCommandModel(BaseModel):
    task_id: Optional[str] = Field(None, description="任务的唯一标识符，如果未提供，则系统会生成新的 UUID")
    commands: List[str] = Field(..., description="要执行的命令列表，多个命令可以并行执行")
    client_id: Optional[str] = Field(None, description="客户端 ID，用于标识发出请求的客户端（可选）")

# 定义任务状态响应模型
class TaskStatusResponseModel(BaseModel):
    taskId: str = Field(..., description="任务的唯一标识符")
    status: str = Field(..., description="当前任务的状态（例如 READY、PENDING 或 COMPLETED）")
    results: List[str] = Field(None, description="如果任务已完成，此字段包含任务执行的结果")

# 定义根据任务名添加任务的请求模型
class AddTaskByNameModel(BaseModel):
    task_name: str = Field(..., description="任务的名称，用于从 `task_config` 中查找对应的任务配置")
    client_id: Optional[str] = Field(None, description="客户端 ID，标识发起请求的客户端（可选）")

# 定义添加任务的响应模型
class AddTaskResponseModel(BaseModel):
    taskId: str = Field(..., description="任务的唯一标识符，成功添加任务后由系统生成")
    message: str = Field(..., description="任务添加成功后的确认消息，通常描述任务名和命令数")
