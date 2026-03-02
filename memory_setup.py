# memory_setup.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("BACKBOARD_API_KEY")

def add_memory(assistant_id: str, content: str):
    assistant_id = os.getenv("BACKBOARD_ASSISTANT_ID")
    url = f"https://app.backboard.io/api/assistants/{assistant_id}/memories"
    headers = {"X-API-Key": API_KEY}
    payload = {"content": content}

    response = requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    #for checking memory 
    assistant_id = os.getenv("BACKBOARD_ASSISTANT_ID")
    load_dotenv()
    API_KEY = os.getenv("BACKBOARD_API_KEY")

    response = requests.get(
        f"https://app.backboard.io/api/assistants/{assistant_id}/memories",
        headers={"X-API-Key": API_KEY}
    )

    memories = response.json()
    for memory in memories["memories"]:
        print(f"Memory: {memory['content']}")
