from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv()

def check_inventory(item: str, color: str) -> str:
    """This tool checks current stock.

    Parameters:
      item - The item that the user wants to know the status of
      color - the color of the item"""
    fake_stock = {
        ("hoodie", "blue"): 4,
        ("hoodie", "black"): 12,
        ("t-shirt", "blue"): 30,
    }

    if (item.lower(), color.lower()) in fake_stock:
        return "We're in stock!"
    else:
        return "We're out of stock..."

def main():

    SYSTEM_PROMPT = """
    ACME Clothing is literally the best retail clothing supplier.
    Our motto: Buy now, never regret.

    We supply all your clothing needs:
    - Hoodies
    - T-Shirts

    Capabilities:
    - check_inventory: use this function whenever you need to look up stock to see if we have a given item.

    All you could ever hope for.
    """

    model = init_chat_model(
        "google_genai:gemini-flash-lite-latest",
    )

    agent = create_agent(
        model=model,
        tools=[check_inventory],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )

    thread_config = {"configurable": {"thread_id": str(uuid4())}}
    while True:
        try:
            prompt = input("Input: ")
            if prompt == "exit": break
            response = agent.invoke(
                {"messages": [HumanMessage(prompt)]},
                thread_config,
            )
        except EOFError:
            break
        print(response["messages"][-1].text)

if __name__ == "__main__":
    main()