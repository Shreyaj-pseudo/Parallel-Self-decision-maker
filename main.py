import asyncio
from config import client
from debate import run_sequential_debate


async def main():
    # 1️⃣ Create a single assistant (identity container)
    assistant = await client.create_assistant(
        name="Parallel Self",
        system_prompt=(
            "You are a multi-agent cognitive system. "
            "Different personas will speak sequentially in this thread. "
            "You must strictly follow the persona instructions included "
            "inside each user message."
        )
    )

    # 2️⃣ Create shared persistent thread
    thread = await client.create_thread(assistant.assistant_id)

    print("\n🧠 Parallel Self is ready.")
    print("Type 'exit' to quit.\n")

    while True:
        topic = input("Enter a decision or problem: ")

        if topic.lower() == "exit":
            break

        try:
            await run_sequential_debate(thread.thread_id, topic)
        except Exception as e:
            print(f"\nError occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())