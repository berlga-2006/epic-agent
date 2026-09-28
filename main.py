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
load_dotenv()


async def main():
    async with MCPAdapter("https://docs.langchain.com/mcp") as adapter:
        mcp_tools = await adapter.list_tools()

    console = Console()

    SYSTEM_PROMPT = """
    You are my personal ai assistant.
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
    asyncio.run(main())