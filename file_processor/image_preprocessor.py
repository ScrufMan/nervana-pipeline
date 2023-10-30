import math

import cv2
import numpy as np

from config.config import SUPPORTED_LANGUAGES
from utils import make_sync_fn_async
from .filters import generic_filter
from .metadata import determine_text_language


# gray-scaling
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def blur(image):
    return cv2.GaussianBlur(image, (5, 5), 0)


# binarization
def thresholding(image):
    return cv2.adaptiveThreshold(image, 255,
	cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 5)


# morphology
def morpho(image):
    kernel = np.ones((3, 3), np.uint8)
    eroded = cv2.erode(image, kernel, iterations=2)
    dilated = cv2.dilate(eroded, kernel, iterations=1)
    return cv2.bilateralFilter(dilated, d=9, sigmaColor=75, sigmaSpace=75)


def deskew_image(
        image: np.ndarray, angle: float, background
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


async def find_best_rotation(image, easyocr_reader):
    """
    Find the best among 4 possible rotations of the image based on the average confidence of the text recognition by tesseract
    :param image:
    :return: rotated image, text returned by tesseract
    """
    best_confidence = -np.inf
    best_rotation = image
    best_text = ""

    angle_to_cv2 = {
        90: cv2.ROTATE_90_COUNTERCLOCKWISE,
        180: cv2.ROTATE_180,
        270: cv2.ROTATE_90_CLOCKWISE,
    }

    for angle in [0, 90, 180, 270]:
        rotated = cv2.rotate(image, angle_to_cv2[angle]) if angle != 0 else image
        # assuming most of the text is in Czech or English
        data = await make_sync_fn_async(easyocr_reader.readtext, rotated)

        # Extract the detection confidences of current orientation but exclude empty, or non-alphanumeric text
        confidences = []
        text = ""
        for _, detected_text, conf in data:
            if not detected_text.isspace():
                confidences.append(conf)
                text += detected_text + " "

        detection_confidence = sum(confidences) / len(confidences) if confidences else 0
        text = generic_filter(text)
        text = text.lower()

        # filter text to only alphanumeric characters with space for language detection
        filtered_text = ""
        for char in text:
            if char.isalnum() or char.isspace():
                filtered_text += char

        lang, lang_confidence = determine_text_language(filtered_text, ocr=True)
        if not lang or lang not in SUPPORTED_LANGUAGES:
            continue

        detection_confidence *= lang_confidence

        if angle == 0:
            # give a  bit more weight to original image
            detection_confidence *= 1.5

        if detection_confidence > best_confidence:
            best_confidence = detection_confidence
            best_rotation = rotated
            best_text = text

    return best_rotation, best_text


async def preprocess(image_path, easyocr_reader):
    def extract_text_regions(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        markers = cv2.watershed(image, markers)
        image[markers == -1] = [255, 0, 0]
        return markers

    # to handle path with non-ascii characters we load image as numpy array
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8),
                         cv2.IMREAD_UNCHANGED)
    regions = extract_text_regions(image)

    def crop_regions(image, boxes):
        cropped_regions = []
        for box in boxes:
            startX, startY, endX, endY = box
            cropped_region = image[startY:endY, startX:endX]
            cropped_regions.append(cropped_region)
        return cropped_regions

    cropped_regions = crop_regions(image, boxes)
    gray = grayscale(image)
    blurred = blur(gray)
    closed = morpho(blurred)
    binarized = thresholding(closed)
    rotated, initial_text = await find_best_rotation(binarized, easyocr_reader)
    return rotated, initial_text
