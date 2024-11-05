import logging
import os
import threading
import queue
import subprocess
import time

from tenacity import retry, wait_fixed, stop_after_attempt
from typing import List, IO

from server.config import config
from server.state import State
from server.pattern import COMPILED_PATTERNS


def start_background_process(command: List[str]) -> subprocess.Popen:
    with open(os.devnull, "w") as devnull:
        process = subprocess.Popen(
            command,
            stdout=devnull,
            stderr=devnull,
        )

    return process


def start_thread(
    path: str, logs_queue: queue.Queue, stop_event: threading.Event
) -> threading.Thread:
    thread = threading.Thread(target=read_logs, args=(path, logs_queue, stop_event))
    thread.start()

    return thread


def read_logs(path: str, logs_queue: queue.Queue, stop_event: threading.Event) -> None:
    @retry(wait=wait_fixed(1), stop=stop_after_attempt(30))
    def open_logs_file(path: str) -> IO:
        return open(path, "r")

    logs_file = open_logs_file(path)

    while not stop_event.is_set():
        line = logs_file.readline()

        if line is None or line == "":
            logger.debug("did not receive a line")
            time.sleep(1)
        else:
            logs_queue.put(line.strip())


def process_log_line(line: str) -> State:
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
    def stop_process():
        process.terminate()
        stop_event.set()
        thread.join()

    command = [
        "wine",
        "/spellbreak-server/BaseServer/g3/Binaries/Win64/g3Server-Win64-Test.exe",
        f"Alpha_Resculpt?game={config.game.mode}",
        f"-port={config.server.port}",
        f"-LOG={config.game.log_file}",
    ]

    os.environ["WINEPREFIX"] = "/root/.wine"
    os.environ["WINEDEBUG"] = "fixme-all"

    logger.info(f"using config {config}")

    logger.debug(f"running command {command}")

    process = start_background_process(command)
    logger.info(f"started process with pid {process.pid}")

    logs_queue = queue.Queue()
    stop_event = threading.Event()
    thread = start_thread(
        f"/spellbreak-server/BaseServer/g3/Saved/Logs/{config.game.log_file}",
        logs_queue,
        stop_event,
    )

    state = State.PROCESS_STARTING
    next_state = None
    state_start_time = time.time()

    line = None

    while thread.is_alive() or not logs_queue.empty():
        try:
            line = logs_queue.get(timeout=1)
        except queue.Empty:
            line = None

        if line is not None:
            logger.debug(line)

            next_state = process_log_line(line)

        state_duration = int(time.time() - state_start_time)

        if next_state is not None and next_state != state:
            logger.info(f"new state {next_state} after {state_duration} seconds")

            state = next_state
            state_start_time = time.time()

        match state:
            case State.LOBBY:
                if state_duration > config.server.idle_timer:
                    logger.info("stopping the process due to inactivity")
                    break

            case State.MATCH_ENDING:
                logger.info("match ending")
                break

            case State.MATCH_COMPLETE:
                logger.info("match complete")
                break

            case State.LOG_FILE_CLOSED:
                logger.info("process done")
                break

        if process.poll() is not None:
            logger.info("process ended unexpectedly")
            break

    stop_process()


logging.basicConfig(
    level=config.server.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(lineno)d: %(message)s",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    main()
