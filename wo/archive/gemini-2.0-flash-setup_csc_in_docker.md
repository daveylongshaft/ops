---
requires: [docker]
platform: [linux]
---
# Set Up CSC Inside Docker Container

## Recommended Agent: gemini-2.0-flash (fast, straightforward container setup)

## Goal
Build a Docker image that runs the CSC server and verify platform detection works inside containers.

## Steps

1. Create a Dockerfile at repo root:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /opt/csc
   COPY . .
   RUN pip install -e packages/csc-shared && pip install -e packages/csc-server
   CMD ["csc-server"]
   ```
2. Build and run:
   ```bash
   docker build -t csc-server .
   docker run --rm -it csc-server python -c "from csc_shared.platform import Platform; p = Platform(); import json; print(json.dumps(p.platform_data['virtualization'], indent=2))"
   ```
3. Verify virtualization type is "docker_container"
4. Run the Docker platform test:
   ```bash
   docker run --rm -v /opt/csc:/opt/csc -w /opt/csc csc-server python -m pytest tests/test_platform_docker.py -v
   ```
5. Save the test output, commit, push

## Key concerns
- `/.dockerenv` detection
- cgroup-based container detection
- Docker-in-Docker not needed for detection tests
- Resource assessment should still work
