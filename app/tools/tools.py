from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
import os

load_dotenv()

def load_documents(document):
    loader = TextLoader(document)
    docs = loader.load()
    return docs

def split_documents(docs, chunk_size=350, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunked_documents = text_splitter.split_documents(docs)
    return chunked_documents

def create_vectorstore(chunked_documents):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=os.environ['OPENAI_API_KEY'])
    vectorstore = FAISS.from_documents(
        chunked_documents,
        embeddings
    )
    return vectorstore

def content_retriever():

    docs = load_documents("./kb.md")

    chunked_documents = split_documents(docs, chunk_size=350, chunk_overlap=50)

    faiss_vectorstore = create_vectorstore(chunked_documents)

    retriever = faiss_vectorstore.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever,
        name="query_tool",
        description="Use this tool when you need to answer questions about the context provided."
    )

    return retriever_tool