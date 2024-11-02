# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


flask --app app run 

## Run with Docker

1. Build the image
```bash
docker build -t devops-project:latest .
```
2. Run the container
```bash
docker run -p 8080:5000 devops-project:latest
```
3. Check server health
```bash
curl http://localhost:8080/
```
