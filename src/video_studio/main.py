from __future__ import annotations

import uvicorn

from .app import app
from .config import settings


def main() -> None:
    uvicorn.run("video_studio.app:app", host=settings.app_host, port=settings.app_port, reload=False)


if __name__ == "__main__":
    main()

