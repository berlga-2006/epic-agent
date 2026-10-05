from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from rich.console import Console
from rich.markdown import Markdown
from uuid import uuid4
from dotenv import load_dotenv
from langchain.mcp import MCPAdapter
import asyncio
import warnings
load_dotenv()
warnings.filterwarnings("ignore", message=".*Key '.*' is not supported in schema.*")

def main():
    asyncio.run(_main())

async def _main():
    config = {
        "mcpServers": {
            "docs-langchain": {
            "url": "https://docs.langchain.com/mcp"
            },
            "reference-langchain": {
            "url": "https://reference.langchain.com/mcp"
            },
            "files": {
            "command": "cmd.exe", 
            "args": [
                "/c",
                "npx"
                "-y", 
                "@modelcontextprotocol/server-filesystem",
                "C:\\Users\\berlg\\Desktop",
                "C:\\Users\\berlg\\Documents\\University\\Fall-2026\\ai-engineering\\ai-file-storage"
            ]
            },
        }
    }

    async with MCPAdapter(config) as adapter:
        mcp_tools = await adapter.list_tools()

    console = Console()

    SYSTEM_PROMPT = """
    You are my personal ai assistant.

    The user can type 'exit' to finish their conversation.
    """

    model = init_chat_model(
        "google_genai:gemini-flash-lite-latest",
    )

    agent = create_agent(
        model=model,
        tools=mcp_tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )

    thread_config = {"configurable": {"thread_id": str(uuid4())}}
    while True:
        try:
            prompt = input("Input: ")
            if prompt == "exit": break
            response = await agent.ainvoke(
                {"messages": [HumanMessage(prompt)]},
                thread_config,
            )
        except EOFError:
            break
        console.print(Markdown(response["messages"][-1].text))

if __name__ == "__main__":
    main()