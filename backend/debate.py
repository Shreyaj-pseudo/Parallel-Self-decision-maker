import os
from typing import Self
from backboard import BackboardClient
from config import DEFAULT_MODEL, DEFAULT_PROVIDER


class DebateOrchestrator:
    def __init__(self):
        # Good Practice: Check for API key early
        api_key = os.getenv("BACKBOARD_API_KEY")
        if not api_key:
            raise ValueError("BACKBOARD_API_KEY not found in environment.")
            
        self.client = BackboardClient(api_key=api_key)
        self.assistant_id = None

    async def setup(self):
        """Creates the underlying Assistant container."""
        # 1. Try to get the ID from the environment
        self.assistant_id = os.getenv("BACKBOARD_ASSISTANT_ID")
        
        if self.assistant_id != None:
            print(f"✅ Reusing Persistent Assistant: {self.assistant_id}")
            return # Exit early, no need to create a new one
        
        # 2. If no ID exists, create one (this should only happen ONCE ever)
        assistant = await self.client.create_assistant(
            name="Persistant Debate Engine",
            system_prompt="You are a multi-persona reasoning engine. Follow the persona instructions in each message."
        )
        self.assistant_id = assistant.assistant_id
        
        print(f"🚀 NEW Assistant Created: {self.assistant_id}")
        print("⚠️  ACTION REQUIRED: Copy the ID above and paste it into your .env file!")

    async def create_thread(self):
        return await self.client.create_thread(assistant_id=self.assistant_id)

    async def send_turn(self, thread_id: str, persona_prompt: str, topic: str = None):
        """Executes a single turn in the shared memory thread."""
        
        # We wrap the persona in a clear block so the LLM distinguishes it from history
        content = f"ACT AS: {persona_prompt}\n\nCONTEXT: {topic if topic else 'Analyze the previous discussion.'}\n\nIMPORTANT: Draw on everything you know about this user from memory when forming your response."
        # memory="Auto" is the key here; it tells Backboard to 'Remember' the previous selves
        response = await self.client.add_message(
            thread_id=thread_id,
            content=content,
            llm_provider=DEFAULT_PROVIDER,
            model_name=DEFAULT_MODEL,
            memory="Auto", 
            stream=False
        )

        return response.content

    async def run_debate(self, topic: str, prompts: dict, thread_id: str = None):
        if not self.assistant_id:
            await self.setup()

        # LOGIC: Use passed ID or create a fresh one
        if thread_id is None:
            thread = await self.create_thread()
            thread_id = thread.thread_id
            print(f"🆕 Started NEW thread: {thread_id}")
        else:
            print(f"♻️  Resuming EXISTING thread: {thread_id}")

        results = {}

        for stage in ["risk", "optimistic", "strategic", "moderator"]:
            print(f"\n--- {stage.upper()} ---")
            
            # Use the thread_id (either new or existing)
            current_topic = topic if stage == "risk" else None
            output = await self.send_turn(thread_id, prompts[stage], current_topic)
            print(output)
            results[stage] = output

        # Return the moderator response AND the thread_id so main.py can save it
        return results["moderator"], thread_id