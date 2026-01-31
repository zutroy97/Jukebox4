import logging
from jukebox.coordinator.change_events import ChangeEvents
from jukebox.coordinator.display_coordinator import DisplayObserver

class ExampleDisplay(DisplayObserver):
    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__class__.__name__)

    def update(self, observable, *args, **kwargs):
        if 'event' in kwargs:
            event = kwargs['event']
            if event == ChangeEvents.TITLE_CHANGED:
                print(f"Title updated to: {kwargs.get('value')}")
            elif event == ChangeEvents.ARTIST_CHANGED:
                print(f"Artist updated to: {kwargs.get('value')}")
            else:
                print(f"Unknown event {event}")
        else:
            print(f"No event information provided {observable}, args: {args}, kwargs: {kwargs}")
