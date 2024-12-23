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

# Test application

## Unit testing: Test the app with unittest

To test the app, run the following command:

```bash
cd test/
python -m unittest test_app.py
```

## Integration testing: API tests with Docker and Newman

The app is tested using newman. Install newman using `npm install -g newman` and run the following command to test the app.

```bash
newman run test/devops-api-tests.postman_collection.json
```