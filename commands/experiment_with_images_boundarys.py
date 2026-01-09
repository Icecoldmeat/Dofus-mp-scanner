import glob
import random
import time
from datetime import datetime

import cv2

from definitions import UNPROCESSED_ITEMS_PATH, ROOT, PROCESSED_ITEMS_PATH
from marketplace_boxes import average_text_box
from repository.mysql import ExternalDofusPriceRepository
from scraper import ScraperManager, Scraper
import cv2
import numpy as np
import easyocr
from matplotlib import pyplot as plt


def get_random_images_to_test() -> list:
    path = f"{PROCESSED_ITEMS_PATH}/**/*.png"
    list_of_files = glob.glob(path, recursive=True)
    return random.sample(list_of_files, 15)


def get_images_to_test() -> list:
    path = '/test/images/cache/20251227/130828/'

    file_names = [ #TODO ADD NEW TO TEST
                  'bone_band.png',
                  'goul_shield.png',
                  'ice_knight_map.png',
                  'cheeken.png',
                  'akakwa_pants.png',
                  'bulwark.png',
                  'captain_chafter_briefs.png',
                  'mantax.png',
                  'brakmar_shield.png',

                  'belteen.png',
                  'castus_flower.png',
                  'fish_juice.png',

                  'rhinteele_ring.png',
                  ]
    file_path = []
    for file_name in file_names:
        file_path.append(f'{ROOT}/{path}{file_name}')

    return file_path


def draw_easyocr_results(image, results, top_padding=20):
    """
    Draw EasyOCR results with red boxes and text, adding top padding
    to ensure text doesn't get drawn outside the image.

    image: np.array (BGR or grayscale)
    results: list of EasyOCR results
    top_padding: pixels to add at the top of the image
    """
    # Ensure 3 channels for color drawing
    if len(image.shape) == 2 or image.shape[2] == 1:
        img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        img = image.copy()

    h, w = img.shape[:2]

    # Create new image with extra top padding
    padded_img = np.zeros((h + top_padding, w, 3), dtype=img.dtype)
    padded_img[top_padding:, :, :] = img  # copy original image below padding

    # Dynamic scaling based on image height
    font_scale = max(0.3, min(1.0, h / 500))
    thickness = max(1, int(h / 200))

    for (bbox, text, conf) in results:
        # Convert bbox points to int and shift y by top_padding
        pts = [(int(x), int(y) + top_padding) for x, y in bbox]

        # Draw bounding box (red)
        cv2.polylines(padded_img, [np.array(pts)], isClosed=True, color=(0, 0, 255), thickness=thickness)

        # Draw text above box
        x, y = pts[0]
        text_y = y - 5  # will always be visible due to padding
        cv2.putText(
            padded_img, text, (x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale, (0, 0, 255), thickness, cv2.LINE_AA
        )

    return padded_img
reader = easyocr.Reader(['en'], gpu=True)
tests = get_images_to_test()
random_paths  = get_random_images_to_test()

all_paths = tests + random_paths


def ocr_with_allowlist(img_to_ocr, arguments: dict):
    rgb = cv2.cvtColor(img_to_ocr, cv2.COLOR_BGR2RGB)

    results = reader.readtext(rgb, **arguments )

    annotated = draw_easyocr_results(img_to_ocr, results)
    return annotated


for path in all_paths:
    print(path)

    # 1️⃣ Read the image
    image = cv2.imread(path)  # Replace with your image path

    b, g, r = cv2.split(image)
    r_boosted = cv2.multiply(r, 1.5)
    r_boosted = np.clip(r_boosted, 0, 255).astype(np.uint8)

    gray_red_emphasized = cv2.addWeighted(r_boosted, 0.6, b, 0.2, 0)
    gray_red_emphasized = cv2.addWeighted(gray_red_emphasized, 1.0, g, 0.2, 0)

    #plt.imshow(cv2.cvtColor(gray_red_emphasized, cv2.COLOR_BGR2RGB))
    #plt.title("Original Image")
    #plt.show()


    # NAME
    name = gray_red_emphasized[40:65,95:]

    # AVG PRICE
    avg = gray_red_emphasized[80:100,95:]

    # PACK
    pack = gray_red_emphasized[170:,55:120]

    # PRICE
    price = gray_red_emphasized[170:,170:300]


    images = [name, avg, pack,price, image ]  # your images
    titles = ["name", "avg", "pack","price", "org"]

    plt.figure(figsize=(12, 4))

    processed = [
        ocr_with_allowlist(name, {'allowlist':'/ abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789 ''', 'slope_ths': 0.4, 'width_ths': 1, 'height_ths': 1}),
        ocr_with_allowlist(avg,{'allowlist':'AP average price 0123456789, K', 'slope_ths': 0.4, 'width_ths': 1}),
        ocr_with_allowlist(pack,{'allowlist':'P pack x1 x10 x100 x1000', 'low_text': 0.1}),
        ocr_with_allowlist(price,{'allowlist':'P price 0123456789, K', 'low_text': 0.2, 'ycenter_ths': 0.75, 'height_ths': 1}),
        ocr_with_allowlist(image,{}),
    ]
    # processed for also results images only images
    for i, (img, title) in enumerate(zip(processed, titles), 1):
        plt.subplot(1, len(images), i)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title(title)
        plt.axis("off")

    plt.tight_layout()
    plt.show()