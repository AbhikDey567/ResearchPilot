
import os
from pathlib import Path

from dotenv import load_dotenv


# Always load backend/.env, regardless of the terminal's working directory.
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Use the model you have configured in backend/.env.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
