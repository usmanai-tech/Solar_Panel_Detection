import os
from ultralytics import YOLO
from PIL import Image, ImageDraw
import numpy as np

PATCH_SIZE = (256 , 256)

# Load the YOLO model
model_path = r'C:\Users\Administrator\Documents\MiniByte\Solar_panel_2\weights\best.pt'
model = YOLO(model_path)

# Function to process satellite image from a numpy array with dynamic confidence
def process_image(image_array, confidence):
    # Create patches, predict, and reconstruct the image
    patches, coords = create_and_save_patches(image_array)
    predictions = predict_on_patches(patches, coords, confidence)
    reconstructed_image_with_detections = reconstruct_image_with_predictions(image_array, predictions)
    return reconstructed_image_with_detections

# Function to create and save 416x416 patches from the large image
def create_and_save_patches(image, patch_size=PATCH_SIZE, output_dir='patches'):
    os.makedirs(output_dir, exist_ok=True)
    patches = []
    coords = []
    h, w, _ = image.shape
    for y in range(0, h, patch_size[0]):
        for x in range(0, w, patch_size[1]):
            patch = image[y:y + patch_size[0], x:x + patch_size[1]]
            if patch.shape[0] == patch_size[0] and patch.shape[1] == patch_size[1]:
                patches.append(patch)
                coords.append((x, y))
                # Save the patch (optional, can be removed if not needed)
                patch_image = Image.fromarray(patch)
                patch_filename = os.path.join(output_dir, f"patch_{x}_{y}.png")
                patch_image.save(patch_filename)
    return patches, coords

# Function to predict on patches with dynamic confidence
def predict_on_patches(patches, coords, confidence, output_dir='predicted_patches'):
    os.makedirs(output_dir, exist_ok=True)
    predictions = []

    for i, (patch, (x_offset, y_offset)) in enumerate(zip(patches, coords)):
        # Use the provided confidence value for prediction
        results = model.predict(source=patch, conf=confidence, save=True)
        predictions.append((results, x_offset, y_offset))

        # Check if any solar panels were detected
        solar_panel_detected = any(result.boxes for result in results)

        if solar_panel_detected:
            patch_image = Image.fromarray(patch)
            draw = ImageDraw.Draw(patch_image)

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

            patch_filename = os.path.join(output_dir, f"predicted_patch_{i}_{x_offset}_{y_offset}.png")
            patch_image.save(patch_filename)
            print(f"Saved detected patch: {patch_filename}")

    return predictions

# Function to reconstruct the image with predictions
def reconstruct_image_with_predictions(image, predictions, patch_size=PATCH_SIZE):
    reconstructed_image = Image.fromarray(image)
    draw = ImageDraw.Draw(reconstructed_image)

    for results, x_offset, y_offset in predictions:
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, x2 = int(x1 + x_offset), int(x2 + x_offset)
                y1, y2 = int(y1 + y_offset), int(y2 + y_offset)
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

    return reconstructed_image
