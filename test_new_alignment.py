from pathlib import Path
from .musicxml_parser import MusicXMLDocument
from . import xml_utils
from .midi_utils import midi_utils
from . import xml_midi_matching as matching

import csv
from tqdm import tqdm

#DATASET_PATH = Path('/home/yoojin/data/20200320/total_dataset/')

DATASET_PATH = Path('/home/yoojin/data/20200320/20200321_test_xml_midi/')
SAVE_PATH = Path('/home/yoojin/data/20200320/20200321_test_xml_midi/save')


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
    match_txt = matching.read_match_txt(match_path)
    match_list = match_txt['match_list']
    missing_xml_list = match_txt['missing']

    return match_list, missing_xml_list


def count_matched_notes(pair):
    matched = 0
    unmatched = 0
    for dic in pair['index_dict_list']:
        if len(dic['match_index']) == 0:
            unmatched += 1
        else:
            matched += 1
    
    return matched, unmatched


if __name__ == '__main__':
    xml_paths = sorted(list(DATASET_PATH.glob('*.xml')))
    perf_paths = sorted(list(DATASET_PATH.glob('*.E*.mid')))
    match_paths = sorted(list(DATASET_PATH.glob('*_match.txt')))

    path_pairs = make_path_pairs(xml_paths, perf_paths, match_paths)

    # start to record matching result before code
    print('start to record matching result before code')
    f = open(str(SAVE_PATH) + '/result_before_code.csv', 'w', encoding='utf-8')
    wr = csv.writer(f)
    wr.writerow(['filename', 'xml_notes', 'midi_notes',
                'matched_midi_notes', 'missing_xml_notes'])

    for path in tqdm(path_pairs):
        xml_notes = get_xml_notes(str(path['xml_path']))
        midi_notes = get_midi_notes(str(path['perf_path']))
        match_list, missing_xml_list = read_match_file(str(path['match_path']))

        wr.writerow([path['match_path'].name, str(len(xml_notes)), str(
            len(midi_notes)), str(len(match_list)), str(len(missing_xml_list))])

    f.close()

    # match xml_note to matchlist
    print('match xml_note to matchlist')
    match_pairs = []
    for path in tqdm(path_pairs):
        xml_notes = get_xml_notes(str(path['xml_path']))
        midi_notes = get_midi_notes(str(path['perf_path']))
        match_list, missing_xml_list = read_match_file(str(path['match_path']))

        print(path['match_path'].name)

        index_dict_list = []
        for xml_index, xml_note in enumerate(xml_notes):
            measure = xml_note.measure_number
            score_time = xml_note.note_duration.xml_position
            pitch = xml_note.pitch[0]

            dic = {'match_index': [], 'xml_index': [xml_index], 'midi_index': [],
                'is_trill': False, 'is_overlapped': False, 'overlap_xml_index': []}
            for match_index, match in enumerate(match_list):
                #if match['xmlNoteID'] != '*' and not 'X' in match['xmlNoteID'].split('-')[1]:
                if match['xmlNoteID'] != '*':
                    #if (measure == int(match['xmlNoteID'].split('-')[1])) and (score_time == match['scoreTime']) and (pitch == match['pitch']):
                    if (score_time == match['scoreTime']) and (pitch == match['pitch']):
                        dic['match_index'].append(match_index)

            if len(dic['match_index']) > 1:
                # 미디 여러 개 - xml 하나라서 match가 여러 개 뜰 경우
                dic['is_trill'] = True

            index_dict_list.append(dic)
            #print(dic)
        pair = {'name': path['match_path'].name, 'xml_notes': xml_notes, 'midi_notes': midi_notes,
                'match_list': match_list, 'missing_xml_list': missing_xml_list, 'index_dict_list': index_dict_list}
        match_pairs.append(pair)
    
    # start to record match result of xml_note to matchlist
    print('start to record match result of xml_note to matchlist')
    f = open(str(SAVE_PATH) + '/result_xml_note_matchlist.csv', 'w', encoding='utf-8')
    wr = csv.writer(f)
    wr.writerow(['filename', 'matched_midi_notes', 'unmatched_xml_notes'])
    for pair in tqdm(match_pairs):
        matched, unmatched = count_matched_notes(pair)
        wr.writerow([pair['name'], str(matched), str(unmatched)])
    f.close()

