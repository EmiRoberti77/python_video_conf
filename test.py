import cv2
import numpy as np

# Create a simple black image
image = np.zeros((720, 1280, 3), dtype=np.uint8)

# Draw a white rectangle
cv2.rectangle(image, (100, 100), (500, 500), (255, 255, 255), -1)

# Display the image
cv2.imshow('Test Image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()