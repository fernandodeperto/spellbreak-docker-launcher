import logging
import os
import threading
import queue
import subprocess
import time

from tenacity import retry, wait_fixed, stop_after_attempt
from typing import Optional, IO

from server.config import config
from server.state import State
from server.pattern import COMPILED_PATTERNS

BIN_DIR = "/spellbreak-server/BaseServer/g3/Binaries/Win64/g3Server-Win64-Test.exe"
LOG_DIR = "/spellbreak-server/BaseServer/g3/Saved/Logs"


def start_background_process(log_file_name: str) -> subprocess.Popen:
    command = [
        "wine",
        BIN_DIR,
        f"Alpha_Resculpt?game={config.game.mode}",
        f"-port={config.server.port}",
        f"-LOG={log_file_name}",
    ]
    logger.debug(f"running command {command}")

    os.environ["WINEPREFIX"] = "/root/.wine"
    os.environ["WINEDEBUG"] = "fixme-all"

    with open(os.devnull, "w") as devnull:
        if config.server.show_game_logs:
            return subprocess.Popen(command)

        return subprocess.Popen(
            command,
            stdout=devnull,
            stderr=devnull,
        )


def process_log_line(line: str) -> Optional[State]:
    results = [
        (pattern_name, compiled_pattern.search(line))
        for pattern_name, compiled_pattern in COMPILED_PATTERNS
    ]

    matches = [
        (pattern_name, result.groups()) for pattern_name, result in results if result
    ]

    if len(matches) > 1:
        raise Exception(f"only one pattern should have matched: {matches}")

    if not len(matches):
        return None

    logger.debug(matches[0])

    match matches[0][0]:
        case "ENGINE_INITIALIZED":
            return State.LOBBY
        case "PLAYER_JOINED":
            logger.info(f"player {matches[0][1]} joined")
        case "REMOVING_PLAYER":
            logger.info(f"player {matches[0][1]} left")
        case "MATCH_STARTED":
            return State.MATCH_STARTED
        case "MATCH_ENDING":
            return State.MATCH_ENDING
        case "MATCH_COMPLETE":
            return State.MATCH_COMPLETE
        case "GAME_ENGINE_SHUTDOWN":
            return State.GAME_ENGINE_SHUTDOWN
        case "LOG_FILE_CLOSED":
            return State.LOG_FILE_CLOSED
        case _:
            pass


def main():
    logger.debug(config)
    logger.debug(os.environ)

    while True:
        log_file_name = f"server-{os.urandom(4).hex()}.log"
        logger.debug(f"using log file {log_file_name}")

        process = start_background_process(log_file_name)

        state = State.PROCESS_STARTING
        next_state = None
        state_start_time = time.time()

        @retry(wait=wait_fixed(1), stop=stop_after_attempt(30))
        def open_log_file(path: str) -> IO:
            return open(os.path.join(LOG_DIR, path), "r")

        log_file = open_log_file(log_file_name)
        line = None

        while True:
            line = log_file.readline()

            if line is not None and line != "":
                logger.debug(line)
                next_state = process_log_line(line)

            state_duration = int(time.time() - state_start_time)

            if next_state is not None and next_state != state:
                logger.info(f"new state {next_state} after {state_duration} seconds")

                state_start_time = time.time()
                state = next_state

            match state:
                case State.LOBBY:
                    if state_duration > config.server.idle_timer:
                        logger.info("stopping the process due to inactivity")
                        process.terminate()
                        break

                case State.MATCH_COMPLETE:
                    logger.info("match complete")
                    process.terminate()
                    break

                case State.LOG_FILE_CLOSED:
                    logger.info("process done")
                    process.terminate()
                    break

            if process.poll() is not None:
                logger.info("process ended unexpectedly")
                break

            if line is None or line == "":
                time.sleep(1)

        process.wait()

        os.remove(os.path.join(LOG_DIR, log_file_name))


logging.basicConfig(
    level=config.server.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(lineno)d: %(message)s",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    main()
