import pytz
import datetime
import time
from event import *
from discord import *
import pickle
import schedule


def dumpEventState(event_file, event_data):
    try:
        f = open(event_file, "wb")
        pickle.dump(event_data, f)
        f.close()
    except Exception as e:
        print("Failed to dump current event state {}".format(str(e)))


# retrieve stored state for events
eventList = EventList()
eventRetriever = EventRetriever()


try:
    eventFile = open('events', "rb")
    events = pickle.load(eventFile)
    if len(events) > 0:
        eventList.enqueueEvents(events)
    eventFile.close()
except FileNotFoundError:
    pass


events = eventRetriever.populateEventData()
eventList.enqueueEvents(events)

# sort event list by
finalList = eventList.getEventList()

# dispatch thread to dump state every 30 minutes
schedule.every(15).minutes.do(
    dumpEventState, event_file="event.txt", event_data=finalList)


while True:
    # run any pending jobs that have been scheduled
    schedule.run_pending()

    # extract current time
    myCurrentTime = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))

    # identify all events occuring in the next 15 minutes that have not already been notified
    eventsIn15Minutes = [e for e in finalList if (myCurrentTime < e.event_start) and (
        e.event_start - myCurrentTime) <= datetime.timedelta(minutes=15) and not e.alreadyNotified()]

    if len(eventsIn15Minutes) > 0:
        for event in eventsIn15Minutes:
            remainingTime = event.event_start - \
                myCurrentTime + datetime.timedelta(seconds=1)
            hours, remainder = divmod(remainingTime.seconds, 3600)
            minutes, second = divmod(remainder, 60)

            print("{} - will occur in {} minute(s) and {} second(s)".format(event.event_name,
                                                                            minutes, second))
            resp = DiscordNotification().notify(event, minutes, second)
            if resp.status_code in [200, 204]:
                event.setNotifyStatus(True)
    else:
        print("No events happening in the next 15 minutes")

    time.sleep(1)
