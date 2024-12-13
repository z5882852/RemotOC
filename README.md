
<p align="center">
  <img src="assets/oc.png" width="200" height="200" alt="oc"></a>
</p>

<h1 align="center" style="font-size: 38px;">RemoteOC</h1>

<p align="center">
  <a href="LICENSE">
    <img alt="GitHub License" src="https://img.shields.io/github/license/z5882852/RemoteOC">
  </a>
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=edb641" alt="python">
  <img src="https://img.shields.io/badge/OpenComputers-1.10.11 GTNH-blue.svg">
  <br/>
  <img src="https://img.shields.io/github/stars/z5882852/RemoteOC">
  <img src="https://img.shields.io/github/forks/z5882852/RemoteOC">
  <img src="https://img.shields.io/github/watchers/z5882852/RemoteOC">
</p>


## 项目介绍

**RemoteOC** 项目基于 Minecraft 的 `OpenComputers` 模组（以下简称`OC`）和 `Python3`，旨在实现 Minecraft 游戏内的 OpenComputers 客户端与外部服务器的交互功能。通过该项目，可以在游戏中使用 OC 与外部服务器进行数据通信，支持的功能包括数据查询、数据处理和远程操作等。

基于该项目可开发插件:
- [AE2的远程控制](https://github.com/z5882852/RemoteOC-GTNH-AE2)：通过实现远程执行合成命令、查看终端内物品等。
- 智能产线：监控产线的使用电量、机器情况等。
- tps监控：用于记录服务器tps情况。

> 当前仓库无任何插件，请前往其他仓库查看

**注意： 该项目的服务端需要一台可公网访问且端口开放的主机（云服务器、内网穿透、申请公网等）或是一些云托管服务。**

### 功能

- **远程操作**：支持在服务端执行远程代码控制 OC。
- **可扩展性**：项目支持自定义扩展插件，可根据需求添加更多的交互功能。

### 原理

OC客户端通过轮询服务器接口获取命令，当获取到命令并执行后将执行结果报告给服务器。

### 开发环境

- **GT: New Horizons**: 2.6.0
- **OpenComputers**: 1.10.11-GTNH
- **Lua**: 5.3
- **Python**: 3.10.10

## 安装步骤

**目录结构**
```tree
RemoteOC
├── Dockerfile  # docker配置文件
├── .dockerignore
├── .gitignore
├── README.md
├── client
│   ├── env.lua  # OC客户端配置文件
│   ├── lib
│   │   ├── json.lua
│   │   └── logger.lua
│   ├── plugins  # 插件目录
│   │   └── echo.lua
│   ├── run.lua  # 启动文件
│   ├── setup.lua  # 安装程序
│   └── src
│       └── executor.lua  # 执行和上报程序
└── server
    ├── app
    │   ├── commands.py
    │   └── __init__.py
    ├── callback.py
    ├── config.py  # 任务配置文件
    ├── .env  # 服务端配置文件
    ├── models.py
    ├── requirements.txt  # 依赖文件
    ├── run.py
    ├── scheduler.py
    └── utils.py
```

### 服务端部署

1. **安装 Python**:
   - 下载并安装 Python3，推荐安装Python3.10版本以上。

2. **源码部署**:
   - 克隆项目代码：
     ```bash
     git clone https://github.com/z5882852/RemoteOC.git
     ```
     > 或直接下载代码
   - 进入服务端目录:
     ```bash
     cd RemoteOC/server
     ```
   - 安装依赖：
     ```bash
     pip install -r requirements.txt
     ```
     使用镜像源安装
     ```bash
     pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
     ```
   - 修改`.env`文件中的token
   - 启动 Python 服务器：
     ```bash
     python server.py
     ```
   - 指定主机或端口启动：
     ```bash
     python server.py --port 8888 --host 0.0.0.0
     ```
3. **docker部署**
   - 修改`.env`文件中的token
   - 编译docker镜像文件：
     ```bash
     docker build -t roc .
     ```
   - 创建并启动容器:
     ```bash
      docker run -d --name roc -p 1030:1030 roc
     ```

4. **查看API文档**
   - Swagger UI 风格的文档
   ```
   http://你的主机名:端口/docs
   ```
   - ReDoc 风格的文档
   ```
   http://你的主机名:端口/redoc
   ```

### OC客户端部署

1. **准备工作**
   - 组装好 OC 电脑（T2以上即可，内存越大越好）
   - 安装 OpenOS 操作系统
   - 安装因特网卡
2. **安装程序安装**
   - 下载安装程序
    ```bash
    wget https://raw.githubusercontent.com/z5882852/RemoteOC/main/client/setup.lua
    ```

   - 安装客户端
    ```bash
    setup.lua
    ```

3. **直接安装(当raw.githubusercontent.com无法访问时)**
   - 下载项目
  
   - 将`client`目录所有文件上传至你的 OC 客户端

4. **将`env.lua`中的`baseUrl`修改为你的后端地址**

5. **运行客户端**
   ```bash
   run.lua
   ```
   DEBUG模式运行
   ```bash
   run.lua --debug
   ```
## 常见问题

1. **无法连接服务器**：
   - 检查服务器 IP 和端口是否正确，确保防火墙未阻止连接。
   
2. **OpenComputers 无法发送请求**：
   - 确保 OC 客户端已安装因特网卡（internetCard）。

3. **外部服务器返回错误**：
   - 检查 Python 服务器日志，确保所有依赖库已正确安装。


## 开发文档

### **任务状态**
- **`READY`**: 任务已准备好，等待客户端获取。
- **`PENDING`**: 任务正在进行中，客户端已获取该任务并执行相关命令。
- **`UPLOADING`**: 任务正在进行中，客户端正在分块报告数据（仅分块上传存在该状态）。
- **`COMPLETED`**: 任务已完成，结果已被上报。

### **任务生命周期记录**
每个任务都记录以下时间：
- **`created_time`**: 任务创建时间。
- **`pending_time`**: 任务状态变为 `PENDING` 的时间。
- **`completed_time`**: 任务完成的时间。

这些时间信息会在任务的相关 API 中返回，帮助跟踪任务的整个生命周期。


### **任务配置 (`task_config`)**

任务配置是一个字典结构，用于定义不同任务的执行方式、命令列表和相关回调处理逻辑。以下是 `task_config` 的基本结构：

```python
task_config = {
    "task_id": {  # 键名为任务名，用于发起任务
        'client_id': 'client_01',  # 指定执行命令的客户端ID
        'commands': [  # 远程执行的命令列表
            "your_command",
        ],
        'cache': False,  # 是否缓存数据，如果为True，则任务执行后不会清空上次执行的数据
        'handle': None,  # 命令执行后的处理函数，格式为 handle(results: list)，用于处理执行结果
        'callback': None,  # 命令执行后的回调函数，格式为 callback(results: list)，可选
        'chunked': False  # 是否启用分块上传，True 表示启用，False 表示不启用（启用后commands只能为有1条命令，且上报数据是一个列表，后端将会把上报的列表合并）
    },
}
```

- **`client_id`**：用于指定任务发往的客户端ID。
- **`commands`**：一个字符串列表，包含远程执行的命令。
- **`cache`**：如果设为 `True`，则任务完成后不会清空上次的执行结果，可以缓存数据。
- **`handle`**：一个可选的函数，用于上报过程中处理任务结果。
- **`callback`**：一个可选的回调函数，当任务完成时调用。
- **`chunked`**：指定任务是否启用分块上传。

### **分块上传**
当`task_config`中`chunked`为`true`时启用。

当您启用分块上传时，OC客户端不会上报您的执行结果，需要您在OC插件中对于需要上传的数据调用`src/executor.lua`的`reportSingleChunk`，并且需要自行传入`taskId`。

由于拓展性低和使用性复杂，因此我并不倡议使用分块上传，除非您需要上报的数据非常大或者电脑内存很小。



### **日志管理**
日志级别由环境变量 `LOG_LEVEL` 控制，可选值为 `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`。
日志会记录每个 API 请求的处理过程及任务状态的更新。


### **插件开发**
每个插件应遵循以下基本结构：
1. **命名**: 插件文件以 `.lua` 结尾，文件名应有意义，例如 `echo.lua`。
2. **函数声明**: 插件内的所有函数都应按照 Lua 语言的标准进行声明。所有需要调用的函数应对外公开（即未使用 `local` 关键字）。
3. **参数处理**: 函数接收参数时可以根据需要进行处理，例如字符串、数字或表（Lua 的数组/字典）。
4. **返回值**: 当插件中的函数被调用时，函数的返回值将会以字符串的形式上报给服务器。
5. **错误处理**: 当报错时，会上报错误的堆栈信息，例如{ message = "Error: xxx" }。


**示例插件代码 (`echo.lua`)**:
```lua
-- 定义一个简单的回显函数
function echo(str)
    return str
end
```

### **插件加载**
插件文件放置在指定的插件目录`plugins/` 中。

在主程序中可以通过 Lua 的 `require` 来自动加载插件。

加载后，插件中的函数将会被注册，可以在主程序中直接调用该函数。

### **命令调用插件中的函数**

为了调用插件中的函数，系统可以通过解析命令内容，动态执行 Lua 函数。命令格式通常为:

`"return <function_name>(<arguments>)"` 

系统会解析命令字符串并执行。

服务器返回的是命令组的形式，客户端将遍历命令组并依次执行
```json
[
    "return <function_name_1>(<arguments>)",
    "return <function_name_2>(<arguments>)",
]
```

**示例**:
要调用 `echo` 函数并传递参数 `Hello, World!`，命令可以写成：
```json
["return echo('Hello, World!')"]
```


## 未来计划

- 增加对 WebSocket 的支持，实现更高效的实时双向通信。
- 扩展服务器功能，使其支持更多复杂的数据处理和操作。

## 贡献

欢迎对 RemoteOC 项目进行贡献！请提交 Pull Request 或报告问题，帮助改进项目。提交代码前请确保：
- 代码通过了基本的单元测试。
- 遵循项目的代码风格指南。

如果你需要帮助或提供建议，请发送邮件至`z5882852@qq.com`，或直接加我QQ：1024902835