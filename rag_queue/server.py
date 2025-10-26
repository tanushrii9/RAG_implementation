from fastapi import FastAPI, Query
from rag_queue.queues.tasks import process_query_task
from rag_queue.client.dramatiq_client import result_backend
from dramatiq.results.errors import ResultMissing
import json

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Server is up and running 🚀"}

@app.post("/chat")
def chat(query: str = Query(..., description="The chat query of user")):
    job = process_query_task.send(query)
    return {"status": "queued", "job_id": job.message_id}

@app.get("/result")
def get_result(job_id: str = Query(..., description="Job ID")):
    """
    Fetch the result of a Dramatiq task from Redis.
    """
    try:
        result_value = result_backend.get_result(job_id, block=False)
        if result_value is None:
            return {"status": "processing", "job_id": job_id}
        # Try to convert bytes → str → json (if structured)
        if isinstance(result_value, bytes):
            result_value = result_value.decode("utf-8")
        try:
            result_value = json.loads(result_value)
        except:
            pass
        return {"status": "completed", "job_id": job_id, "result": result_value}
    except ResultMissing:
        return {"status": "not_found", "job_id": job_id}
    except Exception as e:
        return {"status": "error", "job_id": job_id, "message": str(e)}
