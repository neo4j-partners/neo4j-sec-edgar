from os import listdir
import pandas

df = pandas.DataFrame()
for file in listdir('../data/'):
    if file.endswith('.csv'):
        print('Processing file: ' + file)
        df = df.append(pandas.read_csv('../data/' + file))

print('Cleaning data...')

# This wouldn't be an SEC dataset without a data quality issue.  
# In this case, we have some report dates of: '3-31-2021' that should be '03-31-2021'
# Let's fix that...
df.replace('3-31-2021', '03-31-2021', inplace=True)

# We've got a bunch of updated filings.  We're just going to ignore those.
# So, the only data we want is from: '03-31-2021', '06-30-2021', '09-30-2021', '12-31-2021'
df = df.loc[df['reportCalendarOrQuarter'].str.contains('2021')]

print('Computing targets...')

def computeTargetReportCalendarOrQuarter(reportCalendarOrQuarter):
    if reportCalendarOrQuarter == '03-31-2021':
        targetReportCalendarOrQuarter = '06-30-2021'
    elif reportCalendarOrQuarter == '06-30-2021':
        targetReportCalendarOrQuarter = '09-30-2021'
    elif reportCalendarOrQuarter == '09-30-2021':
        targetReportCalendarOrQuarter = '12-31-2021'
    elif reportCalendarOrQuarter == '12-31-2021':
        targetReportCalendarOrQuarter = '03-31-2022'
    return targetReportCalendarOrQuarter

df['targetReportCalendarOrQuarter'] = df.apply(lambda row: computeTargetReportCalendarOrQuarter(row['reportCalendarOrQuarter']), axis=1)

def computeTarget(df, row):
    targetRow = df.loc[(df['reportCalendarOrQuarter'] == row['targetReportCalendarOrQuarter']) & (df['filingManager'] == row['filingManager']) & (df['cusip'] == row['cusip'])]    
    # We're assuming uniqueness here where it may not be valid.
    # Probably need to go back and ensure we don't download revised filings.
    try:
        targetShares = targetRow.head(1)['shares'].iloc[0]
    except:
        targetShares = 0
    if targetShares > row['shares']:
        return True
    return False

df['target'] = df.apply(lambda row: computeTarget(df, row), axis=1)
df = df.drop(columns=['targetReportCalendarOrQuarter'])

print('Splitting data and writing files to disk...')
train = df.loc[df['reportCalendarOrQuarter'] == '03-31-2021']
train = train.append(df.loc[df['reportCalendarOrQuarter'] == '06-30-2021'])
train.to_csv('../data/train.csv', index=False)

test = df.loc[df['reportCalendarOrQuarter'] == '09-30-2021']
test.to_csv('../data/test.csv', index=False)
