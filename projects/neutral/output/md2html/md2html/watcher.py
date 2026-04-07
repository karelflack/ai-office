import time
from pathlib import Path
from typing import Callable


def watch(input_path: Path, build: Callable[[], None]) -> None:
    """
    Watch input_path for changes and call build() on each modification.

    Requires watchdog (pip install md2html[watch]).
    Raises ImportError with a helpful message if watchdog is not installed.
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        raise ImportError(
            "Watch mode requires watchdog. Install it with:\n"
            "  pip install md2html[watch]"
        )

    class _Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if Path(event.src_path).resolve() == input_path.resolve():
                build()

    observer = Observer()
    observer.schedule(_Handler(), str(input_path.parent), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
