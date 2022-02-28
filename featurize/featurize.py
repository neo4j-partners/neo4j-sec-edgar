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

print('Load complete.  Computing targets...')
df['target']=False
df = df.reset_index()
for index, row in df.iterrows():
    reportCalendarOrQuarter = row['reportCalendarOrQuarter']
    filingManager = row['filingManager']
    cusip = row['cusip']
    shares = row['shares']

    if reportCalendarOrQuarter == '03-31-2021':
        targetReportCalendarOrQuarter = '06-30-2021'
    elif reportCalendarOrQuarter == '06-30-2021':
        targetReportCalendarOrQuarter = '09-30-2021'
    elif reportCalendarOrQuarter == '09-30-2021':
        targetReportCalendarOrQuarter = '12-31-2021'
    elif reportCalendarOrQuarter == '12-31-2021':
        targetReportCalendarOrQuarter = '03-31-2022'

    targetRow = df.loc[(df['reportCalendarOrQuarter'] == targetReportCalendarOrQuarter) & (df['filingManager'] == filingManager) & (df['cusip'] == cusip)]
    # We're assuming uniqueness here where it may not be valid.
    # Probably need to go back and ensure we don't download revised filings.
    targetShares = targetRow.head(1)['shares']

    if targetShares > shares:
        df.loc[index, 'target'] = True

print('Splitting data and writing files to disk...')
train = df.loc[df['reportCalendarOrQuarter'] == '03-31-2021']
train = train.append(df.loc[df['reportCalendarOrQuarter'] == '06-30-2021'])
test = df.loc[df['reportCalendarOrQuarter'] == '09-30-2021']
