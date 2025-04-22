import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
import os

# Load the original image
img = load_img(r'C:\Users\zwano\OneDrive\Desktop\content\OIP.jpeg')  # Change this to your actual image path
x = img_to_array(img)
x = x.reshape((1,) + x.shape)  # Reshape to (1, height, width, channels)

# Create an output directory
os.makedirs('augmented', exist_ok=True)

# Augmentation settings
datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=[0.8, 1.2],
    horizontal_flip=True,
    brightness_range=[0.5, 1.5],
    channel_shift_range=30.0,
    fill_mode='nearest'
)

# Generate and save 10 augmented images
i = 0
for batch in datagen.flow(x, batch_size=1, save_to_dir='augmented', save_prefix='violent_aug', save_format='jpeg'):
    i += 1
    if i >= 100:
        break
