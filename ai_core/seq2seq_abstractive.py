import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from seq2seq_abstractive import load_model, predict
from seq2seq_abstractive import train as train_seq2seq

__all__ = ['load_model', 'predict', 'train_seq2seq']
