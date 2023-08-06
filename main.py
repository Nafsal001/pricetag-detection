import cv2
import pytesseract
import numpy as np

def preprocess_image(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Resize the image
    resized_image = cv2.resize(image, (1000, 300))
    # Convert to grayscale
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    return gray_image

def detect_text(image):
    # Use an OCR library (Pytesseract) to detect text from the image
    custom_config = r'--oem 3 --psm 6 outputbase digits tessedit_char_whitelist=0123456789,'
    detected_text = pytesseract.image_to_string(image, config=custom_config)
    numbers_with_commas = [num.strip() for num in detected_text.split() if num.strip() != '']

    return numbers_with_commas

def draw_contours(image, contours):
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 5)  # Red color (BGR value)
        cv2.putText(image, "Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # Red color (BGR value)

if __name__ == "__main__":
    image_path = "C:/Users/NAFSAL NAZAR/Downloads/mono_cam1_Image1683639716629626000 (1).png"
    preprocessed_image = preprocess_image(image_path)

    # Rotate the image 90 degrees clockwise to make the vertical segments horizontal
    rotated_image = cv2.rotate(preprocessed_image, cv2.ROTATE_90_CLOCKWISE)

    # Define custom horizontal segments
    start_y1, end_y1 = 0, 600
    start_y2, end_y2 = 600, 1000

    # Get segments from the rotated image
    segment1 = rotated_image[start_y1:end_y1, :]
    segment2 = rotated_image[start_y2:end_y2, :]

    # Apply binary thresholding
    _, binary_segment1 = cv2.threshold(segment1, 52, 255, cv2.THRESH_BINARY)

    # Apply morphological erosion to segment 2
    kernel = np.ones((2, 2), np.uint8)
    eroded_segment2 = cv2.erode(segment2, kernel, iterations=1)

    # Apply adaptive thresholding to the eroded segment 2
    adaptive_threshold_segment2 = cv2.adaptiveThreshold(eroded_segment2, 231, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 13, 4)

    # Detect numbers with commas in both segments
    detected_numbers_segment1 = detect_text(binary_segment1)
    detected_numbers_segment2 = detect_text(adaptive_threshold_segment2)

    print("Detected Numbers with Commas in Segment 1:")
    print(detected_numbers_segment1)

    print("Detected Numbers with Commas in Segment 2:")
    print(detected_numbers_segment2)

    # Find contours around the numbers in each binary segment
    contours_segment1, _ = cv2.findContours(binary_segment1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_segment2, _ = cv2.findContours(adaptive_threshold_segment2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours and bounding rectangles on the original images
    segment1_with_contours = cv2.cvtColor(segment1, cv2.COLOR_GRAY2BGR)
    segment2_with_contours = cv2.cvtColor(segment2, cv2.COLOR_GRAY2BGR)
    draw_contours(segment1_with_contours, contours_segment1)
    draw_contours(segment2_with_contours, contours_segment2)

    # Display both segmented images with contours and bounding rectangles
    cv2.imshow('Segment 1 with Contours', segment1_with_contours)
    cv2.imshow('Segment 2 with Contours', segment2_with_contours)

    # Display the binary segment 1, eroded segment 2, and adaptive thresholded segment 2
    cv2.imshow('Binary Segment 1', binary_segment1)
    cv2.imshow('Eroded Segment 2', eroded_segment2)
    cv2.imshow('Adaptive Threshold Segment 2', adaptive_threshold_segment2)

    cv2.waitKey(0)
    cv2.destroyAllWindows()