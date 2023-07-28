# neo4j-sec-edgar-form13
These scripts download SEC EDGAR data and format it for Neo4j loading and analytics.  They operate specifically on SEC Form 13.  An FAQ on Form 13 is available [here](https://www.sec.gov/divisions/investment/13ffaq.htm). EDGAR uses HTTP for access.  A writeup on that is [here](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm).

This dataset is used by one hands on labs:
* [hands-on-lab-neo4j-and-sagemaker](https://github.com/neo4j-partners/hands-on-lab-neo4j-and-sagemaker)
* [hands-on-lab-neo4j-and-vertex-ai](https://github.com/neo4j-partners/hands-on-lab-neo4j-and-vertex-ai)

## Setup
Install dependencies:

    sudo apt update
    sudo apt -y install python3 python3-dev
    sudo apt -y install screen wget
    sudo python3 get-pip.py
    sudo pip3 install --upgrade google-api-python-client
    sudo pip3 install --upgrade pandas
    sudo pip3 install --upgrade tqdm

## Download
To start the downloader, run this:

```python download.py```

```
optional arguments:
-s, --start-date, Start date in the format yyyy-mm-dd (default: 2022-01-01)
-e, --end-date, End date in the format yyyy-mm-dd (default: 2023-07-11)
-o, --output-directory, Local directory to write forms to (default: data/form13-raw/)
```

## Parse & Format
Once you have all the raw forms downloaded, this notebook will parse and format them into a csv file.

```python parse-and-format.py -p 4```

```
optional arguments:
-i, --input-directory, Directory containing raw EDGAR files (default: data/form13-raw/)
-o, --output-file, Local path + file name to write formatted csv too (default: data/form13.csv)
-p, --top-periods, Only include data from `n` most recent report quarters (default: None)
```


## Create Machine Learning Data __(TODO: Complete)__
Create datasets for training a Machine learning model to predict new stock purchases

```python format-ml-data.py```

## Copy data to bucket __(TODO: Update)__
Setup the environment variables:

    gcloud init

Now copy the data:

    gsutil cp train.csv gs://neo4j-datasets/form13/
    gsutil cp test.csv gs://neo4j-datasets/form13/

## Combine train and test __(TODO: Update)__
If you want to combine the train and test datasets you can run:

    import pandas
    train=pandas.read_csv('train.csv')
    test=pandas.read_csv('test.csv')
    form13=pandas.concat([train,test])
    form13.to_csv('form13.csv',index=False)

Then copy it to a bucket with the command:

    gsutil cp form13.csv gs://neo4j-datasets/form13/