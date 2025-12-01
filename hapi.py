import io
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
from ultralytics import YOLO
from new3 import process_image
import logging

app = FastAPI()

# CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLO model
model_path = r'C:\Users\Administrator\Documents\MiniByte\Solar_panel_2\weights\best.pt'
model = YOLO(model_path)

logging.basicConfig(level=logging.INFO)

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...), confidence: float = Form(...)):
    try:
        logging.info("Received file: %s", file.filename)
        logging.info("Received confidence level: %f", confidence)

        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_array = np.array(image)

        # Process the image with the provided confidence value
        reconstructed_image_with_detections = process_image(image_array, confidence)

        output_image_io = io.BytesIO()
        reconstructed_image_with_detections.save(output_image_io, format="PNG")
        output_image_io.seek(0)

        return StreamingResponse(output_image_io, media_type="image/png")

    except Exception as e:
        logging.error("Error processing image: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def read_index():
    index_path = os.path.join(os.getcwd(), "static", "index.html")
    return FileResponse(index_path)

# Run the server with `uvicorn hapi:app --reload`
