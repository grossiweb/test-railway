import os
import requests

models = [
    ("models/inswapper_128.onnx", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/inswapper_128.onnx"),
    ("models/GFPGANv1.3.pth", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/GFPGANv1.3.pth"),
    ("models/realesr-general-x4v3.pth", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/realesr-general-x4v3.pth"),
    ("models/buffalo_l/1k3d68.onnx", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/1k3d68.onnx"),
    ("models/buffalo_l/2d106det.onnx", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/2d106det.onnx"),
    ("models/buffalo_l/det_10g.onnx", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/det_10g.onnx"),
    ("models/buffalo_l/genderage.onnx", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/genderage.onnx"),
    ("models/buffalo_l/w600k_r50.onnx", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/w600k_r50.onnx"),
    ("gfpgan/weights/detection_Resnet50_Final.pth", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/detection_Resnet50_Final.pth"),
    ("gfpgan/weights/parsing_parsenet.pth", "https://huggingface.co/MayankTamakuwala/backend_models/resolve/main/parsing_parsenet.pth"),
]
def download_related_models():
    for local_filename, url in models:

        # Ensure the directory exists
        os.makedirs(os.path.dirname(local_filename), exist_ok=True)

        if(not os.path.exists(local_filename)):
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            print(f'Model downloaded and saved as {local_filename}')
        else:
            print(f'{local_filename} already exists.')

if __name__ == "__main__":
    download_related_models()
