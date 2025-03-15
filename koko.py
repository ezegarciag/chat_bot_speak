from fastapi import FastAPI
from pydantic import BaseModel
from kokoro import KPipeline
import sounddevice as sd
import numpy as np
import asyncio

app = FastAPI()

# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
pipeline = KPipeline(lang_code='a')  # Asegúrate de que lang_code coincide con la voz

# Cola para gestionar los fragmentos de audio
audio_queue = asyncio.Queue()

class TextInput(BaseModel):
    text: str

async def play_audio():
    """Reproducir el audio a 24000 Hz sin bloquear el hilo principal"""
    while True:
        # Esperar hasta que haya un fragmento de audio disponible en la cola
        audio_np = await audio_queue.get()
        
        # Reproducir el audio
        sd.play(audio_np, 24000)
        sd.wait()  # Usamos wait aquí ya que no queremos que se solapen los audios
        
        # Indicar que se ha terminado de reproducir
        print("Audio ha terminado de reproducirse.")

async def generate_audio_fragment(text, fragment_index):
    """Generar el audio de un fragmento de texto"""
    generator = pipeline(
        text, voice='af_heart',  # Cambia la voz si lo deseas
        speed=1, split_pattern=r'\n+'
    )

    # Generar el primer fragmento de audio y devolverlo
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"Fragmento {fragment_index} - Subfragmento {i}:")
        print("Graphemes:", gs)
        print("Phonemes:", ps)

        # Convertir el tensor a numpy
        audio_np = audio.detach().cpu().numpy()

        # Devolver el fragmento de audio generado
        return audio_np  # Solo devolvemos el primer fragmento generado

@app.post("/generate_audio/")
async def generate_audio(input_data: TextInput):
    text = input_data.text
    fragments = text.split('\n')  # Dividir el texto en fragmentos

    # Generar los audios de forma concurrente, pero respetando el orden
    tasks = []
    for i, fragment in enumerate(fragments):
        # Generar el audio en segundo plano para cada fragmento
        tasks.append(generate_audio_fragment(fragment, i))

    # Esperamos a que se generen todos los audios
    audio_fragments = await asyncio.gather(*tasks)

    # Colocar los fragmentos en la cola para que se reproduzcan
    for audio_np in audio_fragments:
        await audio_queue.put(audio_np)

    return {"status": "Audio generado y en espera de ser reproducido"}

# Inicia la reproducción de audio en segundo plano
@app.on_event("startup")
async def startup():
    # Comienza la reproducción de audio en un hilo asíncrono
    asyncio.create_task(play_audio())
