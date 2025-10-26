from dotenv import load_dotenv
from rag_queue.client.dramatiq_client import redis_broker, result_backend
import os
from pathlib import Path
from huggingface_hub import InferenceClient
import dramatiq

# Load .env file from the parent directory (rag_queue folder)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not hf_token:
    raise ValueError("HuggingFace API token not found. Add it to your .env file.")

client = InferenceClient(token=hf_token)

# Don't initialize these at module load time - do it inside the task
embedding_model = None
vector_db = None

def get_vector_db():
    """Lazy load the vector database to avoid memory issues during worker startup"""
    global embedding_model, vector_db
    if vector_db is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_qdrant import QdrantVectorStore
        
        print("🔄 Loading embedding model...")
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        print("🔄 Connecting to vector database...")
        vector_db = QdrantVectorStore.from_existing_collection(
            url="http://localhost:6333",
            collection_name="learning_rag",
            embedding=embedding_model
        )
        print("✅ Vector DB loaded successfully")
    return vector_db

@dramatiq.actor(store_results=True)
def process_query_task(query: str):
    try:
        print(f"🎯 Processing query: {query}")
        
        # Load vector DB only when needed
        db = get_vector_db()
        print("🔍 Searching for relevant chunks...")
        search_results = db.similarity_search(query=query)
        
        context = "\n\n".join([
            f"Page Context: {result.page_content}\nPage Number: {result.metadata['page_label']}\nSource: {result.metadata['source']}"
            for result in search_results
        ])
        
        SYSTEM_PROMPT = f"""
        You are a helpful AI Assistant who answers user query based on the available context retrieved from a PDF file along with page_contents and page number. You should only answer the user based on the following context and navigate the user to open the right page number to know more. Context: {context}
        """
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
        
        print("🤖 Generating response...")
        response = client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        
        answer = response.choices[0].message['content']
        print(f"✅ Response generated: {answer[:100]}...")
        return answer
        
    except Exception as e:
        print(f"❌ Error in process_query_task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise