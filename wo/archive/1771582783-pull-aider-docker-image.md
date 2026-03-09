# Pull aider Docker Image

## Task
Pull the official aider Docker image for use with aider-run script.

## Commands
```bash
# Pull the lightweight core image
docker pull paulgauthier/aider

# Verify image was pulled
docker images | grep aider
```

## Status
- Image: `paulgauthier/aider` (core version, ~1-2GB)
- Already have: ollama running, codellama:7b loaded
- This enables: aider-run to orchestrate Docker container

## Notes
- Docker Desktop already running with ollama container
- Keep images under 20GB total (currently ~12GB in use)
- If pull fails, check disk space and Docker daemon status
