import tensorflow as tf
import numpy as np
import os
import pickle
import tqdm
from string import punctuation
sequence_length = 100
BATCH_SIZE = 128
EPOCHS = 500
FILE_PATH = "wonderland.txt"
BASENAME = os.path.basename(FILE_PATH)
text = open(FILE_PATH, encoding="utf-8").read()
text = text.lower()
text = text.translate(str.maketrans("", "", punctuation))
n_chars = len(text)
vocab = ''.join(sorted(set(text)))
print("unique_chars:", vocab)
n_unique_chars = len(vocab)
print("Number of characters:", n_chars)
print("Number of unique characters:", n_unique_chars)

