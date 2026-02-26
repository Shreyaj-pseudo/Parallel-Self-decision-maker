from config import client, DEFAULT_MODEL, DEFAULT_PROVIDER
from prompts import SELVES, MODERATOR_PROMPT


async def send_persona_turn(thread_id: str, persona_name: str, persona_prompt: str, topic: str = None):
    """
    Sends one sequential persona turn to the shared Backboard thread.
    """

    if topic:
        content = f"""
You are now acting as: {persona_name}

Persona Instructions:
{persona_prompt}

Debate Topic:
{topic}

Read all previous messages in the thread carefully before responding.
Respond concisely but distinctly in this persona.
"""
    else:
        content = f"""
You are now acting as: {persona_name}

Persona Instructions:
{persona_prompt}

Read all previous messages in the thread carefully.
Continue the debate from this persona's perspective.
Be concise.
"""

    response = await client.add_message(
        thread_id=thread_id,
        content=content,
        llm_provider=DEFAULT_PROVIDER,
        model_name=DEFAULT_MODEL,
        memory="Auto",
        stream=False
    )

    return response.content


async def run_sequential_debate(thread_id: str, topic: str):
    print(f"\n--- Debate Topic: {topic} ---\n")

    # 1️⃣ First persona introduces discussion
    first_persona_name = list(SELVES.keys())[0]
    first_persona_prompt = SELVES[first_persona_name]

    print(f"🧠 {first_persona_name} speaking...")
    first_response = await send_persona_turn(
        thread_id,
        first_persona_name,
        first_persona_prompt,
        topic
    )
    print(f"{first_persona_name}: {first_response}\n")

    # 2️⃣ Remaining personas
    for persona_name in list(SELVES.keys())[1:]:
        persona_prompt = SELVES[persona_name]

        print(f"🧠 {persona_name} speaking...")
        response = await send_persona_turn(
            thread_id,
            persona_name,
            persona_prompt
        )
        print(f"{persona_name}: {response}\n")

    # 3️⃣ Moderator synthesis
    print("⚖️ Moderator synthesizing...\n")

    moderator_response = await send_persona_turn(
        thread_id,
        "Moderator",
        MODERATOR_PROMPT
    )

    print(f"Final Recommendation:\n{moderator_response}\n")
    