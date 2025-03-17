import requests
import re
import threading
import time

koko_url = "http://127.0.0.1:8003/generate_audio/"

# Sentencia de texto larga
sentence = """L'italiano è una lingua melodiosa e ricca di storia. Parlata da milioni di persone nel mondo, è famosa per la sua musicalità e il suo legame con l'arte, la cultura e la cucina. Dalle opere di Dante Alighieri ai capolavori del cinema italiano, questa lingua continua a incantare chiunque la ascolti.

Viaggiare in Italia significa immergersi in un mondo di suoni armoniosi, gesti espressivi e tradizioni secolari. Ogni regione ha il suo dialetto e le sue peculiarità, rendendo l'italiano ancora più affascinante e variegato.

Se vuoi scoprire la bellezza dell'italiano, non c'è modo migliore che praticarlo ogni giorno, magari con una buona tazza di caffè e una conversazione appassionante!"""

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
