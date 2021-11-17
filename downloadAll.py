import datetime
import edgar

def run():
    date = datetime.date.today()

    while date > datetime.date(2000,12,31):
        date = date - datetime.timedelta(days=1)
        print(date)
        edgar.downloadDate(date)

run()