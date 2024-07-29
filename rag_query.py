import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from get_embedding_function import get_embedding_function
import time
import json
import os
from datetime import datetime, timedelta

# CHROMA_PATH = r"E:\Abdullah\Pycharm Projects\Conversation Bot Llama\chroma"
# MEMORY_FILE = "chat_memory.json"
# MEMORY_DURATION_DAYS = 3

# PROMPT_TEMPLATE = """
# Answer the question based only on the following context:
#
# {context}
#
# ---
#
# Answer the question based on the above context: {question}
# """
#
#
# def main():
#     # Create CLI.
#     parser = argparse.ArgumentParser()
#     parser.add_argument("query_text", type=str, help="The query text.")
#     args = parser.parse_args()
#     query_text = args.query_text
#     query_rag(query_text)
#
#
# def query_rag(query_text: str):
#     # Prepare the DB.
#     embedding_function = get_embedding_function()
#     db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
#
#     # Search the DB.
#     results = db.similarity_search_with_score(query_text, k=5)
#
#     context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
#     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#     prompt = prompt_template.format(context=context_text, question=query_text)
#     # print(prompt)
#
#     model = Ollama(model="llama3.1")
#     response_text = model.invoke(prompt)
#
#     sources = [doc.metadata.get("id", None) for doc, _score in results]
#     formatted_response = f"Response: {response_text}" # \nSources: {sources}
#     print(formatted_response)
#     return response_text
#
#
# if __name__ == "__main__":
#     main()

import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from get_embedding_function import get_embedding_function
import time
import json
import os
from datetime import datetime, timedelta

CHROMA_PATH = r"E:\Abdullah\Pycharm Projects\Conversation Bot Llama\chroma"
MEMORY_FILE = "chat_memory.json"
MEMORY_DURATION_DAYS = 3
PROMPT_TEMPLATE = """
You are an AI assistant. Use the following context to answer the question. If the context does not contain the information needed, use your pre-trained knowledge to provide a comprehensive answer.

Context:
{context}

---

Question: {question}

Answer:
"""

CASUAL_CONVERSATIONS = {
    "hello": "Hello! How can I help you today?",
    "hi": "Hi there! What can I do for you?",
    "how are you": "I'm an AI, so I don't have feelings, but I'm here to help you!",
    "goodbye": "Goodbye! Have a great day!",
    "bye": "Bye! Take care!"
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    response_text = query_rag(query_text)
    print(response_text)

def query_rag(query_text: str):
    # Handle casual conversation
    for trigger, response in CASUAL_CONVERSATIONS.items():
        if trigger in query_text.lower():
            return response

    # Load memory
    memory = load_memory()
    if memory:
        memory_context = "\n\n".join([f"User: {entry['user']}\nBot: {entry['bot']}" for entry in memory])
    else:
        memory_context = ""

    # Prepare the DB
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB
    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    combined_context = f"{memory_context}\n\n---\n\n{context_text}".strip()
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=combined_context, question=query_text)

    model = Ollama(model="llama3.1")
    response_text = model.invoke(prompt)

    # Save memory
    memory.append({"user": query_text, "bot": response_text})
    save_memory(memory)

    return response_text

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            try:
                memory_data = json.load(file)
            except json.JSONDecodeError:
                return []
        timestamp = memory_data.get("timestamp")
        memory = memory_data.get("memory")
        if datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=MEMORY_DURATION_DAYS) > datetime.now():
            return memory
    return []

def save_memory(memory):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MEMORY_FILE, "w") as file:
        json.dump({"timestamp": timestamp, "memory": memory}, file)

if __name__ == "__main__":
    main()
