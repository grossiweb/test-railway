import numpy as np
import cv2
from PIL import Image
from uuid import uuid4
import os
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import io

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
    # Define the mapping of numbers to Roman numerals
    roman_map = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'),
        (1, 'I')
    ]

    result = ''

    for value, symbol in roman_map:
        # Append the symbol to the result while the value can be subtracted from num
        while num >= value:
            result += symbol
            num -= value

    return result

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

def name_plate(input_image: Image, name: str, gender: str, number: int) -> Image:
    # Your HTML content
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

    # Set up selenium with headless option
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=600x85')

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("data:text/html;charset=utf-8," + html_content)

    screenshot = driver.get_screenshot_as_png()
    driver.quit()

    img_byte_array = io.BytesIO(screenshot)
    
    base_image = input_image

    base_width, base_height = base_image.size
    plate = Image.open(io.BytesIO(screenshot))
    
    plate_width, plate_height = plate.size
    
    watermark = plate.resize((base_width-24, int(base_height/9)+10)).convert("RGBA")
    
    recreation = Image.new('RGBA', (base_width, base_height))
    recreation.paste(base_image, (0,0))
    recreation.paste(watermark, (12, int(base_height-(plate_height/1.2))), mask=watermark)
    
    return recreation