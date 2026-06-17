
import io
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch
import torch.nn.functional as F
import numpy as np
from torchvision.models import efficientnet_b3
import torch.nn as nn
from torchvision import transforms

NUM_CLASSES = 3
CLASS_NAMES = ['Underweight', 'Healthy', 'Overweight']
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'bcs_model_final.pth')

def load_model():
    model = efficientnet_b3(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, NUM_CLASSES)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()
    return model

model = load_model()

app = Flask(__name__)
CORS(app)


# Image preprocessing (must match your training pipeline)
def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize(320),
        transforms.CenterCrop(300),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = transform(image).unsqueeze(0)
    return image

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    image_file = request.files['image']
    image_bytes = image_file.read()
    try:
        input_tensor = preprocess_image(image_bytes)
        with torch.no_grad():
            outputs = model(input_tensor)
            probs = F.softmax(outputs, dim=1).cpu().numpy()[0]
            pred_idx = int(probs.argmax())
            condition = CLASS_NAMES[pred_idx]
            confidence = int(probs[pred_idx] * 100)
        return jsonify({
            'condition': condition,
            'confidence': confidence
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
