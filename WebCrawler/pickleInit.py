import pickle

s = set()
s1 = set()
pickle.dump(s1, open("RENAMETHIS1.p", 'wb'))
pickle.dump(s, open("RENAMETHIS.p", 'wb'))
