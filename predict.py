import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import pickle
from keras.utils import custom_object_scope
from textmod import tokenAndPositionEmbeddings, TransformerBlock

# Load the saved model and tokenizer
with custom_object_scope({'tokenAndPositionEmbeddings': tokenAndPositionEmbeddings, 
                          'TransformerBlock': TransformerBlock}):
    model = load_model('moderation_model.h5')

with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

def predict_text(text):
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=100, padding='post', truncating='post')
    pred = model.predict(padded)[0]
    label = np.argmax(pred)
    confidence = pred[label]
    return label, confidence 