FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 HF_HUB_DISABLE_TELEMETRY=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ffmpeg libgomp1 ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt
COPY main.py .
EXPOSE 7860
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
