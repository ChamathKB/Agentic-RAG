from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.pydantic_v1 import BaseModel, Field
from langchain import hub

import mlflow

from app.tools.test_tools import WeaApiTool
from app.tools.tools import content_retriever
from app.db.vector_store import VectorStore
from app.models.schema import Query
from app.configs import OPENAI_MODEL, OPENAI_API_KEY

from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

mlflow.set_experiment("Agentic-RAG")
mlflow.langchain.autolog(
    log_models=True,
    log_input_examples=True,
    log_model_signatures=True,
)

llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0,
    openai_api_key=OPENAI_API_KEY,
    max_tokens=100,
    verbose=True,
)


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """Chat message history Implementation."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

store = {}

def get_session_history(sender_id: str) -> BaseChatMessageHistory:
    if sender_id not in store:
        store[sender_id] = InMemoryHistory()
    return store[sender_id]


def ask_agent(query: Query, sender_id: str, collection_name: str) -> str:

    qdrant_vectorstore = VectorStore(collection_name)
    retriever_tool = qdrant_vectorstore.content_retriever_tool()

    tools = [WeaApiTool(), retriever_tool]

    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant"),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

    appraisal_agent = RunnableWithMessageHistory(agent_executor, 
                                                 get_session_history, 
                                                 output_messages_key="Assistant_response", 
                                                 input_messages_key="input",
                                                 history_messages_key="chat_history"
                                                 )

    config = {"configurable": {"session_id": sender_id}}
    agent_response = appraisal_agent.invoke({"input": query}, config=config)
    return agent_response["output"]