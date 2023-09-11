# Neo4j SEC EDGAR
This repository contains scripts to download SEC EDGAR data and format it for Neo4j loading and analytics. Specially to

1. Obtain information on investment managers and the companies they purchase stock from using Form 13. An FAQ on Form 13 is available [here](https://www.sec.gov/divisions/investment/13ffaq.htm).
2. Obtain text from 10K filings for a fraction of the above companies

EDGAR uses HTTP for access.  A writeup on that is [here](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm).

This dataset is used in the following hands-on lab(s):
* [hands-on-lab-neo4j-and-vertex-ai](https://github.com/neo4j-partners/hands-on-lab-neo4j-and-vertex-ai)

## Setup
Install dependencies:

    sudo apt update
    sudo apt -y install python3 python3-dev
    sudo apt -y install screen wget
    sudo python3 get-pip.py
    sudo pip3 install --upgrade google-api-python-client
    sudo pip3 install --upgrade pandas tqdm xmltodict beautifulsoup4 secedgar

## Download Form13
To start the Form13 downloader run this:

```python form13-download.py```

```
optional arguments:
-s, --start-date, Start date in the format yyyy-mm-dd (default: 2022-01-01)
-e, --end-date, End date in the format yyyy-mm-dd (default: 2023-08-01)
-o, --output-directory, Local directory to write forms to (default: data/form13-raw/)
```

## Parse & Format Form13
Once you have all the raw forms downloaded, this file will parse and format them into a csv file.

```python form13-parse-and-format.py -p 4```

```
optional arguments:
-i, --input-directory, Directory containing raw EDGAR files (default: data/form13-raw/)
-o, --output-file, Local path + file name to write formatted csv too (default: data/form13.csv)
-p, --top-periods, Only include data from `n` most recent report quarters (default: None)
```

## Download, Parse, and Format 10K Filings
This next program will use company names from the form13 parsed and formatted file (outputed above) to search for and download 10K files.  It will then parse out relevant 10K item text and save to json files, one json file per company. See __10K Notes__ below for more details on the reasoning behind parsing and item selection.

```python filing10k-download-parse-format.py```

```
optional arguments:
  -i,  --input-file, Formatted Form13 csv file to pull company names from (default: data/form13.csv)
  -o, --output-directory, Local path to write formatted text to (default: data/form10k-clean)
  -t , --temp-directory, Directory to temporarily store raw SEC 10K files (default: data/temp-10k)
  -u, --user-agent, Email address to use for user agent in SEC EDGAR calls (default: sales@neo4j.com)
  -s, --start-date, Start date in the format yyyy-mm-dd (default: 2022-01-01)
  -e, --end-date, End date in the format yyyy-mm-dd (default: 2023-01-01)

```

Once that is done, go ahead and zip the files:

```
cd data
zip -r form10k-clean.zip form10k-clean/
cd ..
```

## Create Form13 Single Day Sample
We need a daily sample of form13 data for use in exploration and learning in the labs.  You can run the Python notebook `form13-one-day-sample.ipynb` to create that. It will make a file `./data/form13-2023-05-11.csv`.


## Copy Data to Google Cloud Storage Bucket
Now that you have form13s and 10K filings you can push them to Google cloud storage.

To do so, set the environment variables:

    gcloud init

Now copy the data:

    gsutil cp data/form13.csv gs://neo4j-datasets/form13/form13-v3.csv
    gsutil cp data/form10k-clean.zip gs://neo4j-datasets/form10k/form10k-v2-clean.zip
    gsutil cp data/form13-2023-05-11.csv gs://neo4j-datasets/form13/form13-v3-2023-05-11.csv

## 10K Notes

A [10K](https://www.investor.gov/introduction-investing/investing-basics/glossary/form-10-k) is a comprehensive report filed annually by a publicly traded company about its financial performance and is required by the U.S. Securities and Exchange Commission (SEC). The report contains a comprehensive overview of the company's business and financial condition and includes audited financial statements. While 10Ks contain images and table figures, they primarily consist of free-form text which is what we are interested in extracting here.

Raw 10K reports are structured in iXBRL, or Inline eXtensible Business Reporting Language, which is extremely verbose, containing more markup than actual text content, [here is an example from APPLE](https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/0000320193-22-000108.txt).

This makes raw 10K files very large, unwieldy, and inefficient for direct application of LLM or text embedding services. For this reason, the program contained here, `filing10k-download-parse-format.py`, applies regex and NLP to parse out as much iXBRL and unnecessary content as possible to make 10K text useful.

In addition, `filing10k-download-parse-format.py` also extracts only a subset of items from the 10K that we feel are most relevant for initial exploration and experimentation.  These are sections that discuss the overall business outlook and risk factors, specifically:

* __Item 1 – Business__
This describes the business of the company: who and what the company does, what subsidiaries it owns, and what markets it operates in. It may also include recent events, competition, regulations, and labor issues. (Some industries are heavily regulated, have complex labor requirements, which have significant effects on the business.) Other topics in this section may include special operating costs, seasonal factors, or insurance matters.
* __Item 1A – Risk Factors__
Here, the company lays out anything that could go wrong, likely external effects, possible future failures to meet obligations, and other risks disclosed to adequately warn investors and potential investors.
* __Item 7 – Management's Discussion and Analysis of Financial Condition and Results of Operations__
Here, management discusses the operations of the company in detail by usually comparing the current period versus the prior period. These comparisons provide a reader an overview of the operational issues of what causes such increases or decreases in the business.
* __Item 7A – Quantitative and Qualitative Disclosures about Market Risks__
