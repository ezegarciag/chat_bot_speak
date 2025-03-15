from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from ollama import chat

app = FastAPI()

async def generate_response(query):
    # Prompt del sistema en inglés para hablar de forma conversacional
    system_prompt = {'role': 'system', 'content': 'You are a helpful assistant. Please respond as if you are speaking directly to the user, using conversational and spoken language. Avoid writing in a formal or structured way.'}
    
    # Incluir el prompt del sistema en los mensajes enviados al modelo
    stream = chat(
        model='llama3.1:latest',
        messages=[system_prompt, {'role': 'user', 'content': query}],
        stream=True,
    )
    for chunk in stream:
        yield chunk['message']['content']

@app.post("/chat/")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("query", "")
    return StreamingResponse(generate_response(query), media_type="text/plain")
