from abc import ABC, abstractmethod

class Animation(ABC):
    def __init__(self, **kwargs):
        self.observers = []
        self._text = kwargs.get('text', '').strip()
        self._done : bool = False
        self._max_text_width = kwargs.get('max_text_width', 80)

    @property
    def max_text_width(self) -> int:
        return self._max_text_width
    @property
    def text(self) -> str:
        return self._text

    @abstractmethod
    def next(self) -> str:
        '''Advances the animation by one step and returns the current state of the text.'''
        pass
    
    @property
    def is_finished(self) -> bool:
        '''Returns True if the animation is finished, False otherwise.'''
        return self._done

    def add_observer(self, observer, **kwargs):
        if observer not in self.observers:
            observer_name = kwargs.get('target_name', 'unknown')
            self.observers.append((observer, observer_name))

    def remove_observer(self, observer, **kwargs):
        if observer in self.observers:
            observer_name = kwargs.get('target_name', 'unknown')
            self.observers.remove((observer, observer_name))

    def notify_observers(self, **kwargs):
        for observer in self.observers:
            kwargs['target_name'] = observer[1]
            observer[0].animation_update(**kwargs)
