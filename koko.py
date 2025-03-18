from fastapi import FastAPI, Response
from pydantic import BaseModel
from kokoro import KPipeline
import numpy as np
import asyncio
import base64
import io
import soundfile as sf

app = FastAPI()

# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
pipeline = KPipeline(lang_code='a')  # Asegúrate de que lang_code coincide con la voz

class TextInput(BaseModel):
    text: str
    voz: str

async def generate_audio_fragment(text, fragment_index,voz):
    """Generar el audio de un fragmento de texto y devolver todos los subfragmentos."""
    generator = pipeline(
        text, voice= voz,  # Cambia la voz si lo deseas
        speed=1, split_pattern=r'\n+'
    )

    audio_fragments = []  # Lista para almacenar los fragmentos generados

    # Generar y almacenar todos los fragmentos de audio
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"Fragmento {fragment_index} - Subfragmento {i}:")
        print("Graphemes:", gs)
        print("Phonemes:", ps)

        # Convertir el tensor de audio a numpy
        audio_np = audio.detach().cpu().numpy()

        # Convertir a formato WAV en memoria
        with io.BytesIO() as wav_buffer:
            sf.write(wav_buffer, audio_np, 24000, format='WAV')
            wav_bytes = wav_buffer.getvalue()

        # Codificar en Base64
        audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')
        
        audio_fragments.append(audio_base64)
    
    return audio_fragments

@app.post("/generate_audio/")
async def generate_audio(input_data: TextInput):
    text = input_data.text
    voz = input_data.voz
    fragments = text.split('\n')  # Dividir el texto en fragmentos

    # Generar los audios de forma concurrente
    tasks = [generate_audio_fragment(fragment, i, voz) for i, fragment in enumerate(fragments)]
    all_audio_fragments = await asyncio.gather(*tasks)

    # Aplanar la lista de fragmentos
    audio_base64_list = [audio for sublist in all_audio_fragments for audio in sublist]
    return {"audio_fragments": audio_base64_list}


@app.get("/")
def root():
    return {"message": "intro"}

