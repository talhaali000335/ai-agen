from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
import os

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

class AgentState(TypedDict):
    question: str
    context: Optional[str]
    answer: Optional[str]

def retrieve(state):
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    docs = vectorstore.similarity_search(state["question"], k=3)
    context = "\n\n".join([d.page_content for d in docs])
    return {"context": context}

def generate(state):
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="qwen/qwen3.6-27b", temperature=0.7)
    messages = [
        HumanMessage(content=f"Context:\n{state['context']}\n\nQuestion: {state['question']}")
    ]
    response = llm.invoke(messages)
    return {"answer": response.content}

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()

app_graph = build_graph()