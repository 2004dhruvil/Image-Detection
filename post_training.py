import os
import cv2
import numpy as np
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# This script assumes 'model', 'scaler', 'X_test', 'y_test', and 'preprocess_and_extract' 
# are available in your notebook environment.
# You can copy-paste these blocks into new cells in your model.ipynb.

def evaluate_model(model, X_test, y_test):
    print("--- EVALUATION ---")
    y_pred = model.predict(X_test)
    print("Accuracy Score:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=['real', 'fake']))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
    return y_pred

def save_artifacts(model, scaler):
    print("\n--- SAVING ARTIFACTS ---")
    joblib.dump(model, 'best_svm_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("Model and Scaler saved successfully as 'best_svm_model.pkl' and 'scaler.pkl'")

def predict_single_image(img_path, model, scaler, preprocess_fn):
    # Preprocess and extract features
    features = preprocess_fn(img_path)
    
    if features is None:
        return "Error: Could not process image."
    
    # Reshape and scale
    features = features.reshape(1, -1)
    features = scaler.transform(features)
    
    # Predict
    prediction = model.predict(features)
    return "Fake" if prediction[0] == 1 else "Real"

import matplotlib.pyplot as plt
import random

def plot_prediction_gallery(X_test, y_test, y_pred, n_images=10):
    print(f"\n--- VISUALIZING {n_images} PREDICTIONS ---")
    plt.figure(figsize=(15, 6))
    
    # Randomly pick indices
    indices = random.sample(range(len(X_test)), n_images)
    
    for i, idx in enumerate(indices):
        plt.subplot(2, 5, i + 1)
        
        # Note: SVM was trained on HOG features, not raw pixels.
        # So we can't easily plot the image from X_test directly.
        # In the notebook, you should use the original 'all_image_paths' list.
        
        plt.text(0.5, 0.5, f"Pred: {'Fake' if y_pred[idx]==1 else 'Real'}\nActual: {'Fake' if y_test[idx]==1 else 'Real'}", 
                 horizontalalignment='center', verticalalignment='center',
                 color='green' if y_pred[idx] == y_test[idx] else 'red',
                 fontsize=12, fontweight='bold')
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()

# Example Usage (after training finishes):
# y_pred = evaluate_model(model, X_test, y_test)
# plot_prediction_gallery(X_test, y_test, y_pred)
# save_artifacts(model, scaler)
# result = predict_single_image('path/to/image.jpg', model, scaler, preprocess_and_extract)
# print(f"Prediction: {result}")
