from enum import Enum, auto


class State(Enum):
    PROCESS_NOT_STARTED = auto()
    PROCESS_STARTING = auto()
    LOBBY = auto()
    MATCH_STARTED = auto()
    MATCH_ENDING = auto()
    MATCH_COMPLETE = auto()
    GAME_ENGINE_SHUTDOWN = auto()
    LOG_FILE_CLOSED = auto()
