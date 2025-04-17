import numpy as np
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import pickle
from keras.utils import custom_object_scope
from textmod import tokenAndPositionEmbeddings, TransformerBlock  # Import your custom layers

# Initialize Flask app
app = Flask(__name__)

# Load the trained model and tokenizer with custom object scope
with custom_object_scope({'tokenAndPositionEmbeddings': tokenAndPositionEmbeddings, 
                          'TransformerBlock': TransformerBlock}):
    model = load_model('moderation_model.h5')  # Adjust the path if necessary

with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

# Preprocess the input text function
def preprocess_text(text):
    # Tokenize the input text using the tokenizer
    sequences = tokenizer.texts_to_sequences([text])
    # Pad the sequences to ensure they are of the same length as the model's input
    padded_sequences = pad_sequences(sequences, maxlen=100)  # Adjust maxlen to 100 based on model's requirement
    return padded_sequences

# Function to predict on new input
def predict_text(text):
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=100, padding='post', truncating='post')
    pred = model.predict(padded)[0]
    label = np.argmax(pred)
    confidence = pred[label]
    return label, confidence

# Route to handle predictions
@app.route('/predict', methods=['POST'])
def predict():
    text_content = request.form.get('textContent')  # Get text content from the form
    if not text_content:
        return render_template('index.html', prediction_text='No text provided.')

    try:
        # Predict the content
        label, confidence = predict_text(text_content)

        # Return a result based on the prediction
        if label == 0:
            result = f"✅ Safe comment ({confidence:.2f} confidence)"
        else:
            result = f"⚠️ Toxic comment detected! ({confidence:.2f} confidence)"

        return render_template('index.html', prediction_text=result)

    except Exception as e:
        return render_template('index.html', prediction_text=f'Error: {str(e)}')

# Route to serve the home page
@app.route('/')
def home():
    return render_template('index.html', prediction_text='')

if __name__ == '__main__':
    app.run(debug=True)
