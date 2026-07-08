import os
import sys
import datetime

if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_GALLERY_DL = os.path.join(ROOT_DIR, "resources", "gallery-dl.exe")

if getattr(sys, 'frozen', False):
    BUNDLED_GALLERY_DL = os.path.join(sys._MEIPASS, "resources", "gallery-dl.exe")
else:
    BUNDLED_GALLERY_DL = USER_GALLERY_DL

GALLERY_DL_PATH = USER_GALLERY_DL if os.path.exists(USER_GALLERY_DL) else BUNDLED_GALLERY_DL

LINKS_FILE = os.path.join(ROOT_DIR, "Links.txt")
COOKIE_FILE = os.path.join(ROOT_DIR, "Cookie.txt")
ARCHIVE_FILE = os.path.join(ROOT_DIR, "DownloadArchive.sqlite3")

TODAY_STR = datetime.datetime.now().strftime("%Y_%m_%d")
OUTPUT_BASE = os.path.join(ROOT_DIR, "Pinterest", TODAY_STR)
METADATA_DIR = os.path.join(OUTPUT_BASE, "Metadata")
LOGS_DIR = os.path.join(OUTPUT_BASE, "Logs")

SESSION_SIZE = 50
MIN_DELAY = 1.0
MAX_DELAY = 5.0
MIN_COOLDOWN = 300
MAX_COOLDOWN = 400
TIMEOUT_SEC = 60
MAX_RETRIES = 3

EXPECTED_COOKIE_HEADER = "# Netscape HTTP Cookie File"