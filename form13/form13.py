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
    for x in 'ns1', 'ns2', 'ns3', 'ns4', 'n1', 'n2', 'n3', 'n4':
        contents = contents.replace('<' + x + ':', '<')
        contents = contents.replace('</' + x + ':', '</')
    
    contents = contents.split('<XML>')
    edgarSubmission = contents[1]
    edgarSubmission = edgarSubmission.split('</XML>')[0]
    edgarSubmission = edgarSubmission.split('\n',1)[1]
    edgarSubmission = xmltodict.xmltodict(edgarSubmission)

    reportCalendarOrQuarter = edgarSubmission['formData'][0]['coverPage'][0]['reportCalendarOrQuarter'][0]
    filingManager = edgarSubmission['formData'][0]['coverPage'][0]['filingManager'][0]['name'][0]

    informationTable = contents[2]
    informationTable = informationTable.split('</XML>')[0]
    informationTable = informationTable.split('\n',1)[1]
    try:
        informationTable = xmltodict.xmltodict(informationTable)
    except:
        print('Error parsing information table.')
        print(informationTable)
        exit()

    filings = []
    for infoTable in informationTable['infoTable']:
        # Only want stock holdings, not options
        if(infoTable['shrsOrPrnAmt'][0]['sshPrnamtType'][0]!='SH'):
            pass
        # Only want holdings over $10m
        elif(float(infoTable['value'][0])*1000<10000000):
            pass
        # Only want common stock
        elif(infoTable['titleOfClass'][0]!='COM'):
            pass
        else:
            filing = {}
            filing['filingManager'] = filingManager
            filing['reportCalendarOrQuarter'] = reportCalendarOrQuarter
            filing['nameOfIssuer'] = infoTable['nameOfIssuer'][0]
            filing['cusip'] = infoTable['cusip'][0]
            filing['value'] = infoTable['value'][0] + '000'
            filing['shares'] = infoTable['shrsOrPrnAmt'][0]['sshPrnamt'][0]
            filings.append(filing)

    return filings
