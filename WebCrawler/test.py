import pickle

f = pickle.load(open("failed.p", 'rb'))
p = pickle.load(open("populars.p", 'rb'))
print(str(len(p)) + ' populars out of ' + str(len(p) + len(f)) + ' total tried')
print(str(1.0 * len(p) / (1.0 * (len(p) + len(f)))))
