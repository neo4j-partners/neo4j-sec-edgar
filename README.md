# Neo4j SEC EDGAR
This repository contains scripts to download SEC EDGAR data and format it for Neo4j loading and analytics. Specially to 


1. obtain information on investment managers and the companies they purchase stock from using Form 13 (scripts in  `form13/` directory). An FAQ on Form 13 is available [here](https://www.sec.gov/divisions/investment/13ffaq.htm).
2. obtain text from 10K filings for a fraction of the above companies (scripts in  `filing10k/` directory)


 EDGAR uses HTTP for access.  A writeup on that is [here](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm).

This dataset will be used in the following hands on lab(s):
* [hands-on-lab-neo4j-and-vertex-ai](https://github.com/neo4j-partners/hands-on-lab-neo4j-and-vertex-ai)

## Setup
Install dependencies:

    sudo apt update
    sudo apt -y install python3 python3-dev
    sudo apt -y install screen wget
    sudo python3 get-pip.py
    sudo pip3 install --upgrade google-api-python-client
    sudo pip3 install --upgrade pandas tqdm xmltodict

## Download
To start the downloader, change to the form13/ directory 

```cd form13/```

Then run this:

```python download.py```

```
optional arguments:
-s, --start-date, Start date in the format yyyy-mm-dd (default: 2022-01-01)
-e, --end-date, End date in the format yyyy-mm-dd (default: 2023-07-11)
-o, --output-directory, Local directory to write forms to (default: data/form13-raw/)
```

## Parse & Format
Once you have all the raw forms downloaded, this file will parse and format them into a csv file.

```python parse-and-format.py -p 4```

```
optional arguments:
-i, --input-directory, Directory containing raw EDGAR files (default: data/form13-raw/)
-o, --output-file, Local path + file name to write formatted csv too (default: data/form13.csv)
-p, --top-periods, Only include data from `n` most recent report quarters (default: None)
```

## Download, Parse and Format 10K Filings __(TODO: Update)__


## Copy data to bucket __(TODO: Update)__
Setup the environment variables:

    gcloud init

Now copy the data:

    gsutil cp train.csv gs://neo4j-datasets/form13/
    gsutil cp test.csv gs://neo4j-datasets/form13/