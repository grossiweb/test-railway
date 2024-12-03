import os
import io
import logging
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from PIL import Image
import numpy as np
import cv2
import insightface
from insightface.app import FaceAnalysis
from download_models import download_inswapper_model
from helper import logo_watermark, name_plate, upscale
from MongoDBConnection import DBConnection
from uuid import uuid4
from functools import wraps
from dotenv import load_dotenv
from helper import NumToRoman
import requests
from S3Service import S3Service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, expose_headers=['X-Plate-Number', 'X-Plate-Name'])

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max-limit

# Initialize face detection and MongoDB
if not os.path.exists('models/inswapper_128.onnx'):
    download_inswapper_model()

facedetection = FaceAnalysis(name='buffalo_l', root="./")
facedetection.prepare(ctx_id=1)

dbClient = DBConnection(db="Names", collection="NameCount")

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def rate_limit(limit, per):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implement rate limiting logic here
            # For simplicity, we're not implementing actual rate limiting in this example
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Routes
@app.route('/api/v1/faceswap', methods=['POST'])
@rate_limit(limit=10, per=600)  # Example: 10 requests per minute
def faceswap():
    logger.info("Received face swap request")
    try:
        # File validation
        if 'image' not in request.files:
            logger.warning("No file part in the request")
            return jsonify({"error": "No file part"}), 400
        file = request.files['image']
        if file.filename == '':
            logger.warning("No selected file")
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename):
            logger.warning(f"File type not allowed: {file.filename}")
            return jsonify({"error": "File type not allowed"}), 400

        # Form data validation
        form = request.form
        name = form.get("name")
        gender = form.get("gender")
        style = form.get("style")
        level = form.get("level")

        if not all([name, gender, style, level]):
            logger.warning("Missing required fields in the request")
            return jsonify({"error": "Missing required fields"}), 400

        [_, _, style_category, style_filename] = style.split("/")

        plateName = name[0].upper() + name.lower()[1:]
        plateGender = gender[0].upper() + gender.lower()[1:]

        logger.info(f"Processing face swap for {name}, gender: {gender}, style: {style}, level: {level}")

        # Image processing
        np_img = np.frombuffer(file.read(), np.uint8)
        source_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        s3_service = S3Service()
        style_image_url = s3_service.get_specific_style(
            gender,
            category=style_category,
            filename=style_filename
        )
        
        style_image_response = requests.get(style_image_url)
        style_image_data = style_image_response.content
        image_array = np.asarray(bytearray(style_image_data), dtype=np.uint8)
        dest_img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if dest_img is None:
            logger.error(f"Destination image not found: destination images/{gender}/{style}")
            return jsonify({"error": "Destination image not found"}), 404

        # Face detection
        s_faces = facedetection.get(source_img)
        if len(s_faces) < 1:
            logger.warning("No face detected in source image")
            return jsonify({"error": "No face detected in source image"}), 400

        d_faces = facedetection.get(dest_img)
        if len(d_faces) < 1:
            logger.error("No face detected in destination image")
            return jsonify({"error": "No face detected in destination image"}), 500

        logger.info("Face detection completed successfully")

        # Face swapping
        swapper = insightface.model_zoo.get_model('models/inswapper_128.onnx', download=False, download_zip=False)
        res = swapper.get(dest_img, d_faces[0], s_faces[0], paste_back=True)
        logger.info("Face swapping completed")

        # Name plate logic
        findPerson = dbClient.get_name_data(name=f"{name.lower()}'{gender.lower()}")
        plateNumber = 1 if len(findPerson) < 1 else findPerson[0]["count"] + 1
        res = name_plate(input_image=res, name=name, gender=gender, number=plateNumber)
        logger.info(f"Name plate added for {name}, number: {plateNumber}")

        # Upscaling
        try:
            logger.info("Starting image upscaling")
            res = np.array(res)
            res = upscale(res)
            with io.BytesIO() as output:
                Image.fromarray(res).save(output, format='PNG')
                img_byte_array = output.getvalue()
            logger.info("Image upscaling completed successfully")
        except Exception as error:
            logger.error(f"Error during upscaling: {str(error)}")
            logger.info("Falling back to non-upscaled image")
            # Fallback to non-upscaled image
            with io.BytesIO() as output:
                res.save(output, format='PNG')
                img_byte_array = output.getvalue()

        logger.info("Face swap process completed successfully")
        headers={
            'Content-Type': 'image/png',
            'X-Plate-Number': NumToRoman(plateNumber),
            'X-Plate-Name': f"{plateName}'{plateGender} {NumToRoman(plateNumber)}",
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Expose-Headers': 'X-Plate-Number, X-Plate-Name'
        }
        return Response(
            img_byte_array,
            mimetype='image/png',
            status=200,
            headers=headers
        )

    except Exception as e:
        logger.error(f"Unexpected error in faceswap: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    logger.info(f"Starting Flask app on port {port}, debug mode: {debug_mode}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)