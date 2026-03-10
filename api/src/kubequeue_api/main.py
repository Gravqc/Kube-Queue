from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import socket
import os
import redis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Redis connection configuration
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

logger.info(f"Configured to connect to Redis at {redis_host}:{redis_port}")

# Create Redis connection (lazy connection)
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


class TaskRequest(BaseModel):
    task: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "hostname": socket.gethostname()
    }


@app.get("/")
def root():
    return {"message": "KubeQueue API running"}


@app.post("/task")
def create_task(task_request: TaskRequest):
    """
    Enqueue a task to Redis for worker processing
    """
    try:
        # Push task to Redis queue
        result = r.rpush("tasks", task_request.task)
        logger.info(f"Task enqueued: {task_request.task}, queue length: {result}")
        
        return {
            "status": "enqueued",
            "task": task_request.task,
            "hostname": socket.gethostname(),
            "queue_length": result
        }
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        raise HTTPException(status_code=503, detail=f"Redis connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error enqueueing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))