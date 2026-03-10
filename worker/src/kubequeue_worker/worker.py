import os
import sys
import time
import redis
import socket

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

def main():
    # Get Redis connection details from environment
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    
    print(f"Worker starting on {socket.gethostname()}", flush=True)
    print(f"Connecting to Redis at {redis_host}:{redis_port}", flush=True)
    
    # Connect to Redis
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    # Wait for Redis to be ready
    while True:
        try:
            r.ping()
            print("Connected to Redis successfully", flush=True)
            break
        except redis.ConnectionError as e:
            print(f"Waiting for Redis... ({e})", flush=True)
            time.sleep(2)
    
    print("Worker ready, listening for tasks...", flush=True)
    
    # Main worker loop
    while True:
        try:
            # Block until a task is available (timeout: 1 second)
            result = r.blpop("tasks", timeout=1)
            
            if result:
                queue_name, task = result
                print(f"[{socket.gethostname()}] Processing task: {task}", flush=True)
                
                # Simulate work
                time.sleep(2)
                
                print(f"[{socket.gethostname()}] Task completed: {task}", flush=True)
        
        except Exception as e:
            print(f"Error processing task: {e}", flush=True)
            time.sleep(1)

if __name__ == "__main__":
    main()
