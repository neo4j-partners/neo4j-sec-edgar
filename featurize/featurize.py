from os import listdir
import pandas

form13 = pandas.DataFrame()
for file in listdir('../data/'):
    if file.endswith('.csv'):
        print('Processing file: ' + file)
        form13.append(pandas.read_csv('../data/' + file))

print(form13)