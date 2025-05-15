import numpy as np
import cv2
from PIL import Image
from uuid import uuid4
import os
import base64
import time
import io
import sys
import logging

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import torch

from torchvision.transforms import functional
sys.modules["torchvision.transforms.functional_tensor"] = functional

from basicsr.archs.srvgg_arch import SRVGGNetCompact
from gfpgan.utils import GFPGANer
from realesrgan.utils import RealESRGANer

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def logo_watermark(input_image: np.array, position=(30,30)):
    
    file_name = uuid4()
    cv2.imwrite(f"{file_name}.png", input_image)
    
    base_image = Image.open(f"{file_name}.png")
    os.remove(f"{file_name}.png")

    width, height = base_image.size
    
    watermark = Image.open("misc images/logo.png").resize((int(width/10) + 20, int(width/10))).convert("RGBA")
    
    recreation = Image.new('RGBA', (width, height))
    
    recreation.paste(base_image, (0,0))
    recreation.paste(watermark, position, mask=watermark)
    
    return recreation

def NumToRoman(num):
    romanMap = { 
        1000: "M", 900: "CM", 500: "D", 400: "CD", 100: "C",
        90: "XC", 50: "L", 40: "XL", 10: "X", 9: "IX", 8: "VIII",
        7: "VII", 6: "VI", 5: "V", 4: "IV", 3: "III", 2: "II", 1: "I"
    }
        
    keys = list(romanMap.keys())

    i = 0
    dig = []
    res = ""
    while num > 0:
        x = num - keys[i]
        if x < 0:
            i += 1
        else:
            num = x
            dig.append(keys[i])

    for i in dig:
        res += romanMap[i]
    return res

def name_watermark(input_image: Image):
    img = input_image

    width, height = img.size
    
    fnt = ImageFont.truetype("nordic.ttf", 60)

    txt = Image.new("RGBA", img.size, (255, 255, 255, 0))

    d = ImageDraw.Draw(txt)

    _, _, w, h = d.textbbox((0, 0), "Stefano Angelo - I", font=fnt)
    
    position = ((width-w)/2, (height - (height)/4))

    d.text(position, "Stefano Angelo - I", font=fnt, fill=(255, 255, 255, 255))

    out = Image.alpha_composite(img, txt)

    return out

def change_logo_color():
    # img = Image.open('logo.jpg')

    # img = img.convert('RGB')

    # pickle.dump(img, open("logo.pkl", "wb"))

    with open("logo.pkl", "rb") as file:
        img = pickle.load(file)

    required_color = (0, 255, 0)

    pixels = img.load()

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            if (
                (96<= pixels[i,j][0] <= 239) and 
                (44<= pixels[i,j][1] <= 80) and
                (205 <= pixels[i,j][2] <= 255)
            ):
                pixels[i, j] = required_color
    
    return img

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def name_plate(input_image: np.array, name: str, gender: str, number: int) -> Image:

    print(f"Input parameters - Name: {name}, Gender: {gender}, Number: {number}")
    print(f"Input image shape: {input_image.shape if isinstance(input_image, np.ndarray) else 'Not numpy array'}")

    file_name = str(uuid4())
    try:
        cv2.imwrite(f"{file_name}.png", input_image)
        input_image = Image.open(f"{file_name}.png")
        os.remove(f"{file_name}.png")
    except Exception as e:
        print(f"Error handling input image: {e}")
        raise

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--force-device-scale-factor=1')
    options.add_argument('--hide-scrollbars')
    # Increase width to 640px to accommodate borders
    options.add_argument('--window-size=640,85')
    options.add_argument('--high-dpi-support=1')
    options.binary_location = "/usr/bin/google-chrome"

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(10)
        
        html_content = f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <title>Design Example</title>
                <style>
                
                body{{
                    padding:0;
                    margin:0;
                }}
                
                .background-image {{
                    position: absolute;
                    min-width: 600px;
                    background: url(data:image/png;base64,{get_base64_image("./misc images//plate base.png")}) no-repeat center;
                    background-size: contain;
                }}

                .entity-bg {{
                    background: url(data:image/png;base64,{get_base64_image("./misc images//bg.png")}) no-repeat center;
                    background-size: cover;
                    width: fit-content;
                }}

                .number {{
                    width: 100%;
                    justify-content: flex-end;
                    display: flex;
                }}

                .embossed-text {{
                    font-family: "futura";
                    letter-spacing: 0.1em;
                    color: transparent;
                    font-weight: 100;
                    font-size: xx-large;
                    text-transform: uppercase;
                    text-shadow: 1px 1px 1px rgba(138, 112, 92, 0.8),
                    -1px -1px 1px rgba(0, 0, 0, 0.6), 1px -1px 1px rgba(138, 112, 92, 0.8),
                    -1px 1px 1px rgba(0, 0, 0, 0.6);
                    padding-left: 5px;
                }}
                </style>
            </head>
            <body>
                <div class="background-image">
                <div>
                    <div class="entity-bg embossed-text">{name}'{gender}</div>
                </div>
                <div class="number">
                    <div class="entity-bg embossed-text">{NumToRoman(number)}</div>
                </div>
                </div>
            </body>
            </html>
        '''

        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': 640,
            'height': 85,
            'deviceScaleFactor': 1,
            'mobile': False
        })

        # Save HTML to a temporary file
        debug_html_path = f"plate_{file_name}.html"
        with open(debug_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        driver.get(f"file://{os.path.abspath(debug_html_path)}")

        # Wait for background images to load
        time.sleep(1.5)

        # Get the exact viewport size for verification
        viewport_size = driver.execute_script("""
            return {
                width: document.documentElement.clientWidth,
                height: document.documentElement.clientHeight,
                devicePixelRatio: window.devicePixelRatio
            }
        """)

        # Take screenshot
        screenshot = driver.get_screenshot_as_png()

        # Clean up
        driver.quit()
        os.remove(debug_html_path)

        # Process the screenshot
        img = Image.open(io.BytesIO(screenshot))
        # Crop the extra width to get back to 600.5px
        img = img.crop((0, 1, 600.5, 84.5))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        screenshot = buffer.getvalue()

        # Save for debugging
        # with open("test.png", "wb") as f:
        #     f.write(screenshot)

        # Process screenshot
        base_image = input_image
        base_width, base_height = base_image.size
        
        # Open and verify screenshot
        plate = Image.open(io.BytesIO(screenshot))
        plate_width, plate_height = plate.size
        print(f"Plate dimensions: {plate_width}x{plate_height}")
        
        # Resize and compose
        watermark = plate.resize((base_width-24, int(base_height/9)+10)).convert("RGBA")
        recreation = Image.new('RGBA', (base_width, base_height))
        recreation.paste(base_image, (0,0))
        recreation.paste(watermark, (12, int(base_height-(plate_height*1.7))), mask=watermark)

        return recreation

    except Exception as e:
        print(f"Error during processing: {e}")
        if 'driver' in locals():
            driver.quit()
        raise

def upscale(img: np.array):
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        logger.info("MPS device found.")
        print ("MPS device found.")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info("CUDA device found.")
        print ("CUDA device found.")
    else:
        device = torch.device("cpu")
        logger.info("Using CPU.")
        print ("Using CPU.")

    model = SRVGGNetCompact(
        num_in_ch=3, 
        num_out_ch=3, 
        num_feat=64, 
        num_conv=32, 
        upscale=4, 
        act_type='prelu'
    ).to(device)
    model_path = './models/realesr-general-x4v3.pth'
    upsampler = RealESRGANer(scale=4, model_path=model_path, model=model, tile=0, tile_pad=10, pre_pad=0, half=False, device=device)

    try:
        
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        face_enhancer = GFPGANer(
            model_path=f'./models/GFPGANv1.3.pth',
            upscale=2,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=upsampler
        )

        try:
            _, _, output = face_enhancer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
        except RuntimeError as error:
            print('Error', error)

        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output
    except Exception as error:
        print('global exception', error)
        return None, None

# if __name__ == "__main__":
#     print("mayank")
