
import argparse
from .data_class import YamahaDataset, EmotionDataset, DataSet, DEFAULT_SCORE_FEATURES, DEFAULT_PERFORM_FEATURES
from .data_for_training import PairDataset
import pickle
import _pickle as cPickle

'''
parser = argparse.ArgumentParser()
parser.add_argument('--yamaha_path', type=str)
parser.add_argument('--emotion_path', type=str)
parser.add_argument('--save', action='store_true')
args = parser.parse_args()

if args.yamaha_path:
    dataset = YamahaDataset(args.yamaha_path, args.save)
    for piece in dataset.pieces:
        print(piece)  
if args.emotion_path:
    dataset = EmotionDataset(args.emotion_path, args.save)
    for piece in dataset.pieces:
        print(piece)
'''
# TODO: move to constants.py
yamaha_path = '/home/yoojin/data/chopin_cleaned-updated'
#yamaha_path = '/home/yoojin/data/test_data/Liszt'
yamaha_save_path = '/home/yoojin/repositories/pyScoreParser/yamaha_save'
emotion_path = '/home/yoojin/data/emotionDataset/total_dataset'
emotion_save_path = '/home/yoojin/repositories/pyScoreParser/emotion_save'


# make datasets
#yamaha_dataset = YamahaDataset(yamaha_path, yamaha_path)
emotion_dataset = EmotionDataset(emotion_path, emotion_save_path)

with open(emotion_save_path + "/total_dataset.dat", "wb") as f:
    pickle.dump(emotion_dataset, f, protocol=2)

'''
with open(yamaha_save_path + '/total_dataset.dat', 'rb') as f:
    u = cPickle.Unpickler(f)
    yamaha_dataset = u.load()

with open(emotion_save_path + 'total_dataset.dat', 'rb') as f:
    u = cPickle.Unpickler(f)
    emotion_dataset = u.load()

# for yamaha dataset
for piece in yamaha_dataset.pieces:
    piece.extract_perform_features(DEFAULT_PERFORM_FEATURES)
    piece.extract_score_features(DEFAULT_SCORE_FEATURES)
yamaha_pair_data = PairDataset(yamaha_dataset)

yamaha_pair_data.update_dataset_split_type()
yamaha_pair_data.update_mean_stds_of_entire_dataset()
yamaha_pair_data.save_features_for_virtuosoNet(yamaha_save_path)


# for emotion dataset
for piece in emotion_dataset.pieces:
    piece.extract_perform_features(DEFAULT_PERFORM_FEATURES)
    piece.extract_score_features(DEFAULT_SCORE_FEATURES)
emotion_pair_data = PairDataset(emotion_dataset)

emotion_pair_data.update_dataset_split_type()
emotion_pair_data.update_mean_stds_of_entire_dataset()
emotion_pair_data.save_features_for_virtuosoNet(emotion_save_path)
'''
