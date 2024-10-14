FROM python:3.10-slim

RUN apt-get install ca-certificates

# 拷贝当前项目到/app目录下（.dockerignore中文件除外）
COPY server /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple \
&& pip config set global.trusted-host mirrors.aliyun.com \
&& pip install --upgrade pip \
&& pip install -r requirements.txt --no-warn-script-location

# 验证版本
RUN python3 -V

EXPOSE 1030

# 执行启动命令
CMD python3 run.py
#CMD ["python3", "-m", "uvicorn", "run:app", "--host", "0.0.0.0", "--port ", "80"]

