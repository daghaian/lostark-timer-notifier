import requests
import lxml.html
import json
import pytz
import datetime
import re

EVENT_CALENDAR_URL = "https://lostarkcodex.com/us/eventcalendar/"


class Event:
    def __init__(self, month, day, event_id, event_start, event_name, event_category, event_icon, event_ilevel=None, event_end=None):
        # convert start time to epoch
        hour, minute = event_start.split(":")

        et = pytz.timezone('America/New_York')
        pt = pytz.timezone('America/Los_Angeles')

        server_time = et.normalize(et.localize(datetime.datetime(datetime.datetime.today(
        ).year, int(month), int(day), int(hour), int(minute), 0, 0,)))

        if self.needsTimeAdded(int(event_id)):
            server_time = server_time + datetime.timedelta(minutes=10)

        self.event_start = pt.normalize(server_time.astimezone(pt))

        if event_icon == 'achieve_13_11.webp':
            event_name = "Chaos Gates"
        if "Ghost Ship" in event_name:
            event_name = "Ghost Ships"
        if event_icon == 'achieve_14_142.webp':
            event_name = 'Field Bosses'
        if "Grand Prix" in event_name:
            event_name = "Grand Prix"
            
        self.event_name = event_name.split("(")[0]
        self.event_category = event_category
        self.event_icon = event_icon
        self.event_ilevel = event_ilevel if event_ilevel is not None else 0

        if event_end is not None:
            hour, minute = event_end.split(":")

            end_server_time = et.normalize(et.localize(datetime.datetime(datetime.datetime.today(
            ).year, int(month), int(day), int(hour), int(minute), 0, 0,)))
            self.event_end = pt.normalize(end_server_time.astimezone(pt))

    def hashEvent(self):

        return "{}{}".format(self.event_name, self.event_start)

    def needsTimeAdded(self, id):
        if (id >= 7000 and id < 8000 and id not in [7013, 7035]) or (id in [
            1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 5002,
            5003, 5004, 6007, 6008, 6009, 6010, 6011,
        ]):
            return True
        return False


class EventList:
    def __init__(self):
        self._eventList = []
        self._eventHashList = {}

    def enqueueEvent(self, event):
        # Only add event if not encountered before
        hashed = event.hashEvent()
        if hashed not in self._eventHashList:
            self._eventHashList[hashed] = True
            self._eventList.append(event)

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
