# app_config.py
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
import os # Added for potential environment variable usage

# --- Application Constants ---
# Assumes an 'icons' subdirectory in your project root for these images
DEFAULT_APP_ICON_FILENAME = "cerberus_icon.png"     # Main application icon
DEFAULT_PAYLOAD_ICO_FILENAME = "cerberus_icon.ico"  # Default .ico for payload
DEFAULT_PAYLOAD_NAME = "CerberusPayload.exe"

APP_TITLE = "Cerberus Builder"
APP_VERSION = "1.9" # Version for tabbed UI
ORGANIZATION_NAME = "CerberusProject"
APPLICATION_NAME = "CerberusBuilder"

DISCORD_INVITE_URL = "https://discord.gg/3ZSVqbbUwJ"
YOUTUBE_URL = "https://www.youtube.com/@TrinityT"
GITHUB_URL = "https://github.com/Trinitysudo"

# --- Discord Bot Configuration (for Live Execution / Remote Access Mode) ---
# IMPORTANT: These values are REQUIRED if you intend to use the Remote Access features
# of the generated payload. Treat your BOT_TOKEN like a password.
#
# OPTION 1 (Recommended for BOT_TOKEN): Set an environment variable named "CERBERUS_DISCORD_BOT_TOKEN"
#   DISCORD_BOT_TOKEN = os.getenv("CERBERUS_DISCORD_BOT_TOKEN", "If using the Remote accese put you token here REPLACE ME!")
#
# OPTION 2 (Recommended for COMMAND_CHANNEL_ID): Set an environment variable named "CERBERUS_COMMAND_CHANNEL_ID"
#   COMMAND_CHANNEL_ID = os.getenv("CERBERUS_COMMAND_CHANNEL_ID", "If using the Remote accese put you DISCORD CHANNEL ID (USE DEVMODE AND RIGHTCLICK THE CHANNEL) here REPLACE ME")
#
# If not using environment variables, replace the placeholder strings below directly.

DISCORD_BOT_TOKEN = "If using the Remote accese put you token here REPLACE ME!"
COMMAND_CHANNEL_ID = "If using the Remote accese put you DISCORD CHANNEL ID (USE  DEVMODE AND RIGHTCLICK THE CHANNEL) here REPLACE ME"

# You can add checks in your application logic where these are used:
# For example, before enabling "Remote Access" payload generation:
#
# if (DISCORD_BOT_TOKEN == "If using the Remote accese put you token here REPLACE ME!" or
#     COMMAND_CHANNEL_ID == "If using the Remote accese put you DISCORD CHANNEL ID (USE  DEVMODE AND RIGHTCLICK THE CHANNEL) here REPLACE ME"):
#     print("WARNING: Discord Bot Token or Command Channel ID is not configured for Remote Access mode.")
#     # Potentially disable the feature or show a warning in the GUI
# else:
#     # Proceed with Remote Access feature
#     pass


# --- Original Red Theme Color Definitions ---
CRIMSON_RED = QColor(0xDC, 0x14, 0x3C)
DARK_BACKGROUND = QColor(0x1E, 0x1E, 0x1E)
MID_BACKGROUND = QColor(0x2D, 0x2D, 0x2D)
LIGHT_GRAY_TEXT = QColor(0xD0, 0xD0, 0xD0)
DARK_GRAY_BORDER = QColor(0x4A, 0x4A, 0x4A)
DISABLED_COLOR = QColor(0x55, 0x55, 0x55)
TEXT_ON_RED = QColor(Qt.GlobalColor.white)

# Font Size Limits
MIN_FONT_SIZE = 7
MAX_FONT_SIZE = 14
DEFAULT_FONT_SIZE = 9