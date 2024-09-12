import cv2
import requests

def capture_image():
    print("Initializing camera...")
    
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open the camera.")
        return None

    print("Camera initialized successfully. Capturing image...")
    
    # Capture a single frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture an image.")
        return None

    filename = "captured_document.jpg"
    
    # Save the captured image
    cv2.imwrite(filename, frame)

    print(f"Image captured and saved as {filename}.")
    
    # Release the camera
    cap.release()

    return filename


# Function to send image to Upstage OCR API
def extract_text_from_image(filename):
 
    api_key = "up_jGs3Xv2gvZuCBAb2OaTfhW3YiOZyH"
    
    url = "https://api.upstage.ai/v1/document-ai/ocr"
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"document": open(filename, "rb")}
    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to extract text"}

def main():
    print("Starting the process...")
    # Capture image from the camera
    image_filename = capture_image()

    if image_filename:
        print("Image captured successfully. Extracting text...")
        # Extract text from the captured image
        result = extract_text_from_image(image_filename)
        print("Extracted Text:", result)
    else:
        print("Image capture failed.")

if __name__ == "__main__":
    main()
