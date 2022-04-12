import requests
import lxml.html
import json
import pytz
import datetime
import re
from util import *

EVENT_CALENDAR_URL = "https://lostarkcodex.com/us/eventcalendar/"


class Event:
    def __init__(self, month, day, event_id, event_time, event_name, event_category, event_icon, event_ilevel=None):

        if "-" in event_time:
            self.event_start, self.event_end = event_time.split(
                "-")
        else:
            self.event_start = event_time
            self.event_end = None

        # parse the start time relative to our timezone (PST)
        hour, minute = self.event_start.split(":")
        et = pytz.timezone('America/New_York')
        pt = pytz.timezone('America/Los_Angeles')

        server_time = et.normalize(et.localize(datetime.datetime(datetime.datetime.today(
        ).year, int(month), int(day), int(hour), int(minute), 0, 0,)))

        if self.needsTimeAdded(int(event_id)):
            server_time = server_time + datetime.timedelta(minutes=10)

        self.event_start = pt.normalize(server_time.astimezone(pt))

        event_name = self._groupEventName(event_name, event_icon)

        self.event_name = event_name.split("(")[0]
        self.event_category = event_category
        self.event_icon = event_icon
        self.event_ilevel = event_ilevel if event_ilevel is not None else "N/A"

        if self.event_end is not None:
            # parse the end time relative to our timezone (PST)
            hour, minute = self.event_end.split(":")

            end_server_time = et.normalize(et.localize(datetime.datetime(datetime.datetime.today(
            ).year, int(month), int(day), int(hour), int(minute), 0, 0,)))
            self.event_end = pt.normalize(end_server_time.astimezone(pt))

        self._notified = False

    def _groupEventName(self, eventName, eventIcon):
        if eventIcon == 'achieve_13_11.webp':
            return "Chaos Gates"
        if "Ghost Ship" in eventName:
            return "Ghost Ships"
        if eventIcon == 'achieve_14_142.webp':
            return 'Field Bosses'
        if "Grand Prix" in eventName:
            return "Grand Prix"
        return eventName

    def hashEvent(self):

        return "{}{}".format(self.event_name, self.event_start)

    def needsTimeAdded(self, id):
        if (id >= 7000 and id < 8000 and id not in [7013, 7035]) or (id in [
            1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 5002,
            5003, 5004, 6007, 6008, 6009, 6010, 6011,
        ]):
            return True
        return False

    def setNotifyStatus(self, status):
        self._notified = status

    def alreadyNotified(self):
        return self._notified == True


class EventList:
    def __init__(self):
        self._eventList = []
        self._eventHashList = {}

    def enqueueEvents(self, events):
        for e in events:
            # Only add event if not encountered before
            myCurrentTime = getCurrentTime()
            if myCurrentTime < e.event_start:
                hashed = e.hashEvent()
                if hashed not in self._eventHashList:
                    self._eventHashList[hashed] = True
                    self._eventList.append(e)
        # sort the list by event_start
        self._eventList = sorted(self._eventList, key=lambda x: x.event_start)

    def getEventList(self):
        return self._eventList


class EventRetriever:

    def getEventData(self):
        r = requests.get(EVENT_CALENDAR_URL)
        if r.status_code == 200:
            print("Successfully retrieved event calendar data")

        # Parse event data
        tree = lxml.html.fromstring(r.content)
        raw_data = tree.xpath(
            "//div/script[contains(text(), 'calendar_data')]")
        raw_data = raw_data[0].text

        calendar_data = re.search("var calendar_data=(.*);", raw_data)
        calendar_events = re.search("var calendar_events=(.*);", raw_data)
        calendar_msgs = re.search("var calendar_msgs=(.*);", raw_data)

        if calendar_data:
            calendar_data = json.loads(calendar_data.group(1))
        if calendar_events:
            calendar_events = json.loads(calendar_events.group(1))
        if calendar_msgs:
            calendar_msgs = json.loads(calendar_msgs.group(1))[0]

        return calendar_data, calendar_events, calendar_msgs

    def populateEventData(self):
        eventList = []
        calendar_data, calendar_events, calendar_msgs = self.getEventData()

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

                                    newEvent = Event(
                                        month, day, eventMetadata, event_time, event_name, category_name, event_icon, event_ilevel)
                                    eventList.append(newEvent)

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

                                        newEvent = Event(
                                            month, day,  eventID, event_time, event_name, category_name, event_icon, event_ilevel)
                                        eventList.append(newEvent)
        return eventList
