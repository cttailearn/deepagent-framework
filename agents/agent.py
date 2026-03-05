import os
from pathlib import Path
try:
    from .tools import build_tools
except Exception:
    from tools import build_tools
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

skills_dir = os.path.join(os.path.dirname(__file__), "skills")



research_instructions = """
你是一个助手。只有当用户明确需要时间、日期或时间戳时，才调用工具。
如果不需要工具，直接用自然语言回答。

## `get_system_time`

获取当前系统时间，返回带时区的 ISO 8601 字符串。
参数：
- utc: 是否返回 UTC 时间（默认 false，返回本地时区时间）

## `exec`

在工作区执行 shell 命令。


## `process`
管理后台执行会话。

"""

def build_agent(backend_root: str | None = None):
    from langchain.chat_models import init_chat_model

    model = init_chat_model(
        model=os.getenv("OPENAI_API_MODEL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_API_BASE"),
        temperature=0.7,
        max_retries=3,
        timeout=60,
    )

    default_root = str(Path(__file__).resolve().parents[1])
    root_dir = backend_root or default_root
    os.environ["DEEPAGENT_BACKEND_ROOT"] = root_dir

    return create_deep_agent(
        backend=FilesystemBackend(root_dir=root_dir, virtual_mode=True),
        skills=[skills_dir] if os.path.exists(skills_dir) else [],
        tools=build_tools(),
        model=model,
        system_prompt=research_instructions,
        checkpointer=MemorySaver(),
        
    )


if __name__ == "__main__":
    agent = build_agent()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "你可以执行命令吗？可以的话查看一下当前运行的系统"}]},
        config={"recursion_limit": 64, "configurable": {"thread_id": "default"}},
    )
    print(result["messages"][-1].content)
