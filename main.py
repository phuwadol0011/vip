import os, time, logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def getenv_str(name):
    val = os.getenv(name)
    logging.info("ENV %s raw=%r", name, val)  # << log เช็คค่าจริง
    if val is None or not str(val).strip():
        raise RuntimeError(f"Missing ENV: {name}")
    return str(val).strip()

BOT_TOKEN    = getenv_str("BOT_TOKEN")
VIP_CHAT_ID  = int(getenv_str("VIP_CHAT_ID"))
ITEM_TITLE   = os.getenv("ITEM_TITLE", "VIP Pass")
ITEM_DESC    = os.getenv("ITEM_DESCRIPTION", "เข้ากลุ่ม")
ITEM_STARS   = int(os.getenv("ITEM_STARS", "100"))
INVITE_TTL_H = int(os.getenv("INVITE_TTL_HOURS", "12"))

