from keras.layers import Layer
import tensorflow as tf
from keras.utils import register_keras_serializable

@register_keras_serializable()
class tokenAndPositionEmbeddings(Layer):
    def __init__(self, vocab_size, maxlen, embed_dim, **kwargs):
        super().__init__(**kwargs)
        self.token_embed = tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.pos_embed = tf.keras.layers.Embedding(input_dim=maxlen, output_dim=embed_dim)
        self.maxlen = maxlen  # store maxlen and embed_dim
        self.embed_dim = embed_dim

    def call(self, x):
        positions = tf.range(start=0, limit=self.maxlen, delta=1)
        positions = self.pos_embed(positions)
        x = self.token_embed(x)
        return x + positions

    @classmethod
    def from_config(cls, config):
        # Extract maxlen and embed_dim from the config, and pass them to the constructor
        return cls(vocab_size=config['vocab_size'], 
                   maxlen=config['max_len'], 
                   embed_dim=config['emb_dim'])

@register_keras_serializable()
class TransformerBlock(Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.att = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([
            tf.keras.layers.Dense(ff_dim, activation='relu'),
            tf.keras.layers.Dense(embed_dim),
        ])
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)

    def call(self, inputs, training=False):
        attn_output = self.att(inputs, inputs)
        out1 = self.layernorm1(inputs + self.dropout1(attn_output, training=training))
        ffn_output = self.ffn(out1)
        return self.layernorm2(out1 + self.dropout2(ffn_output, training=training))
