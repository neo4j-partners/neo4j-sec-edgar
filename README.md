# neo4j-edgar
These scripts download SEC EDGAR data and load that into Neo4j.  They operate specifically on SEC Form 13.  An FAQ on Form 13 is available [here](https://www.sec.gov/divisions/investment/13ffaq.htm).

EDGAR uses HTTP for access.  A writeup on that is [here](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm).

## Setup
Install dependencies:

    sudo apt update
    sudo apt -y install python3 python3-dev python3-venv 
    sudo apt -y install screen wget
    sudo python3 get-pip.py
    sudo pip3 install --upgrade google-api-python-client
    sudo pip3 install --upgrade google-cloud-bigquery

Setup the enviromental variables:

    gcloud init

## Download
To start the downloader, run this:

    cd download
    screen -S edgar
    python3 download.py

Then type ^ad to detach.

## Featurize
Once you have all the CSVs per date, you're going to want to combine and featurize them.  This will spit out a single CSV.

    cd featurize
    python3 featurize.py

## Copy data to bucket

    gsutil cp *.csv gs://neo4j-datasets

## Loading data into Neo4j
First off, create an AuraDS instance.

To load the dataset run:

    LOAD CSV WITH HEADERS FROM 'https://storage.googleapis.com/neo4j-datasets/2022-02-17.csv' AS row
    MERGE (m:Manager {filingManager:row.filingManager})
    MERGE (c:Company {nameOfIssuer:row.nameOfIssuer, cusip:row.cusip})
    MERGE (m)-[r1:Owns {value:toInteger(row.value), shares:toInteger(row.shares), reportCalendarOrQuarter:row.reportCalendarOrQuarter}]->(c)

To delete the contents of the database, you can run:

    MATCH (n)
    DETACH DELETE n;
