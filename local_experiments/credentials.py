"""Portable optional OpenAI credential access; no keys embedded or printed."""
import os
from pathlib import Path
from dotenv import dotenv_values


def openai_key():
    value = os.environ.get('OPENAI_API_KEY', '').strip()
    if value:
        return value
    root = Path(__file__).resolve().parents[1]
    for name in ['.env', '.env.local']:
        path = root / name
        if path.is_file():
            value = (dotenv_values(path).get('OPENAI_API_KEY') or '').strip()
            if value:
                return value
    raise RuntimeError('Optional OpenAI key missing; inference does not require one')
