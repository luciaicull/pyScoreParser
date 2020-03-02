from .data_class import YamahaDataset, EmotionDataset, DataSet, DEFAULT_SCORE_FEATURES, DEFAULT_PERFORM_FEATURES
from .data_for_training import PairDataset
import pickle
import _pickle as cPickle
import csv

emotion_path = '/home/yoojin/data/emotionDataset/test'
#emotion_save_path = '/home/yoojin/repositories/pyScoreParser/emotion_save'
emotion_save_path = '/home/yoojin/data/emotionDataset/test/save'
print('Start: make dataset')
# make datasets
emotion_dataset = EmotionDataset(emotion_path, emotion_save_path)
print('Finished: make dataset')

print('Start: save dataset')
with open(emotion_save_path + "/total_dataset.dat", "wb") as f:
    pickle.dump(emotion_dataset, f, protocol=2)
print('Finished: save dataset')
'''
print('Start: load dataset')
with open(emotion_save_path + '/total_dataset.dat', 'rb') as f:
    u = cPickle.Unpickler(f)
    emotion_dataset = u.load()
print('Finished: load dataset')
'''
print('Start: save note matched result')
f = open(emotion_save_path + '/match_result.csv', 'w', encoding='utf-8')
wr = csv.writer(f)
wr.writerow(['performance.midi_path',
             'num_matched_notes', 'num_unmatched_notes'])
for piece in emotion_dataset.pieces:
    for performance in piece.performances:
        wr.writerow([performance.midi_path, str(
            performance.num_matched_notes), str(performance.num_unmatched_notes)])
f.close()
print('Finished: save note matched result')

print('Start: extract features')
for piece in emotion_dataset.pieces:
    piece.extract_perform_features(DEFAULT_PERFORM_FEATURES)
    piece.extract_score_features(DEFAULT_SCORE_FEATURES)
print('Finished: extract features')

print('Start: make PairDataset')
emotion_pair_data = PairDataset(emotion_dataset)
print('Finished: make PairDataset')

with open(emotion_save_path + "/pairdataset.dat", "wb") as f:
    pickle.dump(emotion_pair_data, f, protocol=2)

print('Start: statistics')
emotion_pair_data.update_dataset_split_type()
emotion_pair_data.update_mean_stds_of_entire_dataset()
print('Finished: statistics')

print('Start: save features')
emotion_pair_data.save_features_for_virtuosoNet(emotion_save_path)
print('Finished: save features')
