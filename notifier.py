import requests
import lxml.html
import re
import json
import pytz
import datetime
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
from event import *

eventList = EventList()
eventRetriever = EventRetriever()

calendar_data, calendar_events, calendar_msgs = eventRetriever.getEventData()

for category, categoryEvents in calendar_data.items():
    for month, monthEvents in categoryEvents.items():
        for day, dayEvents in monthEvents.items():
            if type(dayEvents) is list:
                dayEvents = dayEvents[0]
            for eventMetadata, events in dayEvents.items():
                category_name = None
                event_start = None
                event_end = None
                event_time = None
                event_icon = None
                event_ilevel = None
                event_name = None

                # Check if the events are a list. If so, then all events in this category do not have an ilevel and eventMetadata is the event ID, else its the item level
                if(type(events) is list):
                    for t in events:
                        if "Proving Ground" not in calendar_events[eventMetadata][0]:
                            category_name = calendar_msgs[category][0]
                            event_time = t
                            event_icon = calendar_events[eventMetadata][1]
                            event_ilevel = None
                            event_name = calendar_events[eventMetadata][0]

                            if "-" in event_time:
                                event_start, event_end = event_time.split(
                                    "-")
                            else:
                                event_start = event_time

                            newEvent = Event(
                                month, day, eventMetadata, event_start, event_name, category_name, event_icon, event_ilevel, event_end)
                            eventList.enqueueEvent(newEvent)

                # Else, we have an item level requirement for the events in this category
                else:
                    for eventID, event in events.items():
                        for t in event:
                            if "Proving Ground" not in calendar_events[eventID][0]:
                                category_name = calendar_msgs[category][0]
                                event_time = t
                                event_icon = calendar_events[eventID][1]
                                event_ilevel = eventMetadata
                                event_name = calendar_events[eventID][0]

                                if "-" in event_time:
                                    event_start, event_end = event_time.split(
                                        "-")
                                else:
                                    event_start = event_time

                                newEvent = Event(
                                    month, day,  eventID, event_start, event_name, category_name, event_icon, event_ilevel, event_end)
                                eventList.enqueueEvent(newEvent)

finalList = eventList.getEventList()
finalList = sorted(finalList, key=lambda x: x.event_start)
myCurrentTime = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))

while True:
    eventsIn15Minutes = [e for e in finalList if (myCurrentTime < e.event_start) and (
        e.event_start - myCurrentTime) <= datetime.timedelta(minutes=15)]
    if len(eventsIn15Minutes) > 0:

        for event in eventsIn15Minutes:
            print("{} - will occur in {}".format(event.event_name,
                                                 event.event_start-myCurrentTime))
    else:
        print("No events happening in the next 15 minutes")
    time.sleep(60)
