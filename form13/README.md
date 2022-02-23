# form13
The form 13 FAQ is [here](https://www.sec.gov/divisions/investment/13ffaq.htm).

## Setup
Install dependencies:

    sudo apt update
    sudo apt -y install python3 python3-dev python3-venv python3-pip
    sudo pip3 install --upgrade google-api-python-client
    sudo pip3 install --upgrade google-cloud-bigquery

## Run
To start the downloader, run this:

    screen -S edgar
    python3 downloader.py

Then type ^ad to detach.
