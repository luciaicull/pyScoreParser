'''
from pathlib import Path
import pretty_midi, csv
from .musicxml_parser import MusicXMLDocument
from . import xml_utils
from .midi_utils import midi_utils
from . import xml_midi_matching as matching
'''
from .data_class import YamahaDataset, EmotionDataset, DataSet, DEFAULT_SCORE_FEATURES, DEFAULT_PERFORM_FEATURES
from .data_for_training import PairDataset
import pickle
import _pickle as cPickle
import csv

emotion_path = '/home/yoojin/data/20200326/test_xml_midi/'
emotion_save_path = '/home/yoojin/data/20200326/test_xml_midi/save'
'''
Test new alignment as original method
'''


print('Start: make dataset')
emotion_dataset = EmotionDataset(
    emotion_path, emotion_save_path, new_alignment=True)
print('Finished: make dataset')

print('Start: save dataset')
with open(emotion_save_path + "/total_dataset.dat", "wb") as f:
    pickle.dump(emotion_dataset, f, protocol=2)
print('Finished: save dataset')

print('Start: load dataset')
with open(emotion_save_path + '/total_dataset.dat', 'rb') as f:
    u = cPickle.Unpickler(f)
    emotion_dataset = u.load()
print('Finished: load dataset')

print('Start: save note matched result')
f = open(emotion_save_path + '/final_match_result.csv', 'w', encoding='utf-8')
wr = csv.writer(f)
wr.writerow(['performance.midi_path',
             'num_matched_notes', 'num_unmatched_notes'])
for piece in emotion_dataset.pieces:
    for performance in piece.performances:
        wr.writerow([performance.midi_path.split('/')[-1], str(
            performance.num_matched_notes), str(performance.num_unmatched_notes)])
f.close()
print('Finished: save note matched result')

'''
print('Start: load dataset')
with open(emotion_save_path + '/total_dataset.dat', 'rb') as f:
    u = cPickle.Unpickler(f)
    emotion_dataset = u.load()
print('Finished: load dataset')
'''
print('Start: extract features')
for piece in emotion_dataset.pieces:
    piece.extract_perform_features(DEFAULT_PERFORM_FEATURES)
    piece.extract_score_features(DEFAULT_SCORE_FEATURES)
print('Finished: extract features')

print('Start: make PairDataset')
emotion_pair_data = PairDataset(emotion_dataset)
print('Finished: make PairDataset')

# save PairDataset for entire dataset for feature tracking
# you can check feature dictionary in each ScorePerformPairData() object in PairDataset.data_pairs
# reference : data_for_training.py or use test_check_features.py
# features in ScorePerformData.features() are shape of dictionary
#       : {feature_key1:(len(notes)), feature_key2:(len(notes)), ...}
with open(emotion_save_path + "/pairdataset.dat", "wb") as f:
    pickle.dump(emotion_pair_data, f, protocol=2)

print('Start: statistics')
emotion_pair_data.update_dataset_split_type()
emotion_pair_data.update_mean_stds_of_entire_dataset()
print('Finished: statistics')

# features will saved at {emotion_save_path}.{train OR test OR validation}.{perform_midi_name}.dat
# features are in shape of list
#        : (len(notes), len(features))
print('Start: save features')
emotion_pair_data.save_features_for_virtuosoNet(emotion_save_path)
print('Finished: save features')



# TODO
# Codes to be removed
'''
DATASET_PATH = Path('/home/yoojin/data/20200326/test_Bach_paf/')
SAVE_PATH = Path('/home/yoojin/data/20200326/test_Bach_paf/save')
#DATASET_PATH = Path(
#    '/home/yoojin/data/20200320/test_Schumann_tanze_6_7_modified/')

def make_path_pairs(xml_paths, perf_paths, match_paths):
    pairs = []
    for xml_path in xml_paths:
        for perf_path in perf_paths:
            if xml_path.name[:-len('.xml')] in perf_path.name:
                for match_path in match_paths:
                    if perf_path.name[:-len('.mid')] in match_path.name:
                        pair = {'xml_path': xml_path,
                                'perf_path': perf_path, 'match_path': match_path}
                        pairs.append(pair)
                        #print(match_path)
    return pairs


def get_xml_notes(xml_path):
    xml_obj = MusicXMLDocument(xml_path)
    notes, rests = xml_obj.get_notes()
    directions = xml_obj.get_directions()
    time_signatures = xml_obj.get_time_signatures()

    xml_notes = xml_utils.apply_directions_to_notes(
        notes, directions, time_signatures)
    return xml_notes


def get_midi_notes(perf_path):
    midi = midi_utils.to_midi_zero(perf_path)
    midi = midi_utils.add_pedal_inf_to_notes(midi)
    midi_notes = midi.instruments[0].notes

    return midi_notes


def read_match_file(match_path):
    match_list, missing_xml_list = matching.read_match_file(match_path)

    return match_list, missing_xml_list


def find_corresp_match_and_midi(dic, match_list, midi_notes, score_time, score_pitch):
    for match_index, match in enumerate(match_list):
        if match['xmlNoteID'] != '*':
            if score_time == match['scoreTime'] and score_pitch == match['pitch']:
                dic['match_index'].append(match_index)
                midi_idx = find_midi_note_index(
                    midi_notes, match['midiStartTime'], match['midiEndTime'], match['pitch'])
                if midi_idx != -1:
                    dic['midi_index'].append(midi_idx)
                    match['used'] = True


def check_pitch(pitch):
    if len(pitch) == 4:
        base_pitch_num = pretty_midi.note_name_to_number(pitch[0]+pitch[-1])
        if pitch[1:3] == 'bb':
            pitch = pretty_midi.note_number_to_name(base_pitch_num-2)
        if pitch[1:3] == '##':
            pitch = pretty_midi.note_number_to_name(base_pitch_num+2)
    return pitch


def find_midi_note_index(midi_notes, start, end, pitch, ornament=False):
    pitch = check_pitch(pitch)
    if not ornament:
        for i, note in enumerate(midi_notes):
            print(abs(note.start - start))
            print(abs(note.end - end))
            print(pretty_midi.note_name_to_number(pitch))
            if (abs(note.start - start) < 0.001) and (abs(note.end - end) < 0.001) and (note.pitch == pretty_midi.note_name_to_number(pitch)):
                return {'idx': i, 'pitch': pretty_midi.note_number_to_name(note.pitch)}
    else:
        for i, note in enumerate(midi_notes):
            if (abs(note.start - start) < 0.0002) and (abs(note.end - end) < 0.0002) and (abs(note.pitch - pretty_midi.note_name_to_number(pitch)) <= 2):
                return {'idx': i, 'pitch': pretty_midi.note_number_to_name(note.pitch)}
    return -1


def find_trill_midis(dic, match_list, midi_notes):
    if len(dic['match_index']) > 1:
        # 미디 여러 개 - xml 하나라서 match가 여러 개 뜰 경우
        dic['is_trill'] = True

        start_idx = dic['match_index'][0]
        end_idx = dic['match_index'][-1]
        match_id = match_list[start_idx]['xmlNoteID']
        pitch = match_list[start_idx]['pitch']

        new_match_idx = []

        # find trill
        trill_pitch = None
        for idx in range(start_idx, end_idx + 1):
            if idx in dic['match_index']:
                continue
            else:
                if (match_list[idx]['xmlNoteID'] == match_id) or (match_list[idx]['errorIndex'] == 3):
                    midi_idx = find_midi_note_index(
                        midi_notes, match_list[idx]['midiStartTime'], match_list[idx]['midiEndTime'], match_list[idx]['pitch'])
                    if midi_idx != -1:
                        dic['midi_index'].append(midi_idx)
                        new_match_idx.append(idx)
                        trill_pitch = match_list[idx]['pitch']
                        if match_list[idx]['xmlNoteID'] != match_id:
                            dic['fixed_trill_idx'].append(midi_idx)
                        match_list[idx]['used'] = True

        # find one prev trill
        prev_idx = start_idx - 1
        prev = match_list[prev_idx]
        if prev['pitch'] == trill_pitch:
            if (prev['xmlNoteID'] == match_id) or (prev['errorIndex'] == 3):
                midi_idx = find_midi_note_index(
                    midi_notes, prev['midiStartTime'], prev['midiEndTime'], prev['pitch'])
                if midi_idx != -1:
                    dic['midi_index'].append(midi_idx)
                    new_match_idx.append(prev_idx)
                    if prev['xmlNoteID'] != match_id:
                        dic['fixed_trill_idx'].append(midi_idx)
                    prev['used'] = True

        dic['match_index'] += new_match_idx
        dic['match_index'].sort()
        prev_midi_index = dic['midi_index']
        dic['midi_index'] = sorted(
            prev_midi_index, key=lambda prev_midi_index: prev_midi_index['idx'])


def find_ornament_midis(dic, score_time, match_list, midi_notes):
    if len(dic['match_index']) > 0:
        match = match_list[dic['match_index'][0]]
        cand_match_idx = [idx for idx, match in enumerate(match_list) if match['scoreTime'] == score_time]
        new_match_idx = []
        for cand in cand_match_idx:
            cand_match = match_list[cand]
            if not cand_match['used']:
                if (cand_match['xmlNoteID'] == match['xmlNoteID']):
                    midi_idx = find_midi_note_index(
                        midi_notes, cand_match['midiStartTime'], cand_match['midiEndTime'], match['pitch'], ornament=True)
                    if midi_idx != -1:
                        dic['midi_index'].append(midi_idx)
                        new_match_idx.append(cand)
                        if cand_match['xmlNoteID'] != match['xmlNoteID']:
                            dic['fixed_trill_idx'].append(midi_idx)
                        cand_match['used'] = True
                        dic['is_ornament'] = True
        dic['match_index'] += new_match_idx
        new_match_idx = []
        if len(dic['match_index']) >= 2:
            for cand in cand_match_idx:
                cand_match = match_list[cand]
                if not cand_match['used']:
                    if (cand_match['errorIndex'] == 3):
                        midi_idx = find_midi_note_index(
                            midi_notes, cand_match['midiStartTime'], cand_match['midiEndTime'], match['pitch'], ornament=True)
                        if midi_idx != -1:
                            dic['midi_index'].append(midi_idx)
                            new_match_idx.append(cand)
                            if cand_match['xmlNoteID'] != match['xmlNoteID']:
                                dic['fixed_trill_idx'].append(midi_idx)
                            cand_match['used'] = True
                            dic['is_ornament'] = True
                        
        dic['match_index'] += new_match_idx
        dic['match_index'].sort()
        prev_midi_index = dic['midi_index']
        dic['midi_index'] = sorted(
            prev_midi_index, key=lambda prev_midi_index: prev_midi_index['idx'])



def match_xml_midi(xml_index, xml_note, match_list, midi_notes):
    dic = {'match_index': [], 'xml_index': {xml_index, xml_note.pitch[0]}, 'midi_index': [
    ], 'is_trill': False, 'is_ornament': False, 'is_overlapped': xml_note.is_overlapped, 'overlap_xml_index': [], 'unmatched': False, 'fixed_trill_idx': []}

    find_corresp_match_and_midi(
        dic, match_list, midi_notes, xml_note.note_duration.xml_position, xml_note.pitch[0])

    find_trill_midis(dic, match_list, midi_notes)

    find_ornament_midis(
        dic, xml_note.note_duration.xml_position, match_list, midi_notes)

    if len(dic['midi_index']) == 0:
        dic['unmatched'] = True
    else:
        for idx in dic['match_index']:
            match_list[idx]['used'] = True

    return dic


def count_result(index_dict_list, match_list):
    matched_xml_num = 0
    missing_xml_notes_num = 0
    fixed_trill_notes_num = 0
    for result_dic in index_dict_list:
        if len(result_dic['match_index']) != 0:
            matched_xml_num += 1
        else:
            missing_xml_notes_num += 1
        fixed_trill_notes_num += len(result_dic['fixed_trill_idx'])

    pitch_error_notes_num = len([match for match in match_list if (
        not match['used']) and (match['errorIndex'] == 1)])
    extra_midi_notes_num = len([match for match in match_list if (
        not match['used']) and (match['errorIndex'] == 3)])

    return matched_xml_num, extra_midi_notes_num, pitch_error_notes_num, missing_xml_notes_num, fixed_trill_notes_num


if __name__ == '__main__':
    xml_paths = sorted(list(DATASET_PATH.glob('*.xml')))
    perf_paths = sorted(list(DATASET_PATH.glob('*.E*.mid')))
    match_paths = sorted(list(DATASET_PATH.glob('*_match.txt')))

    path_pairs = make_path_pairs(xml_paths, perf_paths, match_paths)

    match_pairs = []

    
    f = open(str(SAVE_PATH) + '/xml-midi_align_result.csv', 'w', encoding='utf-8')
    wr = csv.writer(f)
    wr.writerow(['filename', 'total_xml_notes_num', 'matched_xml_num',
                 'extra_midi_notes_num', 'pitch_error_notes_num', 'missing_xml_notes_num', 'fixed_trill_notes_num'])
    
    for path in path_pairs:
        # get notes and match list
        xml_notes = get_xml_notes(str(path['xml_path']))
        midi_notes = get_midi_notes(str(path['perf_path']))
        match_list, missing_xml_list = read_match_file(str(path['match_path']))

        print(path['match_path'].name)

        # match xml note and midi note
        index_dict_list = []
        for xml_index, xml_note in enumerate(xml_notes):
            dic = match_xml_midi(xml_index, xml_note, match_list, midi_notes)
            index_dict_list.append(dic)
            print(dic)

        pair = {'name': path['match_path'].name, 'xml_notes': xml_notes, 'midi_notes': midi_notes,
                'match_list': match_list, 'missing_xml_list': missing_xml_list, 'index_dict_list': index_dict_list}
        match_pairs.append(pair)

        # record results
        total_xml_notes_num = len(xml_notes)
        matched_xml_num, extra_midi_notes_num, pitch_error_notes_num, missing_xml_notes_num, fixed_trill_notes_num = count_result(
            index_dict_list, match_list)
        
        print(total_xml_notes_num, matched_xml_num, extra_midi_notes_num, pitch_error_notes_num,
              missing_xml_notes_num, fixed_trill_notes_num)

        wr.writerow(
            [pair['name'], str(total_xml_notes_num), str(matched_xml_num), str(extra_midi_notes_num), str(pitch_error_notes_num), str(missing_xml_notes_num), str(fixed_trill_notes_num)])

    f.close()
'''
