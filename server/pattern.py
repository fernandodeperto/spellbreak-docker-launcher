import re

PATTERNS = {
    "ENGINE_INITIALIZED": r"Game Engine Initialized",
    "PLAYER_JOINED": r'"DisplayName":"(.*?)"',
    "REMOVING_PLAYER": r"Removing player (.*?) from squad",
    "MATCH_STARTED": r"Force Spawn players",
    "MATCH_ENDING": r"Match Ending",
    "MATCH_COMPLETE": r"The match was complete",
    "GAME_ENGINE_SHUTDOWN": r"Game engine shut down",
    "LOG_FILE_CLOSED": r"Log file closed",
}

COMPILED_PATTERNS = [
    (pattern_name, re.compile(pattern)) for pattern_name, pattern in PATTERNS.items()
]
