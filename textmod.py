import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

vocab_size = 10000
maxlen = 100
embed_dim = 32
num_heads = 2
ff_dim = 64

# Load CSV data
csv = r'C:\Users\zwano\Downloads\jigsaw-toxic-comment-classification-challenge\train.csv\train.csv'
df = pd.read_csv(csv)

class tokenAndPositionEmbeddings(layers.Layer):
    def __init__(self, vocab_size, max_len, emb_dim, **kwargs):
        super(tokenAndPositionEmbeddings, self).__init__(**kwargs)
        self.token_embeddings = layers.Embedding(vocab_size, emb_dim)
        self.position_embeddings = layers.Embedding(max_len, emb_dim)
        self.vocab_size = vocab_size
        self.max_len = max_len
        self.emb_dim = emb_dim

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.position_embeddings(positions)
        x = self.token_embeddings(x)
        return x + positions

    def get_config(self):
        config = super().get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "max_len": self.max_len,
            "emb_dim": self.emb_dim,
        })
        return config


# Define the Transformer block
class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1, **kwargs):
        super(TransformerBlock, self).__init__(**kwargs)
        self.att = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = keras.Sequential([
            layers.Dense(ff_dim, activation="relu"),
            layers.Dense(embed_dim)
        ])
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.rate = rate

    def call(self, inputs, training=None):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)

        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)

    def get_config(self):
        config = super().get_config()
        config.update({
            "embed_dim": self.embed_dim,
            "num_heads": self.num_heads,
            "ff_dim": self.ff_dim,
            "rate": self.rate
        })
        return config

# Define the transformer model
def build_transformer_model(maxlen, vocab_size, embed_dim, num_heads, ff_dim):
    inputs = layers.Input(shape=(maxlen,))
    embedding_layer = tokenAndPositionEmbeddings(vocab_size, maxlen, embed_dim)
    x = embedding_layer(inputs)

    transformer_block = TransformerBlock(embed_dim, num_heads, ff_dim)
    x = transformer_block(x)

    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(20, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    outputs = layers.Dense(2, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)
    return model

# Compile the model
model = build_transformer_model(maxlen, vocab_size, embed_dim, num_heads, ff_dim)
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

texts = df['comment_text'].astype(str).tolist()
labels = df['toxic'].tolist()  # You can extend this to multi-label later

# Tokenize
tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
padded_sequences = pad_sequences(sequences, maxlen=maxlen, padding='post', truncating='post')

# Convert to arrays
x_train_real = np.array(padded_sequences)
y_train_real = np.array(labels)

# Retrain model with real data
model.fit(x_train_real, y_train_real, batch_size=32, epochs=1)

# Function to predict on new input
def predict_text(text):
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=maxlen, padding='post', truncating='post')
    pred = model.predict(padded)[0]
    label = np.argmax(pred)
    confidence = pred[label]

    if label == 0:
        print(f"✅ Safe comment ({confidence:.2f} confidence)")
    else:
        print(f"⚠️ Toxic comment detected! ({confidence:.2f} confidence)")

model.save("moderation_model.h5")

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)