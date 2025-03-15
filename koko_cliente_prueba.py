import requests

# URL del servidor FastAPI
server_url = "http://127.0.0.1:8003/generate_audio/"

# Datos a enviar (texto para generar el audio)
data = {
    "text": "hello there! anything you want to know?"
}

# Enviar la solicitud POST al servidor FastAPI
response = requests.post(server_url, json=data)

