import os
import joblib
import cv2
from skimage.feature import hog
import warnings
warnings.filterwarnings('ignore')

IMG_SIZE = 128
MODEL_PATH = 'best_svm_model.pkl'
SCALER_PATH = 'scaler.pkl'
IMG_PATH = '../test_fake_image.png'

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

img = cv2.imread(IMG_PATH)
img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)

hog_features = hog(
    gray,
    orientations=9,
    pixels_per_cell=(8, 8),
    cells_per_block=(2, 2),
    block_norm='L2-Hys'
)

features = hog_features.reshape(1, -1)
features_scaled = scaler.transform(features)

pred = model.predict(features_scaled)
print(f"RAW PREDICTION: {pred[0]}")
