import glob
import time
from datetime import datetime

import cv2

from definitions import UNPROCESSED_ITEMS_PATH, ROOT
from marketplace_boxes import average_text_box
from repository.mysql import ExternalDofusPriceRepository
from scraper import ScraperManager, Scraper
import cv2
import numpy as np
import easyocr
from matplotlib import pyplot as plt


path = '/test/images/cache/20251227/130828/cheeken.png'
path_root = f"{ROOT}{path}"

# 1️⃣ Read the image
image = cv2.imread(path_root)  # Replace with your image path
print("Original image shape:", image.shape)  # (H, W, 3)
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title("Original Image")
plt.show()

b, g, r = cv2.split(image)
r_boosted = cv2.multiply(r, 1.5)
r_boosted = np.clip(r_boosted, 0, 255).astype(np.uint8)

# Merge back with original B and G
enhanced_red = cv2.merge([b, g, r_boosted])
gray_red_emphasized = cv2.addWeighted(r_boosted, 0.6, b, 0.2, 0)
gray_red_emphasized = cv2.addWeighted(gray_red_emphasized, 1.0, g, 0.2, 0)
plt.imshow(gray_red_emphasized, cmap='gray')
plt.title("Grayscalered Image")
plt.show()

# 2️⃣ Convert to grayscale
#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#print("Grayscale image shape:", gray.shape)  # (H, W)
#plt.imshow(gray, cmap='gray')
#plt.title("Grayscale Image")
#plt.show()

# 4️⃣ Threshold / Binarize
#_, thresh = cv2.threshold(gray_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#plt.imshow(thresh, cmap='gray')
#plt.title("Thresholded Image")
#plt.show()

# 5️⃣ Optional: Morphological operations (close small gaps)
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
# processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
# plt.imshow(processed, cmap='gray')
# plt.title("Morphologically Processed Image")
# plt.show()

# 6️⃣ Feed to EasyOCR
reader = easyocr.Reader(['en'])
results = reader.readtext(gray_red_emphasized)

# 7️⃣ Print results and draw bounding boxes
for bbox, text, prob in results:
    print(f"Detected text: '{text}' with confidence {prob:.2f}")
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

# Show final image with detected text boxes
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title("Detected Text")
plt.show()

#date = datetime(year=2025,month=12,day=31)
#C:\Users\richa\Documents\Python\Dofus-mp-scanner\cache\items\20251228\122736
#C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251227\143247\70.png
#C:\Users\richa\Documents\Python\Dofus-mp-scanner/cache//items/20251231\173240\175.png