
import time
from abc import ABC, abstractmethod
import typing
from enum import Enum

StateBase = typing.NewType("StateBase", ABC)

# https://auth0.com/blog/state-pattern-in-python/

class Sound(Enum):
    NO_SOUND=0
    CLICK=1
    BOOM=2

class Mine:

    _state = None
    _timestamp = None
    _mines_self_reset = None
    _click_debounce_sec = None
    _boom_debounce_sec = None

    def __init__(self, mines_self_reset=True, click_debounce_sec=0.5, boom_deboucne_sec=0.5, state: StateBase=None) -> None:
        
        self._mines_self_reset = mines_self_reset       # Mines are allowed to go 'boom' multiple times
        self._click_debounce_sec = click_debounce_sec   # Number or fraction of a second that a button must be held to go 'click'
        self._boom_debounce_sec = boom_deboucne_sec     # Number or fraction of a second that a button must be released to go 'boom'

        if state is not None:
            self.setMine(state)
        else:
            self.setMine(stateUninitialized())

        self._timestamp = time.monotonic()
 

    # method to change the state of the object
    def setMine(self, state: StateBase):

        self._state = state
        self._state.mine = self

    def presentState(self):
        print(f"Mine is in {type(self._state).__name__}")


    # Call when a new input reading in available
    # Returns 0: no sound, 1: click, 2: boom
    def inputReading(self, reading):
        if reading==True:
            return self._state.active()
        else:
            return self._state.inactive()
        
    # Reset state back to uninitialized
    def reset(self):
        self.setMine(stateUninitialized())



# The abstract state interface for all the states
class StateBase(ABC):
    @property
    def mine(self) -> Mine:
        return self._mine

    @mine.setter
    def mine(self, mine: Mine) -> None:
        self._mine = mine

    @abstractmethod
    def active(self) -> Sound: # returns 0: nothing, 1: click, 2: boom
        pass

    @abstractmethod
    def inactive(self) -> Sound: # returns 0: nothing, 1: click, 2: boom
        pass

# Concrete states
class stateUninitialized(StateBase):
    def active(self) -> Sound:
        return Sound.NO_SOUND
    
    def inactive(self) -> Sound:
        self.mine._timestamp = time.monotonic()
        self.mine.setMine(stateIdle())
        return Sound.NO_SOUND

class stateIdle(StateBase):
    def active(self) -> Sound:
        self.mine.setMine(stateClickDebounce())
        return Sound.NO_SOUND

    def inactive(self) -> Sound:
        return Sound.NO_SOUND

class stateClickDebounce(StateBase):
    def active(self) -> Sound:
        if (time.monotonic() - self.mine._timestamp) > self.mine._click_debounce_sec:
            self.mine.timestamp = time.monotonic()
            self.mine.setMine(stateClick())
            return Sound.CLICK
        else:
            return Sound.NO_SOUND

    def inactive(self) -> Sound:
        self.mine._timestamp = time.monotonic()
        self.mine.setMine(stateIdle())
        return Sound.NO_SOUND

class stateClick(StateBase):
    def active(self) -> Sound:
        return Sound.NO_SOUND

    def inactive(self) -> Sound:
        self.mine.setMine(stateBoomDebounce())
        return Sound.NO_SOUND

class stateBoomDebounce(StateBase):
    def active(self) -> Sound:
        self.mine._timestamp = time.monotonic()
        self.mine.setMine(stateClick())
        return Sound.NO_SOUND

    def inactive(self) -> Sound:
        if (time.monotonic() - self.mine._timestamp) > self.mine._boom_debounce_sec:
            self.mine.timestamp = time.monotonic()
            if self.mine._mines_self_reset == True:
                self.mine.setMine(stateIdle())
            else:
                self.mine.setMine(stateTerminate())
            return Sound.BOOM
        else:
            return Sound.NO_SOUND
        
# If this state is reached, it will stay here until reset
class stateTerminate(StateBase):
    def active(self) -> Sound:
        return Sound.NO_SOUND
    
    def inactive(self) -> Sound:
        return Sound.NO_SOUND

if __name__ == "__main__":
    print("This is a class to track Mine game state. Don't run it because it doesn't do anything.")