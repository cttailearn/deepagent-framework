# deepagent-framework

基于 [deepagents](https://pypi.org/project/deepagents/) 的最小可用框架：提供一个通用助手 Agent，支持在工作区执行命令、管理后台会话，并可通过 skills 目录扩展能力。

## 环境要求

- Python >= 3.13
- 推荐使用 [uv](https://github.com/astral-sh/uv) 管理依赖（本项目包含 `uv.lock`）

## 安装依赖

使用 uv：

```bash
uv sync
```

## 配置

在项目根目录创建 `.env`（或以环境变量方式注入）：

```ini
OPENAI_API_KEY=你的_key
OPENAI_API_MODEL=你的_model

# 可选：兼容 OpenAI 协议的 API Base（如自建网关/第三方平台）
OPENAI_API_BASE=https://api.openai.com/v1
```

## 运行

最简单的方式：

```bash
uv run python main.py "你好，介绍一下这个项目怎么用"
```

从 stdin 读取：

```bash
echo "帮我总结一下当前目录结构" | uv run python main.py
```

禁用流式输出：

```bash
uv run python main.py "输出一段 JSON" --no-stream
```

指定会话 thread_id（用于 MemorySaver 做会话隔离）：

```bash
uv run python main.py "继续刚才的话题" --thread-id demo
```

指定 backend 根目录（工具执行命令时的工作目录）：

```bash
uv run python main.py "列出当前目录文件" --backend-root D:\path\to\workspace
```

## 目录结构

- `main.py`：CLI 入口，支持流式/非流式输出
- `agents/agent.py`：构建 Agent（模型、工具、skills、backend）
- `agents/tools.py`：工具实现
- `agents/skills/`：扩展技能目录（可按 deepagents 的 skills 机制添加）

## 内置工具

Agent 内置 3 个工具（在 `agents/tools.py` 定义）：

- `get_system_time(utc=false)`：获取当前系统时间（带时区的 ISO 8601）
- `exec(...)`：在工作区执行命令，可转后台运行并返回 `sessionId`
- `process(...)`：管理后台会话（list/poll/log/write/kill/clear/remove）

## 权限与安全开关（可选）

为降低误操作风险，工具支持通过环境变量控制“提权执行”：

```ini
DEEPAGENT_TOOLS_ELEVATED=1
DEEPAGENT_AGENT_ELEVATED=1
```

同时设置以上两个变量后，`exec(..., elevated=true)` 才会被允许。
