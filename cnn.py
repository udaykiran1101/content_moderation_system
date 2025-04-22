import os
import shutil
import numpy as np
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import VGG16
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

# Path to your image directory
image_dir = r'C:\Users\zwano\OneDrive\Desktop\content\augmented'

# Prepare labels and directories for 'violent' and 'not_violent'
labels = ['violent', 'not_violent']
image_paths = []
image_labels = []

# Collect image paths and assign labels
for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_paths.append(os.path.join(root, file))
            label = 'violent' if 'violent' in root else 'not_violent'  # Assuming folder names correspond to class
            image_labels.append(label)

# Split the data into train and test sets (80% train, 20% test)
train_paths, test_paths, train_labels, test_labels = train_test_split(
    image_paths, image_labels, test_size=0.2, random_state=42
)

# Set up the ImageDataGenerator for train and test
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
test_datagen = ImageDataGenerator(rescale=1./255)

# Create temporary directories to store the images for the train/test split
train_dir = 'train_dir'
test_dir = 'test_dir'

# Create directories for 'violent' and 'not_violent' in train and test sets
os.makedirs(os.path.join(train_dir, 'violent'), exist_ok=True)
os.makedirs(os.path.join(train_dir, 'not_violent'), exist_ok=True)
os.makedirs(os.path.join(test_dir, 'violent'), exist_ok=True)
os.makedirs(os.path.join(test_dir, 'not_violent'), exist_ok=True)

# Copy images to the respective directories
def copy_images(image_paths, labels, dest_dir):
    for img_path, label in zip(image_paths, labels):
        img_name = os.path.basename(img_path)
        shutil.copy(img_path, os.path.join(dest_dir, label, img_name))

# Copy training and testing images to the respective directories
copy_images(train_paths, train_labels, train_dir)
copy_images(test_paths, test_labels, test_dir)

# Load a pre-trained VGG16 model and use transfer learning
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze the base model layers

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(512, activation='relu'),
    layers.Dense(1, activation='sigmoid')  # Binary classification (violent or not)
])

# Compile the model
model.compile(optimizer=optimizers.Adam(), loss='binary_crossentropy', metrics=['accuracy'])

# Load images using flow_from_directory for training and testing
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary',  # Binary classification (violent or not violent)
    shuffle=True
)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary',
    shuffle=False
)

# Train the model
history = model.fit(
    train_generator,
    epochs=5,
    validation_data=test_generator
)

# Plot training and validation accuracy/loss graphs
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.legend()
plt.show()

# Predict function for a new image
def predict_image(image_path):
    # Load and preprocess the image
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Rescale the image
    
    # Make the prediction
    prediction = model.predict(img_array)
    
    # Print the raw prediction value and determine the class
    print(f"Prediction probability: {prediction[0][0]}")
    print(f"Prediction: {'Violent' if prediction[0][0] < 0.05 else 'Not Violent'}")
    
    return prediction

# Example: Make a prediction on a new image
# image_path = r'C:\Users\zwano\OneDrive\Desktop\content\OIP.jpeg'
image2= r'C:\Users\zwano\OneDrive\Desktop\content\cat.jpeg'# Change to the image path you want to predict
# predict_image(image_path)
predict_image(image2)
