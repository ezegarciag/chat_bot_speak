import requests
import re
import threading
import time

koko_url = "http://127.0.0.1:8003/generate_audio/"

# Sentencia de texto larga
sentence = """In the vast landscape of human history, there have been numerous turning points that have shaped the course of civilization, some of which are widely recognized for their profound impact, such as the Industrial Revolution, the advent of the internet, and the space race of the 20th century; however, it is the ongoing evolution of technology that continues to alter the fabric of society in ways that were once unimaginable, transforming the way individuals communicate, interact, and perceive the world around them.
In the vast landscape of human history, there have been numerous turning points that have shaped the course of civilization, some of which are widely recognized for their profound impact, such as the Industrial Revolution, the advent of the internet, and the space race of the 20th century; however, it is the ongoing evolution of technology that continues to alter the fabric of society in ways that were once unimaginable, transforming the way individuals communicate, interact, and perceive the world around them.
In the vast landscape of human history, there have been numerous turning points that have shaped the course of civilization, some of which are widely recognized for their profound impact, such as the Industrial Revolution, the advent of the internet, and the space race of the 20th century; however, it is the ongoing evolution of technology that continues to alter the fabric of society in ways that were once unimaginable, transforming the way individuals communicate, interact, and perceive the world around them."""

# Dividir el texto solo por puntos
sentence_split = re.split(r'[.?!;]', sentence)

# Filtrar cualquier texto vacío que pueda quedar
sentences = [s.strip() for s in sentence_split if s.strip()]

def send_request(text):
    data = {
        "text": text
    }
    try:
        # Enviar la solicitud POST para cada oración
        response = requests.post(koko_url, json=data)
        # Imprimir la respuesta (opcional)
        print(response.json())  # Esto imprimirá el contenido JSON de la respuesta
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la solicitud: {e}")

# Crear y arrancar hilos con un retardo para evitar sobrecargar el servidor
threads = []
for i, s in enumerate(sentences):
    thread = threading.Thread(target=send_request, args=(s,))
    threads.append(thread)
    thread.start()
    
    # Esperar medio segundo antes de iniciar el siguiente hilo
    time.sleep(0.5)

# Esperar a que todos los hilos terminen
for thread in threads:
    thread.join()
