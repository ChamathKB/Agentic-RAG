from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.prompts import PromptTemplate
from langchain import hub

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS

from test_tools import WeaApiTool
from dotenv import load_dotenv
import os

load_dotenv()


llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=100,
    verbose=True,
)

loader = TextLoader("./kb.md")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=350, chunk_overlap=50
)

chunked_documents = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small",openai_api_key=os.environ['OPENAI_API_KEY'])

faiss_vectorstore = FAISS.from_documents(
    chunked_documents,
    embeddings
)


retriever = faiss_vectorstore.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    name="query_tool",
    description="Use this tool when you need to answer questions about the context provided."
)

tools = [WeaApiTool(), retriever_tool]



prompt = hub.pull("hwchase17/openai-tools-agent")


agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

# user="What is the weather like right now in NewYork"
user="What is pet policy?"
print(agent_executor.invoke({"input": user}))