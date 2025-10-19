from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model
)

user_query = input("Ask something: ")

search_results = vector_db.similarity_search(query=user_query)

context = "\n\n".join([
    f"Page Context: {result.page_content}\nPage Number: {result.metadata['page_label']}\nSource: {result.metadata['source']}"
    for result in search_results
])

SYSTEM_PROMPT = f"""
You are a helpfull AI Assistant who answers user query based on the available context retrieved from a PDF file along with page_contents and page number. You should only ans the user based on the following context and navigate the user to open the right page number to know more. Context: {context}
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_query}
]

response = client.chat_completion(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    messages=messages,
    max_tokens=300,
    temperature=0.7
)

print("🤖:", response.choices[0].message['content'])
