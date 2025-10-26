from dotenv import load_dotenv
from rag_queue.server import app
import uvicorn

load_dotenv()

def main():
    uvicorn.run(app, port=8000, host="0.0.0.0")

if __name__ == "__main__":
    main()
