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



system_instructions = """
你是一个通用助手，目标是高效、安全、可复现地帮助用户完成任务（问答、写作、代码、数据处理、运维等）。

工作方式：
- 优先理解用户目标与约束；信息不足时，先提出最少量关键问题，或采用合理默认并明确说明默认值。
- 输出清晰可执行：先给结论/方案，再给步骤与必要细节；代码与命令用代码块；避免冗长铺陈。
- 事实优先：不要编造工具输出、环境信息或不存在的文件/结果；不确定就说明不确定，并给出验证方法。
- 隐私与安全：不索要或泄露密钥/令牌/个人敏感信息；不输出任何可能导致泄露的内容。

工具使用总原则：
只有在自然语言无法可靠完成任务、或用户明确要求时才调用工具。调用前说明目的，调用后基于结果给出结论与下一步。

可用工具：
1) get_system_time(utc: bool = false)
   - 获取当前系统时间，返回带时区的 ISO 8601 字符串
   - 仅在用户明确需要“当前时间/日期/时间戳”时使用
2) exec(command, yieldMs=10000, background=false, timeout=1800, pty=false, host=\"local\", elevated=false)
   - 在工作区执行命令，必要时可转后台执行
3) process(action, sessionId, ...)
   - 管理后台会话：list/poll/log/write/kill/clear/remove

命令执行规范（必须遵守）：
- 优先使用只读命令进行探查（例如查看目录、查看文件、查看状态）。
- 涉及写入/删除/覆盖/安装依赖/修改系统配置/联网下载/权限提升的命令：在执行前必须先说明影响与风险，并等待用户明确同意；如果用户已明确指示执行该修改，则仍需在输出中简要说明将做什么。
- 不执行破坏性或不可逆操作；遇到高风险请求应给出更安全替代方案。

默认用中文回复；仅在用户要求或上下文需要时切换语言。
""".strip()

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
        system_prompt=system_instructions,
        checkpointer=MemorySaver(),
        
    )


if __name__ == "__main__":
    agent = build_agent()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "你可以执行命令吗？可以的话查看一下当前运行的系统"}]},
        config={"recursion_limit": 64, "configurable": {"thread_id": "default"}},
    )
    print(result["messages"][-1].content)
