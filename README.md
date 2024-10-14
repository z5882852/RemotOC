
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
- AE2的远程控制：通过实现远程执行合成命令、查看终端内物品等。
- 智能产线：监控产线的使用电量、机器情况等。
- tps监控：用于记录服务器tps情况。

> 当前分支无任何插件，请前往其他分支查看

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
│   ├── setup.lua
│   └── src
│       └── executor.lua
└── server
    ├── app
    │   ├── commands.py
    │   └── __init__.py
    ├── callback.py
    ├── config.py  # 任务配置文件
    ├── .env  # 服务端配置文件
    ├── models.py
    ├── requirements.txt
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
   http://你的主机名/docs
   ```
   - ReDoc 风格的文档
   ```
   http://你的主机名/redoc
   ```

### OC客户端部署

1. 在 OC 客户端安装因特网卡

2. 将客户端代码（`client`目录内容）上传到OC客户端内

3. 运行客户端
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

## 未来计划

- 增加对 WebSocket 的支持，实现更高效的实时双向通信。
- 扩展服务器功能，使其支持更多复杂的数据处理和操作。

## 贡献

欢迎对 RemoteOC 项目进行贡献！请提交 Pull Request 或报告问题，帮助改进项目。提交代码前请确保：
- 代码通过了基本的单元测试。
- 遵循项目的代码风格指南。

