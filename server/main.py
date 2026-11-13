"""Faroese speech-to-text service for a protected Hugging Face Inference Endpoint.

The CTranslate2 model is loaded on the remote endpoint, never on the Windows client.
"""
import hmac
import os
import tempfile

from fastapi import FastAPI, HTTPException, Request
from faster_whisper import WhisperModel

MODEL_ID = "carlosdanielhernandezmena/whisper-large-faroese-8k-steps-100h-ct2"
app = FastAPI(title="Føroysk Tala — remote Faroese ASR")
model = None


@app.on_event("startup")
def startup():
    global model
    model_path = "/repository" if os.path.isfile("/repository/model.bin") else MODEL_ID
    model = WhisperModel(
        model_path,
        device=os.getenv("CT2_DEVICE", "cuda"),
        compute_type=os.getenv("CT2_COMPUTE_TYPE", "float16"),
    )


@app.get("/health")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"ok": True, "model": MODEL_ID}


@app.post("/transcribe")
async def transcribe(request: Request):
    # A private HF Endpoint validates its own bearer token at the gateway.
    # Only use this optional second token if explicitly configured.
    secret = os.getenv("FO_REMOTE_ASR_TOKEN")
    if secret and not hmac.compare_digest(
        request.headers.get("authorization", ""), "Bearer " + secret
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if request.headers.get("content-type", "").split(";")[0].strip().lower() != "audio/wav":
        raise HTTPException(status_code=415, detail="WAV required")

    data = await request.body()
    if not 44 <= len(data) <= 6_000_000:
        raise HTTPException(status_code=413, detail="Invalid audio size")

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(data)
        tmp.flush()
        try:
            segments, _ = model.transcribe(tmp.name, beam_size=5, vad_filter=True)
            transcription = " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:
            raise HTTPException(status_code=422, detail="Unable to transcribe") from exc

    return {"text": transcription, "model": MODEL_ID}
