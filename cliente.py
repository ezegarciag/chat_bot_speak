import requests
import pyaudio
import wave
import io
import numpy as np
import re
import aiohttp
import asyncio


# Configuración de PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 500  # Umbral de energía para detectar audio
SILENCE_DURATION = 1.0  # Tiempo en segundos para considerar silencio

# URLs de las APIs
transcribe_url = "http://127.0.0.1:8001/transcribe/"
chat_url = "http://127.0.0.1:8002/chat/"
koko_url = "http://127.0.0.1:8003/generate_audio/"


# Inicializar PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Esperando audio...")

recording = False
frames = []
silence_frames = 0


async def send_to_chat(query):
    """Recibe un flujo de texto y envía oraciones completas a otro lugar de manera asíncrona"""
    sentence = ""  # Variable para acumular las oraciones

    # Crear una sesión asíncrona para manejar la solicitud HTTP
    async with aiohttp.ClientSession() as session:
        async with session.post(chat_url, json={"query": query}) as response:
            # Cambiar iter_any() por iter_chunked()
            async for chunk in response.content.iter_chunked(1024):
                if chunk:
                    # Decodificar y acumular los datos del chunk
                    text = chunk.decode('utf-8')
                    sentence += text  # Agregar el fragmento al acumulado de la oración
                    
                    # Verificar si se ha formado una oración completa
                    if re.search(r'[.!?]$', sentence):  # Si termina con ., ! o ?
                        # Aquí se puede enviar la oración a otro lugar
                        print(f"Oración completa detectada: {sentence.strip()}")
                        data = {
                            "text": sentence.strip()
                        }
                        # Enviar la oración completa a otro servicio/API de manera asíncrona
                        async with session.post(koko_url, json=data):
                            pass  # Puedes manejar la respuesta si es necesario
                        
                        sentence = ""  # Reiniciar la oración para la siguiente



async def process_audio():
    global recording  # Añadir esta línea para declarar que estamos utilizando la variable global 'recording'

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            energy = np.abs(audio_data).mean()

            if energy > SILENCE_THRESHOLD:
                if not recording:
                    print("Detección de voz: Iniciando grabación...")
                    recording = True
                    frames = []

                frames.append(data)
                silence_frames = 0
            elif recording:
                silence_frames += 1
                frames.append(data)

                # Si hay suficiente silencio, detener grabación
                if silence_frames > (SILENCE_DURATION * RATE / CHUNK):
                    print("Silencio detectado: Enviando audio...")
                    recording = False

                    # Convertir a WAV en memoria
                    buffer = io.BytesIO()
                    with wave.open(buffer, 'wb') as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(p.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))
                    buffer.seek(0)

                    # Enviar a la API de transcripción
                    files = {'file': ('audio.wav', buffer, 'audio/wav')}
                    response = requests.post(transcribe_url, files=files)

                    if response.status_code == 200:
                        transcription = response.json().get("transcription", "")
                        print("Transcripción:", transcription)

                        # Enviar transcripción al chat de manera asíncrona
                        await send_to_chat(transcription)
                        print("Esperando audio...")
                    else:
                        print("Error en la transcripción:", response.status_code)

                    frames = []  # Reiniciar buffer

    except KeyboardInterrupt:
        print("\nDeteniendo grabación...")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

# Ejecutar la función principal asíncrona
asyncio.run(process_audio())
