import math
import http.client
import io
import csv
import form4
import database


def downloadDate(date):
    form4URLs = getForm4URLs(date)

    # Download and parse each Form 4
    print('We have ' + str(len(form4URLs)) + ' Form 4 URLs for the date ' + str(date))
    t = []
    for url in form4URLs:
        transactions = form4.download(url)
        for transaction in transactions:
            t.append(transaction)

    print('Done with download.  Writing to BigQuery...')
    db = database.database()
    db.insert(t)


def getForm4URLs(date):
    print('Composing the URL of the master file...')
    year = str(date.year)
    quarter = 'QTR' + str(math.ceil(date.month / 3))
    date = date.strftime('%Y%m%d')
    path = '/Archives/edgar/daily-index/' + year + '/' + quarter + '/master.' + date + '.idx'
    url = 'https://www.sec.gov' + path
    print('The URL of the master file is ' + url)

    print('Downloading the master file...')
    conn = http.client.HTTPSConnection('www.sec.gov')
    conn.request('GET', path)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    conn.close()

    if response.status == 200 and response.reason == 'OK':
        text = data.decode('windows-1252')
        form4URLs = parseMasterFile(text)
        return form4URLs
    else:
        print('Download failed for master file.')
        return []


def parseMasterFile(text):
    print('Parsing the master file...')
    form4URLs = []
    file = io.StringIO(text)
    reader = csv.reader(file, delimiter='|')
    for row in reader:
        if len(row) != 5:
            # This is a header
            pass
        elif row[2] == '4':
            # This is a Form 4
            form4URLs.append('https://www.sec.gov/Archives/' + row[4])

    return form4URLs
