from dotenv import load_dotenv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_classic.agents import (
    initialize_agent,
    AgentType
)

from langchain_classic.memory import (
    ConversationBufferMemory
)

from tool import (
    get_balance,
    get_allowance,
    transfer_from,
    predict_property_price,
    recommend_property,
    analyze_location
)

# Gemini 3.1 Flash Lite
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

tools = [
    get_balance,
    get_allowance,
    transfer_from,
    predict_property_price,
    recommend_property,
    analyze_location
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
)

print("\nAntier's housing price prediction agent ready")
print("Type exit to quit")

while True:

    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    try:
        response = agent.invoke({
            "input": user_input
        })

        print("\nAssistant:")
        print(response["output"])

    except Exception as e:

        print(f"\nError: {e}")