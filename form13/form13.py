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
        text = data.decode('utf-8')
        file = io.StringIO(text)
        transactions = parse(file)
        return transactions
    else:
        print('Download failed for form13 file.')
        print(response.status, response.reason)
        return []
    
    
def parse(file):
    for line in file:
        if line.startswith('<SEC-DOCUMENT>'):
            secDocument = line.replace('<SEC-DOCUMENT>', '')
            secDocument = secDocument.strip()
            break

    for line in file:
        if line.startswith('<ACCEPTANCE-DATETIME>'):
            acceptanceDatetime = line.replace('<ACCEPTANCE-DATETIME>', '')
            acceptanceDatetime = acceptanceDatetime.strip()
            break

    for line in file:
        if line.startswith('<?xml version="1.0"?>'):
            break

    contents = file.read()
    file.close()

    contents = contents.split('</XML>')
    edgarSubmission = contents[0]
    edgarSubmission = xmltodict.xmltodict(edgarSubmission)
    print(edgarSubmission)

    informationTable = contents[1]
    informationTable = informationTable.split('<?xml version="1.0"?>')[1]
    informationTable = xmltodict.xmltodict(informationTable)
    print(informationTable)

    '''
    issuerTradingSymbol = ownershipDocument['issuer'][0]['issuerTradingSymbol'][0]
    rptOwnerCik = ownershipDocument['reportingOwner'][0]['reportingOwnerId'][0]['rptOwnerCik'][0]
    rptOwnerName = ownershipDocument['reportingOwner'][0]['reportingOwnerId'][0]['rptOwnerName'][0]

    try:
        isDirector = ownershipDocument['reportingOwner'][0]['reportingOwnerRelationship'][0]['isDirector'][0]
        isDirector = convertToBoolean(isDirector)
    except KeyError:
        isDirector = False
    '''
    

    filings = []
    return filings


def convertToBoolean(s):
    if s == '0':
        return False
    elif s == '1':
        return True
    elif s == 'false':
        return False
    elif s == 'true':
        return True
    else:
        print('Cannot figure out correct value.')
