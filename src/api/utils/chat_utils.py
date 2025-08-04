from azure.ai.projects import AIProjectClient

def print_response(thread_id: str, project_client: AIProjectClient) -> None:

    messages = project_client.agents.messages.list(thread_id=thread_id)

    for msg in messages:
        if msg.role == "assistant":
            return f"AI: {msg.content[0]['text']['value']}"
        if msg.role == "user":
            return f"User: {msg.content[0]['text']['value']}"