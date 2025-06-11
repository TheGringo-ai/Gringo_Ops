.streamlit/config.toml
[server]
headless = true
enableCORS = false
port = 8080

Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080
CMD ["streamlit", "run", "gringo_launcher.py", "--server.port=8080", "--server.address=0.0.0.0"]

.dockerignore
__pycache__/
*.pyc
.venv/
.git/
.streamlit/

app.yaml
runtime: custom
env: flex
service: gringo-launcher

requirements.txt
streamlit
openai
google-generativeai