import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from bilstm_extractive import load_model, predict
from bilstm_extractive import train as train_bilstm

__all__ = ['load_model', 'predict', 'train_bilstm']
