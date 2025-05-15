from dotenv import load_dotenv
import os


load_dotenv()


BOT_API = os.getenv("BOT_API")
if BOT_API is None:
    raise ValueError("No environment variable: BOT_API")


KANDINSKY_API_KEY = os.getenv("KANDINSKY_API_KEY")
if KANDINSKY_API_KEY is None:
    raise ValueError("No environment variable: KANDINSKY_API_KEY")


KANDINSKY_SECRET_KEY = os.getenv("KANDINSKY_SECRET_KEY")
if KANDINSKY_SECRET_KEY is None:
    raise ValueError("No environment variable: KANDINSKY_SECRET_KEY")
