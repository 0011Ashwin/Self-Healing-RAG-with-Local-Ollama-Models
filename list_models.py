import urllib.request
import json

def list_ollama_models():
    url = "http://localhost:11434/api/tags"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print("Available Ollama Models:")
            for model in data.get('models', []):
                print(f"- {model['name']}")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        print("Make sure Ollama is running (default port 11434)")

if __name__ == "__main__":
    list_ollama_models()
