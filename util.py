import datetime
import pytz


def getCurrentTime():
    myCurrentTime = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    return myCurrentTime
