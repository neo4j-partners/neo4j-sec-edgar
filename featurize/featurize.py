from os import listdir
import pandas

form13 = pandas.DataFrame()
for file in listdir('../data/'):
    form13.append(pandas.read_csv('../data/' + file))

print(form13)