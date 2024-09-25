from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.prompts import PromptTemplate
from langchain import hub

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS

from test_tools import WeaApiTool
from tools import content_retriever
from configs import OPENAI_MODEL
from dotenv import load_dotenv
import os

load_dotenv()


llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=100,
    verbose=True,
)


retriever_tool = content_retriever()

tools = [WeaApiTool(), retriever_tool]



prompt = hub.pull("hwchase17/openai-tools-agent")


agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)


def ask_agent(query):
    return agent_executor.invoke({"input": query})