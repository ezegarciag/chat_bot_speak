import requests
import base64
import sounddevice as sd
import io
import soundfile as sf

koko_url = "http://localhost:8001/generate_audio/"

# Texto de prueba
#sentence = """L'italiano è una lingua melodiosa e ricca di storia. Parlata da milioni di persone nel mondo, è famosa per la sua musicalità e il suo legame con l'arte, la cultura e la cucina. Dalle opere di Dante Alighieri ai capolavori del cinema italiano, questa lingua continua a incantare chiunque la ascolti."""

sentence = """Technology has been evolving at an astonishing rate over the past few decades. Innovations in artificial intelligence, machine learning, and robotics are transforming industries and reshaping the way we live and work. The possibilities seem endless, and we are only beginning to scratch the surface of what these advancements can offer."""

voz_it = "if_sara" # italiana

voz_en = "af_heart"


def send_request_and_play(text,voz):
    data = {
        "text": text,
        "voz": voz
    }
    try:
        response = requests.post(koko_url, json=data)
        response_json = response.json()
        
        if "audio_fragments" in response_json:
            for fragment_b64 in response_json["audio_fragments"]:
                # Decodificar Base64 a bytes
                audio_bytes = base64.b64decode(fragment_b64)
                # Leer el WAV en memoria con soundfile
                with io.BytesIO(audio_bytes) as audio_buffer:
                    audio_np, samplerate = sf.read(audio_buffer, dtype="float32")
                # Reproducir el audio
                sd.play(audio_np, samplerate=samplerate)
                sd.wait()
        else:
            print("No se recibieron fragmentos de audio.")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la solicitud: {e}")

# Procesar la oración
send_request_and_play(sentence, voz_en) # cambiale la voz segun el idioma
