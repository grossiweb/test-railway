import os
import requests

def download_inswapper_model():
    url = 'https://github.com/grossiweb/Models/releases/download/inswapper_128/inswapper_128.onnx'
    local_filename = 'models/inswapper_128.onnx'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(local_filename), exist_ok=True)
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f'Model downloaded and saved as {local_filename}')

if __name__ == "__main__":
    download_inswapper_model()