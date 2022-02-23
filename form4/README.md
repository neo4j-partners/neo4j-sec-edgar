# form4
To start the downloader, run this:

    screen -S edgar
    python3 downloader.py

Then type ^ad to detach.

To get historical data, you'll need to start one of these too:

    screen -S edgar-historical
    python3 downloadAll.py

Then type ^ad to detach.