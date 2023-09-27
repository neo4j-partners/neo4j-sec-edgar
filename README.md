# neo4-sec-edgar
This repository contains scripts to download SEC EDGAR data and format it for Neo4j loading and analytics. Specially to:

1. form-13: Obtain information on investment managers and the companies they purchase stock from using Form 13. An FAQ on Form 13 is available [here](https://www.sec.gov/divisions/investment/13ffaq.htm).
2. form-10-k: Obtain text from 10-K filings for a fraction of the above companies

EDGAR uses HTTP for access.  A writeup on that is [here](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm).

## Setup
To run the scripts you will need to install dependencies:

    sudo apt update
    sudo apt -y install python3 python3-dev
    sudo apt -y install screen wget
    sudo python3 get-pip.py
    sudo pip3 install --upgrade google-api-python-client
    sudo pip3 install --upgrade pandas tqdm xmltodict beautifulsoup4 secedgar
