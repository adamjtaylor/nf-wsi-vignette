import numpy as np
import cv2 as cv

# Create a dummy image
img = np.random.randint(0, 256, (1881, 2416, 3), dtype=np.uint8)

# Try encoding
success, img_encode = cv.imencode(".jpg", img, [cv.IMWRITE_JPEG_QUALITY, 80])

if success:
    print("JPEG encoding successful.")
else:
    print("JPEG encoding failed.")
