from os import listdir
import pandas

df = pandas.DataFrame()
for file in listdir('../data/'):
    if file.endswith('.csv'):
        print('Processing file: ' + file)
        df = df.append(pandas.read_csv('../data/' + file))

# This wouldn't be an SEC dataset without a data quality issue.  
# In this case, we have some report dates of: '3-31-2021' that should be '03-31-2021'
# Let's fix that...
df.replace('3-31-2021', '03-31-2021', inplace=True)

# We've got a bunch of updated filings.  We're just going to ignore those.
# So, the only data we want is from: '03-31-2021', '06-30-2021', '09-30-2021', '12-31-2021'
df = df.loc[df['reportCalendarOrQuarter'].str.contains('2021')]








# split the data
train = df.loc[df['reportCalendarOrQuarter'] == '03-31-2021']
train = train.append(df.loc[df['reportCalendarOrQuarter'] == '06-30-2021'])
test = df.loc[df['reportCalendarOrQuarter'] == '09-30-2021']
