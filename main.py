import asyncio
from debate import DebateOrchestrator
from memory_setup import add_memory
from prompts import RISK_AVERSE_PROMPT, OPTIMISTIC_PROMPT, STRATEGIC_PROMPT, MODERATOR_PROMPT
import requests
from utils import load_sessions, save_session

async def main():
    debate = DebateOrchestrator()
    await debate.setup()
    
    sessions = load_sessions()
    
    print("\n--- 🧠 Parallel Self: Session Manager ---")
    if sessions:
        print("Available Sessions:")
        for name in sessions:
            print(f" • {name}")
    else:
        print("No saved sessions found.")

    choice = input("\nEnter session name to RESUME or 'new' to start fresh: ").strip()

    active_thread_id = None
    session_name = choice

    if choice.lower() != 'new' and choice in sessions:
        active_thread_id = sessions[choice]
    else:
        session_name = input("What would you like to name this new session? ")

    topic = input(f"\n[Topic for {session_name}]: ")

    prompts_map = {
        "risk": RISK_AVERSE_PROMPT,
        "optimistic": OPTIMISTIC_PROMPT,
        "strategic": STRATEGIC_PROMPT,
        "moderator": MODERATOR_PROMPT
    }

    # Execute the debate
    _, final_thread_id = await debate.run_debate(topic, prompts_map, active_thread_id)

    # Save progress to our local JSON database
    save_session(session_name, final_thread_id)
    print(f"\n✅ Progress saved in session: '{session_name}'")

if __name__ == "__main__":
    asyncio.run(main())
    