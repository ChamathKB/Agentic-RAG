from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

import mlflow

from app.tools.tavily_search import search
from app.tools.weather_tool import WeatherTool
from app.db.vector_store import VectorStore
from app.models.schema import Query
from app.configs import OPENAI_MODEL, OPENAI_API_KEY


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


store = {}

def get_session_history(sender_id: str) -> BaseChatMessageHistory:
    """
    Get or create a chat message history for a given sender ID.
    
    Args:
        sender_id (str): Unique identifier for the chat session/sender
        
    Returns:
        BaseChatMessageHistory: Chat message history object for the sender
        
    Description:
        Retrieves existing chat history from store if it exists for the sender_id,
        otherwise creates a new ChatMessageHistory and stores it before returning.
    """
    if sender_id not in store:
        store[sender_id] = ChatMessageHistory()
    return store[sender_id]


def ask_agent(query: Query, sender_id: str, collection_name: str) -> str:
    """
    Creates and executes an agent with tools and chat history to process user queries.
    
    Args:
        query (Query): The user's input query to be processed
        sender_id (str): Unique identifier for the chat session/sender
        collection_name (str): Name of the vector store collection to use
        
    Returns:
        str: The agent's response to the query
        
    Description:
        1. Initializes vector store and tools (retriever, search, weather)
        2. Creates a chat prompt template with system message and placeholders
        3. Creates a tool-calling agent with the tools and prompt
        4. Wraps the agent executor with message history functionality
        5. Executes the agent with the query and returns the response
    """

    qdrant_vectorstore = VectorStore(collection_name)
    retriever_tool = qdrant_vectorstore.content_retriever_tool()

    search_tool = search()

    tools = [WeatherTool(), retriever_tool, search_tool]

    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant"),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

    appraisal_agent = RunnableWithMessageHistory(agent_executor, 
                                                 get_session_history, 
                                                 input_messages_key="input",
                                                 history_messages_key="chat_history"
                                                 )

    config = {"configurable": {"session_id": sender_id}}
    agent_response = appraisal_agent.invoke({"input": query}, config=config)
    return agent_response["output"]
