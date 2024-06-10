from flask import Flask, jsonify, send_from_directory, request, send_file, Response
import os
import io
from PIL import Image
from download_models import download_inswapper_model
import insightface
from insightface.app import FaceAnalysis
import numpy as np
import cv2
from helper import logo_watermark, name_plate
from flask_cors import CORS
from MongoDBConnection import DBConnection

if not os.path.exists('models/inswapper_128.onnx'):
    download_inswapper_model()

facedetection = FaceAnalysis(name='buffalo_l', root="./")
facedetection.prepare(ctx_id=1, det_size=(640, 640))

app = Flask(__name__)
CORS(app)

dbClient = DBConnection(db="Names",collection="NameCount")

@app.route('/faceswap', methods=['POST'])
def faceswap():

    file = request.files['image']
    form = request.form
    
    name, gender, style, level = form["name"], form["gender"], form["style"], form["level"]
    
    np_img = np.frombuffer(file.read(), np.uint8)
    source_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
    # CHANGE DESTINATION IMAGE BASED ON STYLE AND LEVEL
    dest_img = cv2.imread("destination images/test2.png")

    swapper = insightface.model_zoo.get_model('models/inswapper_128.onnx', download=False, download_zip=False)

    ##############################################################################################################
    s_faces = facedetection.get(source_img)
    if len(s_faces) < 1:
        return Response({"error" : "No Face Detected in Source Image"}, status=404)

    d_faces = facedetection.get(dest_img)

    #############################################################################################################

    source_face = s_faces[0]
    dest_face = d_faces[0]

    #############################################################################################################

    res = dest_img.copy()
    res = swapper.get(res, dest_face, source_face, paste_back=True)

    #############################################################################################################

    # Los-Angelos Logo Logic
    res = logo_watermark(res)
    
    # Name Plate Number Logic
    findPerson = dbClient.get_name_data(name=name)
    
    if(len(findPerson) < 1):
        plateNumber = 1
    else:
        plateNumber = findPerson[0]["count"] + 1
    
    res = name_plate(input_image=res, name=name, gender=gender, number=plateNumber)
    
    # Returning Image Logic
    img_byte_array = io.BytesIO()
    res.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)

    return Response(img_byte_array, mimetype='image/png', status=200)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=8000))
