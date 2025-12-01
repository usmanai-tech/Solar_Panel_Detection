document.getElementById('uploadButton').addEventListener('click', async () => {
    const imageInput = document.getElementById('imageInput');
    const confidenceInput = document.getElementById('confidenceInput');
    const outputImage = document.getElementById('outputImage');
    const loading = document.getElementById('loading');
    const outputSection = document.getElementById('outputSection');
    const resetButton = document.getElementById('resetButton');

    // Check if an image file is selected
    if (!imageInput.files[0]) {
        alert("Please select an image file.");
        return;
    }

    // Validate confidence input
    const confidence = parseFloat(confidenceInput.value);
    if (isNaN(confidence) || confidence < 0.1 || confidence > 1.0) {
        alert("Please enter a valid confidence value between 0.1 and 1.0.");
        return;
    }

    // Prepare the form data
    const formData = new FormData();
    formData.append("file", imageInput.files[0]);
    formData.append("confidence", confidence);

    // Show loading message and hide the output image initially
    loading.style.display = 'block';
    outputImage.style.display = 'none';
    outputSection.style.display = 'none';
    resetButton.style.display = 'none';

    try {
        console.log("Uploading image:", imageInput.files[0].name);
        console.log("Confidence level:", confidence);

        // Send the image and confidence value to the FastAPI server
        const response = await fetch("http://127.0.0.1:8000/upload-image/", {
            method: "POST",
            body: formData,
        });

        // Get the processed image blob from the response
        const imageBlob = await response.blob();
        const imageUrl = URL.createObjectURL(imageBlob);

        // Display the processed image
        outputImage.src = imageUrl;
        outputImage.style.display = 'block';
        outputSection.style.display = 'block';
        resetButton.style.display = 'block';
        console.log("Processed image displayed successfully.");
    } catch (error) {
        console.error("Fetch error:", error);
        alert("Error: " + error.message);
    } finally {
        loading.style.display = 'none';
    }
});

// Zoom and Drag Functionality
const outputImage = document.getElementById('outputImage');
let scale = 1;
let translateX = 0;
let translateY = 0;
let isDragging = false;
let startX = 0;
let startY = 0;

// Function to handle zoom in and out centered on cursor
function zoomImage(event) {
    event.preventDefault();
    const zoomSpeed = 0.1;
    const rect = outputImage.getBoundingClientRect();
    const offsetX = event.clientX - rect.left;
    const offsetY = event.clientY - rect.top;

    // Determine the direction of the scroll (up or down)
    const delta = event.deltaY < 0 ? 1 : -1;
    const newScale = scale + delta * zoomSpeed;

    if (newScale < 0.5 || newScale > 10) return;

    const originX = ((offsetX - translateX) / scale) * 100 / rect.width;
    const originY = ((offsetY - translateY) / scale) * 100 / rect.height;

    outputImage.style.transformOrigin = `${originX}% ${originY}%`;

    translateX -= (offsetX - translateX) * (newScale / scale - 1);
    translateY -= (offsetY - translateY) * (newScale / scale - 1);

    // Update the scale
    scale = newScale;

    // Apply the transform
    outputImage.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
}

// Function to handle mouse down event for dragging
function onMouseDown(event) {
    isDragging = true;
    startX = event.clientX - translateX;
    startY = event.clientY - translateY;
    outputImage.style.cursor = 'grabbing';
}

// Function to handle mouse move event for dragging
function onMouseMove(event) {
    if (!isDragging) return;
    translateX = event.clientX - startX;
    translateY = event.clientY - startY;
    outputImage.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
}

// Function to handle mouse up event for stopping drag
function onMouseUp() {
    isDragging = false;
    outputImage.style.cursor = 'grab';
}

// Function to reset the image to its original state
function resetImage() {
    scale = 1;
    translateX = 0;
    translateY = 0;
    outputImage.style.transform = 'translate(0px, 0px) scale(1)';
    outputImage.style.transformOrigin = 'center'; // Reset transform origin to center
}

// Add event listeners for zoom, drag, and reset
outputImage.addEventListener('wheel', zoomImage);
outputImage.addEventListener('mousedown', onMouseDown);
document.addEventListener('mousemove', onMouseMove);
document.addEventListener('mouseup', onMouseUp);
document.getElementById('resetButton').addEventListener('click', resetImage);




