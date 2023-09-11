# Neo4j SEC EDGAR
This repository contains scripts to download SEC EDGAR data and format it for Neo4j loading and analytics. Specially to

1. obtain information on investment managers and the companies they purchase stock from using Form 13. An FAQ on Form 13 is available [here](https://www.sec.gov/divisions/investment/13ffaq.htm).
2. obtain text from 10K filings for a fraction of the above companies

EDGAR uses HTTP for access.  A writeup on that is [here](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm).

This dataset is used in the following hands on lab(s):
* [hands-on-lab-neo4j-and-vertex-ai](https://github.com/neo4j-partners/hands-on-lab-neo4j-and-vertex-ai)

## Setup
Install dependencies:

    sudo apt update
    sudo apt -y install python3 python3-dev
    sudo apt -y install screen wget
    sudo python3 get-pip.py
    sudo pip3 install --upgrade google-api-python-client
    sudo pip3 install --upgrade pandas tqdm xmltodict

## Download Form13
To start the form 13 downloader run this:

```python form13-download.py```

```
optional arguments:
-s, --start-date, Start date in the format yyyy-mm-dd (default: 2022-01-01)
-e, --end-date, End date in the format yyyy-mm-dd (default: 2023-08-01)
-o, --output-directory, Local directory to write forms to (default: data/form13-raw/)
```

## Parse & Format
Once you have all the raw forms downloaded, this file will parse and format them into a csv file.

```python form13-parse-and-format.py -p 4```

```
optional arguments:
-i, --input-directory, Directory containing raw EDGAR files (default: data/form13-raw/)
-o, --output-file, Local path + file name to write formatted csv too (default: data/form13.csv)
-p, --top-periods, Only include data from `n` most recent report quarters (default: None)
```

## Download, Parse, and Format 10K Filings
This next program will use company names from the form13 parsed and formatted file outputed above to search for and download 10k files.  It will then parse out relevant 10k section text and save to json files, one json file per company. See __10k Notes__ below for more details on the reasoning behind parsing and section selection. 


```filing10k-download-parse-format.py```

```
optional arguments:
  -i,  --input-file, Formatted Form13 csv file to pull company names from (default: data/form13.csv)
  -o, --output-directory, Local path to write formatted text to (default: data/form10k-clean)
  -t , --temp-directory, Directory to temporarily store raw SEC 10K files (default: data/temp-10k)
  -u, --user-agent, Email address to use for user agent in SEC EDGAR calls (default: sales@neo4j.com)
  -s, --start-date, Start date in the format yyyy-mm-dd (default: 2022-01-01)
  -e, --end-date, End date in the format yyyy-mm-dd (default: 2023-01-01)

```

Once that is done, go ahead and zip the json files  __(TODO: Command)__

## Create Single Day Sample
We need a daily sample of form13 data for use in exploration and learning in the labs.  You can run the python notebook `form13-one-day-sample.ipynb` to create that. It will make a file `./data/form13-v2-2023-05-11.csv`.


## Copy Data to Google Cloud Storage Bucket __(TODO: Update for three files above)__
Now that you have form13s and 10K filings you can push them to Google cloud storage. 

To do so, setup the environment variables:

    gcloud init

Now copy the data:

    gsutil cp form13 gs://neo4j-datasets/form13/
    gsutil cp test.csv gs://neo4j-datasets/form13/

## 10K Notes __(TODO: Copy Explanations from Other Repo)__