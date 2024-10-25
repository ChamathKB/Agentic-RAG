from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import PromptTemplate
from langchain import hub

import mlflow

from app.tools.test_tools import WeaApiTool
from app.tools.tools import content_retriever
from app.db.vector_store import VectorStore
from app.configs import OPENAI_MODEL

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
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=100,
    verbose=True,
)

def ask_agent(query, collection_name):

    qdrant_vectorstore = VectorStore(collection_name)
    retriever_tool = qdrant_vectorstore.content_retriever_tool()

    tools = [WeaApiTool(), retriever_tool]



    prompt = hub.pull("hwchase17/openai-tools-agent")


    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

    agent_response = agent_executor.invoke({"input": query})
    return agent_response["output"]