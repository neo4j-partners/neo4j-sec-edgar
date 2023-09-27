# neo4-sec-edgar
This repository contains scripts to download SEC EDGAR data and format it for Neo4j loading and analytics. Specially to:

* [form13](form13): Obtain information on investment managers and the companies they purchase stock from using Form 13. An FAQ on Form 13 is available [here](https://www.sec.gov/divisions/investment/13ffaq.htm).
* [form10-k](form10-k): Obtain text from 10-K filings for a fraction of the above companies

EDGAR uses HTTP for access.  A writeup on that is [here](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm).

## Setup
To run the scripts you will need to install dependencies:

    sudo apt update
    sudo apt -y install python3 python3-dev
    sudo apt -y install screen wget
    sudo python3 get-pip.py
    sudo pip3 install --upgrade google-api-python-client
    sudo pip3 install --upgrade pandas tqdm xmltodict beautifulsoup4 secedgar

## Download
You can now run the scripts for each form.

## Copy Data to Google Cloud Storage Bucket
Now that you have Form-13 and Form 10-K you can push them to Google cloud storage.

To do so, set the environment variables:

    gcloud init

Now copy the Form 13 data:

    gsutil cp data/form13.csv gs://neo4j-datasets/hands-on-lab/form13-2023.csv
    gsutil cp data/form13-2023-05-11.csv gs://neo4j-datasets/hands-on-lab/form13-2023-05-11.csv
    # to do - https://github.com/neo4j-partners/neo4j-sec-edgar/issues/4

And copy Form 10-K:

    gsutil cp data/form10k.zip gs://neo4j-datasets/hands-on-lab/form10k.zip
    