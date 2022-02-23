from importlib.resources import contents
import xmltodict
import http.client
import io


def download(path):
    conn = http.client.HTTPSConnection('www.sec.gov')
    conn.request('GET', path, headers={'User-Agent': 'Neo4j Ben.Lackey@Neo4j.com'})
    response = conn.getresponse()
    data = response.read()
    conn.close()

    if response.status == 200 and response.reason == 'OK':
        print('http://sec.gov' + path)
        text = data.decode('utf-8')
        file = io.StringIO(text)
        transactions = parse(file)
        return transactions
    else:
        print('Download failed for form13 file.')
        print(response.status, response.reason)
        return []
    
    
def parse(file):
    contents = file.read()
    file.close()

    # hacky way to trim namespace.  Should probably come back and parse properly later
    contents = contents.replace('<ns1:', '<')
    contents = contents.replace('</ns1:', '</')
    
    contents = contents.split('<XML>')
    edgarSubmission = contents[1]
    edgarSubmission = edgarSubmission.split('</XML>')[0]
    edgarSubmission = edgarSubmission.split('\n',1)[1]
    edgarSubmission = xmltodict.xmltodict(edgarSubmission)

    informationTable = contents[2]
    informationTable = informationTable.split('</XML>')[0]
    informationTable = informationTable.split('\n',1)[1]
    informationTable = xmltodict.xmltodict(informationTable)

    reportCalendarOrQuarter = edgarSubmission['formData'][0]['coverPage'][0]['reportCalendarOrQuarter'][0]
    fillingManager = edgarSubmission['formData'][0]['coverPage'][0]['filingManager'][0]['name'][0]

    filings = []
    for infoTable in informationTable['infoTable']:
        filing = {}
        filing['fillingManager'] = fillingManager
        filing['reportCalendarOrQuarter'] = reportCalendarOrQuarter
        filing['nameOfIssuer'] = infoTable['nameOfIssuer'][0]
        filing['cusip'] = infoTable['cusip'][0]
        filing['value'] = infoTable['value'][0]
        filing['shares'] = infoTable['shrsOrPrnAmt'][0]['sshPrnamt'][0]
        filings.append(filing)

    return filings
