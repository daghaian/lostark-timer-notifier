import requests
import lxml.html
import re
import json
import datetime
import pytz


class Event:
    def __init__(self, event_start, event_name, event_category, event_icon, event_ilevel=None, event_end=None):

        # convert start time to epoch
        hour, minute = event_start.split(":")
        test = datetime.datetime(datetime.today(
        ).year, int(month), int(day), int(hour), int(minute), 0, 0, pytz.timezone('US/Mountain'))
        print(test.timestamp())
        self.event_start = event_start
        self.event_name = event_name
        self.event_category = event_category
        self.event_icon = event_icon
        if event_ilevel is not None:
            self.event_ilevel = event_ilevel
        if event_end is not None:
            self.event_end = event_end


EVENT_CALENDAR_URL = "https://lostarkcodex.com/us/eventcalendar/"
eventList = []

# Begin by retrieving event data
r = requests.get(EVENT_CALENDAR_URL)
if r.status_code == 200:
    print("Successfully retrieved event calendar data")

    # Parse event data
    tree = lxml.html.fromstring(r.content)
    raw_data = tree.xpath("//div/script[contains(text(), 'calendar_data')]")
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
                        for time in events:
                            if "Proving Ground" not in calendar_events[eventMetadata][0]:
                                category_name = calendar_msgs[category][0]
                                event_time = time
                                event_icon = calendar_events[eventMetadata][1]
                                event_ilevel = None
                                event_name = calendar_events[eventMetadata][0]

                                print("Category ID: {} Category Name: {} Month: {} Day: {} Event ID: {}, Event Name: {} Event Time: {} Item Level: NONE".format(
                                    category, calendar_msgs[category][0], month, day, eventMetadata, calendar_events[eventMetadata][0], time))
                                continue
                    # Else, we have an item level requirement for the events in this category
                    else:
                        for eventID, event in events.items():
                            for time in event:
                                if "Proving Ground" not in calendar_events[eventID][0]:
                                    category_name = calendar_msgs[category][0]
                                    event_time = time
                                    event_icon = calendar_events[eventID][1]
                                    event_ilevel = eventMetadata
                                    event_name = calendar_events[eventID][0]

                                    print("Category ID: {} Category Name: {} Month: {} Day: {} Event ID: {} Event Name: {} Event Time: {} Item Level: {}".format(
                                        category, calendar_msgs[category][0], month, day, eventID, calendar_events[eventID][0], time, eventMetadata))
                                    continue

                    if "-" in event_time:
                        event_start, event_end = event_time.split("-")
                    else:
                        event_start = event_time
                    eventList.append(Event(event_start=event_start, event_name=event_name, event_category=category_name,
                                     event_icon=event_icon, event_ilevel=event_ilevel, event_end=event_end))

    # #         # Check on interval
