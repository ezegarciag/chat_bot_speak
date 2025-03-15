from fastapi import FastAPI, File, UploadFile
import torch
import torchaudio
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from io import BytesIO

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

# Ruta raíz
@app.get("/")
async def root():
    return {"message": "Welcome to the voice transcription API!"}

@app.get("/hello")
async def hello():
    return {"message": "Hello, welcome to the API!"}

# Endpoint para la transcripción de audio
@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Leer el archivo de audio
        audio_data = await file.read()

        # Convertir el archivo de audio a formato adecuado usando torchaudio
        audio_io = BytesIO(audio_data)
        waveform, sample_rate = torchaudio.load(audio_io)

        # Usar el pipeline de Whisper para transcribir el audio
        result = pipe(waveform.squeeze().numpy())["text"]

        return {"transcription": result}
    except Exception as e:
        return {"error": str(e)}
