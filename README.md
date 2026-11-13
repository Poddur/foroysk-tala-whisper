# Føroysk Tala — Faroese Whisper Large CT2 remote speech recognition

This repository contains the **server code** and GitHub Actions Docker build for a private Hugging Face Inference Endpoint. The model weights are **not** stored here, in the Docker image, or on the user's Windows computer.

## Model

`carlosdanielhernandezmena/whisper-large-faroese-8k-steps-100h-ct2`

The server loads model weights from `/repository` when Hugging Face mounts the selected model, otherwise fetches them on the remote server. Both options are remote — no model download on the Windows client.

## 1. Docker Hub secrets (required before building)

In GitHub, go to **Settings → Secrets and variables → Actions → New repository secret** and create:

- `DOCKERHUB_USERNAME` = `poddur`
- `DOCKERHUB_TOKEN` = a Docker Hub access token with permission to **push** to `poddur/foroysk-tala-whisper`

Never paste a token into a GitHub file or into chat. The Docker Hub repository may remain **Private**. The GitHub repository is currently **Public**: do not put secrets or recordings in it. You can change it to Private under GitHub **Settings → General → Danger Zone → Change repository visibility**.

## 2. Build on GitHub-hosted infrastructure

Go to **Actions → Build and publish Faroese Whisper server → Run workflow**. The workflow validates Python syntax, builds the image and pushes:

`poddur/foroysk-tala-whisper:v0.1.0`

Check for a green workflow result and verify the new tag in Docker Hub. **No Docker installation or Whisper model download is required on Windows.** The build requires GitHub Actions access and valid secrets.

## 3. Configure Hugging Face Inference Endpoint (billing required)

Only after the Docker image is confirmed in Docker Hub, select the ASR model shown above and choose:

| Field | Value |
| --- | --- |
| Inference Engine | Custom |
| Engine Container URL | `poddur/foroysk-tala-whisper:v0.1.0` |
| Container port | `7860` |
| Health route | `/health` |
| Endpoint authentication | Private |
| Hardware | A compatible NVIDIA GPU, **not 2 vCPU / 4 GB CPU** |
| Environment | `CT2_DEVICE=cuda`, `CT2_COMPUTE_TYPE=float16` |
| Server Arguments / Command | Leave blank |

For a **private** Docker Hub image, supply username `poddur` and a **separate read-only** Docker Hub token in the custom container registry credential fields. Do not reuse the GitHub push token.

**Do not click Create Endpoint until the image build and configuration are verified and you accept the Hugging Face hourly cost.** Scaling to zero limits idle costs but startup can be slow; deployment and running capacity may still be billed.

## 4. Endpoint HTTP interface

- `GET /health` returns model readiness (HTTP 200 only after startup completed)
- `POST /transcribe` expects a **WAV** file in the request body and `Content-Type: audio/wav`; returns JSON with `text` and `model`
- Max WAV request body: 6 MB
- Use the Hugging Face private Endpoint's bearer token on the Windows app side; never embed tokens in JavaScript or GitHub code
- `FO_REMOTE_ASR_TOKEN` is optional extra authentication inside the container and should be **unset** for ordinary private-HF-gateway access unless both sides are deliberately configured for it

The existing Windows application must separately be configured for the endpoint URL and token. A Docker build alone does **not** switch the application's ASR.

## Verification / current status

This repository contains deployable **source**; a live endpoint and real speech recognition have not yet been verified. Check the GitHub Actions logs, Docker Hub image tag, Endpoint `/health`, and an actual Faroese WAV transcription before switching the Windows app.
