import datetime
import edgar


def run():
    date = datetime.date.today()
    
    while date >= datetime.date(2021, 1, 1):
        date = date - datetime.timedelta(days=1)
        print(date)
        edgar.downloadDate(date)
        break

run()
