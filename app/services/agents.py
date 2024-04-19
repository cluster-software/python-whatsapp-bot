import os

from dotenv import load_dotenv

from langchain.memory import ChatMessageHistory
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

import numpy as np

from app.schemas.catalog import Catalog

load_dotenv()  # Load environment variables from a .env file

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# SYSTEM_MESSAGE = """You are a helpful assistant for the Mexican bakery Prollecto Bullé.
# Your job is to help customers with any requests they might have. Most customers will speak spanish but if they address you in a different language, respond in that language.
# Your ultimate goal is to get the following information from the customer
# 1. What product to they want to order for the bakery
# 2. What quantity of the product do they want
# 3. When are they planning on picking up their order

# Don't be pushy and if they don't directly ask about products, just answer their questions. You should only prompt them for the above information if
# 1. They ask about a product
# 2. The conversation reaches a natural stopping point

# If they customer asks you whether a certain product is in stock right now, say you will need to check and get back to them later. Make sure to still get them to tell you
# 1. which exact products they want
# 2. the quantity they want
# 3. when they want to pick up

# It is important that you DO NOT tell them whether or not the product is actually in stock since you are unable to check that.
# """

SYSTEM_MESSAGE = """You are a helpful assistant for Pixz – A printing shop in Mexico that lets customers print their designs on various items like flyers, medical receipts, mugs and many more products.
Your job is to help customers with any requests they might have. Most customers will speak spanish but if they address you in a different language, respond in that language. 
Your ultimate goal is to get the following information from the customer 
1. What product to they want to order 
2. What quantity of the product do they want 

Don't be pushy and if they don't directly ask about products, just answer their questions. You should only prompt them for the above information if 
1. They ask about a product 
2. The conversation reaches a natural stopping point
"""


class OpenAIChatbot:

    def __init__(
        self,
        openai_model: str,
        chat_history: ChatMessageHistory | None = None,
        tools: list[BaseTool] | None = None,
        catalog: Catalog | None = None,
    ):
        self.chat_model = ChatOpenAI(model=openai_model)
        self.chat_history = (
            chat_history
            if chat_history is not None
            else ChatMessageHistory(messages=[SystemMessage(content=SYSTEM_MESSAGE)])
        )
        self.tools = tools
        if tools is not None:
            self.chat_model = self.chat_model.bind_tools(tools)
        self.catalog = catalog

    def _handle_tool_call(self, model_response: AIMessage):
        tool_calls = model_response.tool_calls
        for call in tool_calls:
            if call["name"] == "product_search":
                # handle product search call
                item_id = call["args"]["item_id"]
                item = self.catalog.get_item_by_id(item_id)
                options = item.options
                all_option_value_lists = [x[1] for x in item.price_map]
                all_option_values = sum(
                    all_option_value_lists, []
                )  # flatten all_option_value_lists
                option_values = [
                    list(
                        set(
                            [
                                option_value.value
                                for option_value in all_option_values
                                if option_value.option_id == option.id
                            ]
                        )
                    )
                    for option in options
                ]
                model_response_content = (
                    "Me podrías indicar lo siguiente para poder hacer la cotización?\n"
                )
                for i, option in enumerate(options):
                    option_values_string = ", ".join(option_values[i])
                    model_response_content += f"{i+1}. {option.name}. Las opciones son: {option_values_string}\n"
                model_response.content = model_response_content
                return
            else:
                pass
                # handle other calls

    def respond_to_user(self, user_input: str):
        # add user input to messages
        self.chat_history.add_user_message(user_input)
        model_response = self.chat_model.invoke(self.chat_history.messages)
        if len(model_response.tool_calls) > 0:
            self._handle_tool_call(model_response)
        else:
            pass
        self.chat_history.add_ai_message(model_response)
        return model_response.content


# bot = OpenAIChatbot(openai_model="gpt-3.5-turbo-0125")

# input1 = "Translate this sentence from English to French: I love programming."
# response1 = bot.respond_to_user(input1)
# print("response1: ", response1)

# input2 = "What did I just ask you"
# response2 = bot.respond_to_user(input2)

# print("response2: ", response2)
