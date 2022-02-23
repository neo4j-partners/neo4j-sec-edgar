# form13
The form 13 FAQ is [here](https://www.sec.gov/divisions/investment/13ffaq.htm).

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

## Run
To start the downloader, run this:

    screen -S edgar
    python3 download.py

Then type ^ad to detach.
