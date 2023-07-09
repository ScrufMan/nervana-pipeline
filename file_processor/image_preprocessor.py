import cv2
import numpy as np
import pytesseract

from .filters import generic_filter
from .helpers import blocking_to_async


# gray-scaling
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def blur(image):
    return cv2.GaussianBlur(image, (3, 3), 0)


# binarization
def thresholding(image):
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 9)


# morphology
def morpho(image):
    kernel = np.ones((1, 1), np.uint8)
    dilate = cv2.dilate(image, kernel)
    closed = cv2.erode(dilate, kernel)
    return closed


def is_alphanumeric_with_space(text: str):
    for char in text:
        if not (char.isalnum() or char.isspace()):
            return False
    return True


async def find_best_rotation(image):
    """
    Find the best among 4 possible rotations of the image based on the average confidence of the text recognition by tesseract
    :param image:
    :return: rotated image, text returned by tesseract
    """
    best_confidence = -np.inf
    best_rotation = None
    text = None

    angle_to_cv2 = {
        90: cv2.ROTATE_90_COUNTERCLOCKWISE,
        180: cv2.ROTATE_180,
        270: cv2.ROTATE_90_CLOCKWISE,
    }

    for angle in [0, 90, 180, 270]:
        rotated = cv2.rotate(image, angle_to_cv2[angle]) if angle != 0 else image
        # assuming most of the text is in Czech or English
        data = await blocking_to_async(pytesseract.image_to_data, rotated, output_type=pytesseract.Output.DICT,
                                       lang="ces+eng")

        # Extract the orientation confidence but exclude empty, or non-alphanumeric text
        confidences = [conf for conf, text in zip(data["conf"], data["text"]) if
                       conf != "-1" and not text.isspace() and is_alphanumeric_with_space(text)]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0

        if angle == 0:
            # give a little bit more weight to original image
            average_confidence *= 1.05

        if average_confidence > best_confidence:
            best_confidence = average_confidence
            best_rotation = rotated
            text = " ".join([text for text in data["text"] if
                             text != "" and not text.isspace() and is_alphanumeric_with_space(text)])
            text = generic_filter(text, oneline=True)
            text = text.lower()

    return best_rotation, text


async def preprocess(image_path):
    # to handle path with non-ascii characters we load image as numpy array
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8),
                         cv2.IMREAD_UNCHANGED)
    gray = grayscale(image)
    blurred = blur(gray)
    binarized = thresholding(blurred)
    closed = morpho(binarized)
    rotated, initial_text = await find_best_rotation(closed)
    return rotated, initial_text
