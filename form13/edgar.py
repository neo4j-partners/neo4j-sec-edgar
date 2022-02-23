import math
import http.client
import io
import csv
import form13
#import database


def downloadDate(date):
    form13Paths = getForm13URLs(date)

    # Download and parse each Form 13
    print('We have ' + str(len(form13Paths)) + ' Form 13 URLs for the date ' + str(date))
    f = []
    for path in form13Paths:
        filings = form13.download(path)
        for filing in filings:
            f.append(filing)

    #print('Done with download.  Writing to BigQuery...')
    #db = database.database()
    #db.insert(f)

    if len(f) > 0:
        with open(str(date) + '.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = f[0].keys())
            writer.writeheader()
            writer.writerows(f)

def getForm13URLs(date):
    print('Composing the URL of the master file...')
    year = str(date.year)
    quarter = 'QTR' + str(math.ceil(date.month / 3))
    date = date.strftime('%Y%m%d')
    path = '/Archives/edgar/daily-index/' + year + '/' + quarter + '/master.' + date + '.idx'
    url = 'https://www.sec.gov' + path
    print('The URL of the master file is ' + url)

    print('Downloading the master file...')
    conn = http.client.HTTPSConnection('www.sec.gov')
    conn.request('GET', path, headers={'User-Agent': 'Neo4j Ben.Lackey@Neo4j.com'})
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    conn.close()

    if response.status == 200 and response.reason == 'OK':
        text = data.decode('windows-1252')
        form4Paths = parseMasterFile(text)
        return form4Paths
    else:
        print('Download failed for master file.')
        return []


def parseMasterFile(text):
    print('Parsing the master file...')
    form4Paths = []
    file = io.StringIO(text)
    reader = csv.reader(file, delimiter='|')
    for row in reader:
        if len(row) != 5:
            # This is a header
            pass
        elif row[2] == '13F-HR':
            # This is a Form 13
            form4Paths.append('/Archives/' + row[4])

    return form4Paths
