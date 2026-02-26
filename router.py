def route_model(role: str):
    if role in ["risk", "optimistic"]:
        return {
            "llm_provider": "openai",
            "model_name": "gpt-4o-mini"
        }
    elif role == "strategic":
        return {
            "llm_provider": "openai",
            "model_name": "gpt-4o"
        }
    elif role == "moderator":
        return {
            "llm_provider": "openai",
            "model_name": "gpt-4o"
        }
    else:
        raise ValueError("Invalid role")