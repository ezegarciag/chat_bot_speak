from fastapi import FastAPI
from io import BytesIO
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from core.mic import Microphone

# Inicializar la API
app = FastAPI()

# Cargar el modelo al inicio de la API
model_id = "openai/whisper-large-v3"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

@app.get("/")
async def root():
    return {"message": "Welcome to the voice transcription API!"}


@app.get("/transcribe_microphone/")
async def transcribe_microphone():
    # Captura el audio del micrófono
    mic = Microphone()
    audio_data = mic.start_listening()

    # Convertir el audio a formato adecuado para la transcripción
    audio_io = BytesIO(audio_data)

    # Usar el pipeline de Whisper para transcribir el audio
    result = pipe(audio_io)["text"]

    return {"transcription": result}
