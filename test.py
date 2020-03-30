import _pickle as cPickle
'''
data_folder_path = '/home/yoojin/data/emotionDataset/test/save/pairdataset.dat'
data_file_name = 'Clementi.sonatine_op36_no1_mov3.mm_1-end.s012.'
emotion = ['E1.mid.dat', 'E2.mid.dat',
           'E3.mid.dat', 'E4.mid.dat', 'E5.mid.dat']

E1 = []
E2 = []
E3 = []
E4 = []
E5 = []
with open(data_folder_path, 'rb') as f:
    u = cPickle.Unpickler(f)
    pairdataset = u.load()
    for pair in pairdataset.data_pairs:
        if pair.perform_path == '/home/yoojin/data/emotionDataset/test/Clementi.sonatine_op36_no1_mov3.mm_1-end.s012.E1.mid':
            E1 = pair.features['tempo']
        if pair.perform_path == '/home/yoojin/data/emotionDataset/test/Clementi.sonatine_op36_no1_mov3.mm_1-end.s012.E2.mid':
            E2 = pair.features['tempo']
        if pair.perform_path == '/home/yoojin/data/emotionDataset/test/Clementi.sonatine_op36_no1_mov3.mm_1-end.s012.E3.mid':
            E3 = pair.features['tempo']
        if pair.perform_path == '/home/yoojin/data/emotionDataset/test/Clementi.sonatine_op36_no1_mov3.mm_1-end.s012.E4.mid':
            E4 = pair.features['tempo']
        if pair.perform_path == '/home/yoojin/data/emotionDataset/test/Clementi.sonatine_op36_no1_mov3.mm_1-end.s012.E5.mid':
            E5 = pair.features['tempo']
        #print(pair.features.keys())
print(len(E1))
print(len(E2))
print(len(E3))
print(len(E4))
print(len(E5))

print(E1)
'''
emotion_save_path = '/home/yoojin/data/emotionDataset/test/save'
with open(emotion_save_path + '/pairdataset.dat', 'rb') as f:
    u = cPickle.Unpickler(f)
    pairdataset = u.load()

pairs = []
for pair in pairdataset.data_pairs:
    if 's012' in pair.perform_path:
        pairs.append(pair)

for pair in pairs:
    print(pair.features.keys())