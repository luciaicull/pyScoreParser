from .data_class import YamahaDataset, EmotionDataset, DataSet, DEFAULT_SCORE_FEATURES, DEFAULT_PERFORM_FEATURES
from .data_for_training import PairDataset
import pickle
import _pickle as cPickle
import csv

pairdataset_path = '/home/yoojin/repositories/pyScoreParser/emotion_save/pairdataset.dat'
with open(pairdataset_path, 'rb') as f:
    u = cPickle.Unpickler(f)
    pair_dataset = u.load()

for pair in pair_dataset.data_pairs:
    # you can check features by using features[key] here
    # key are in constants.DEFAULT_SCORE_FEATURES or constants.DEFAULT_PERFORM_FEATURES
    features = pair.features
