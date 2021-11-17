import sched
import datetime
import time
import edgar

class downloader:
    schedule = sched.scheduler(time.time, time.sleep)

    # It looks like master files are showing up right around 10:03 PM with some outliers.
    # Downloading at 10:30 PM should give us enough room.
    downloadTime = datetime.time(22,30,0)

    def __init__(self):
        today = datetime.date.today()
        downloadDateTime = datetime.datetime.combine(today, self.downloadTime)
        downloadTime = time.mktime(downloadDateTime.timetuple())

        print('Going to run EDGAR download next at ' + downloadDateTime.isoformat())
        self.schedule.enterabs(downloadTime, 0, self.download, ())
        self.schedule.run()

    def download(self):
        print('Running EDGAR download at ' + datetime.datetime.today().isoformat())
        edgar.downloadDate(datetime.date.today())
        print('Done with EDGAR download at ' + datetime.datetime.today().isoformat())

        # Reschedule the download to run again tomorrow.
        # Assume the system clock uses NY time.
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        downloadDateTime = datetime.datetime.combine(tomorrow, self.downloadTime)
        downloadTime = time.mktime(downloadDateTime.timetuple())

        print('Going to run EDGAR download next at ' + downloadDateTime.isoformat())
        self.schedule.enterabs(downloadTime, 0, self.download, ())


downloader()