"""Local Development Setup Script for PromiseOS Backend.

Validates environment, creates necessary directories, prepares .env if missing,
and initializes database tables.
Usage:
    python -m scripts.local_setup
"""

import asyncio
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db


async def setup():
    logger.info("=== PromiseOS Backend Local Setup ===")

    # 1. Check Python version
    major, minor = sys.version_info.major, sys.version_info.minor
    logger.info(f"Detected Python {major}.{minor}")
    if major < 3 or (major == 3 and minor < 11):
        logger.warning("PromiseOS is designed for Python 3.11+. Some features may behave differently.")

    # 2. Check and copy .env if missing
    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env"
    env_example = base_dir / ".env.example"

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        logger.info("Created local .env from .env.example (MOCK_LLM=true, empty API keys).")
    else:
        logger.info(".env file is present.")

    # 3. Create required directories
    dirs = [
        settings.upload_path,
        base_dir / "data" / "samples",
        base_dir / "data" / "test_evidence",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory confirmed: {d}")

    # 4. Initialize Database
    logger.info(f"Initializing database at: {settings.DATABASE_URL}")
    await init_db()

    logger.info("=== Setup Complete. Ready to run FastAPI server: ===")
    logger.info("uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    asyncio.run(setup())
