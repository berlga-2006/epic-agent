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
import os

import logging
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("langchain_google_genai._function_utils").setLevel(logging.ERROR)
logging.disable(logging.WARNING)

import warnings
from langchain_core._api import LangChainBetaWarning
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

load_dotenv()

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
                    "npx",
                    "-y", 
                    "@modelcontextprotocol/server-filesystem",
                    "C:\\Users\\berlg\\Documents\\University\\Fall-2026\\ai-engineering\\epic-agent\\src\\epic_agent\\excel_files",
                    "C:\\Users\\berlg\\Documents\\University\\Fall-2026\\ai-engineering\\ai-file-storage"
                ]
            },
            "mcp-excel-stdio": {
                "command": "C:/Users/berlg/Documents/University/Fall-2026/ai-engineering/mcp_excel_server/.venv/Scripts/python.exe",
                "args": ["C:\\Users\\berlg\\Documents\\University\\Fall-2026\\ai-engineering\\mcp_excel_server\\src\\mcp_excel_server\\__main__.py", "stdio"],
                "env": {
                    **os.environ,
                    "PYTHONPATH": "src",
                }
            }
        }
    }

    async with MCPAdapter(config) as adapter:
        mcp_tools = await adapter.list_tools()

    console = Console()

    SYSTEM_PROMPT = """
    You are my personal ai assistant, I want you to help me plan my meals for two week periods, starting with the next monday. You can save previous information, such as meals
    that I've eaten, when I like to cook them (for breakfast lunch or dinner), and how long the leftovers last. Any relevant personal information you
    can save in a .txt file named food-info, in your ai-file-storage folder. At the beginning of each conversation load all the info you have from this file.

    The user can type 'exit' to finish their conversation.
`
    You have the ability to copy and modify excel spreadsheets.

    After you have made a two week meal plan, ask the user if it's okay. If it is approved, copy the meal-plan-template file in your excel_files folder, and put the new file in the ai-file-storage folder.
    Then, working in your new copied file, add the date to each day in the calendar, replacing the *date* text. Then, put in all the different meals replacing the *meal* text. Each day will have the meals
    spread across three cells vertically, breakfast, lunch, or dinner. You don't need to create any new cells or modify the styling of the cells. Just change the text in the correct cells, which are
    any cell where the text has a * symbol around the text.
    You can make meal suggestions, but don't put any of those suggestions in the calendar without asking first.
    """

    model = init_chat_model(
        "google_genai:gemini-flash-lite-latest",
        temperature=0.2,
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