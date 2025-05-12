# Cerberus Payload Builder 🐍🔧

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
[![Discord](https://img.shields.io/discord/YOUR_SERVER_ID?label=Discord&logo=discord&logoColor=white&color=7289DA&style=for-the-badge)](https://discord.gg/YOUR_DISCORD_INVITE_CODE)
<!-- Replace YOUR_SERVER_ID and YOUR_DISCORD_INVITE_CODE -->
<!-- You can generate more badges here: https://shields.io/ -->

**Cerberus Builder** is a Python-based GUI application (using PyQt6) designed for internal IT departments to create customized information-gathering payloads. These payloads, when executed on a target Windows machine, collect general system information and securely send it to a pre-configured Discord webhook.

---

## ✨ Features

*   **Intuitive GUI Builder**: Easily configure payload settings using a clean, themed graphical interface.
    *   🖌️ **Customizable Appearance**: Includes a built-in font size adjuster for user comfort.
*   **Targeted Information Gathering**:
    *   🖥️ **General System Information**: Collects OS details, CPU, RAM, disk usage, IP address, geolocation (via public IP), network interface details (MAC, local IPs, gateway), connected Wi-Fi SSID, and GPU information (Windows via WMI).
*   **Secure Data Exfiltration**:
    *   💬 **Discord Integration**: Sends collected data as a formatted embed message to a specified Discord webhook URL. Includes retry logic for network requests.
*   **Payload Customization**:
    *   🖼️ **Custom Payload Icon**: Set a custom `.ico` file for the generated executable.
    *   📦 **EXE Pumping**: Option to inflate the output executable to a specified size (MB) with null bytes, potentially aiding in certain analysis evasion scenarios.
*   **Asynchronous Build Process**:
    *   ⚙️ **Non-Blocking GUI**: Compiles payloads using PyInstaller in a separate thread, preventing the GUI from freezing.
    *   📊 **Progress & Logging**: Visual progress bar and detailed build logs within the application.
*   **Standalone Payloads**: Generates single, standalone Windows executables (`.exe`) that run without needing Python installed on the target machine.
*   **Organized & Maintainable Code**: Refactored with configuration, UI styling, and UI setup separated into modules for better readability and future development.

---

## 🖼️ Screenshots

**(Coming Soon! Replace these with actual screenshots)**

*   **Cerberus Builder GUI:**
    `[Link to Screenshot of Builder GUI]` or embed directly:
    `![Cerberus Builder GUI](path/to/your/builder_gui_screenshot.png)`

*   **Sample Discord Embed:**
    `[Link to Screenshot of Discord Embed]` or embed directly:
    `![Sample Discord Embed](path/to/your/discord_embed_screenshot.png)`

---

## 🚀 Getting Started

### Prerequisites

*   **Python 3.9 or higher**
*   **PyQt6** and other dependencies (can be installed via `requirements.txt`)
*   **PyInstaller** (for compiling payloads) - The builder attempts to locate it in common Python script paths or expects it to be in your system's PATH.
*   A **Discord Webhook URL** to send the reports to.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/[YourGitHubUsername]/CerberusMalware.git
    cd CerberusMalware
    ```
    *(Replace `[YourGitHubUsername]` with your actual GitHub username)*

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    *(Create a `requirements.txt` file first! See section below)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Essential Links (Optional but Recommended):**
    Open `app_config.py` and update the following placeholders with your actual links:
    *   `DISCORD_INVITE_URL = "YOUR_DISCORD_INVITE_LINK_HERE"`
    *   `YOUTUBE_URL = "https://www.youtube.com/@TrinityT"` (Already set to yours)
    *   `GITHUB_URL = "https://github.com/Trinitysudo"` (Already set to yours)

5.  **Prepare Icons:**
    Ensure the following icon files are present in the project root directory (or update paths in `app_config.py` and `ui_setup.py`):
    *   `cerberus_icon.png` (for the builder app window, ~32x32 or 64x64 recommended)
    *   `cerberus_icon.ico` (default icon for generated payloads, must be `.ico`)
    *   `discord_icon.png` (for the Discord link button, ~24x24)
    *   `youtube_icon.png` (for the YouTube link button, ~24x24)
    *   `github_icon.png` (for the GitHub link button, ~24x24)

### Creating a `requirements.txt`

Based on the project files, your `requirements.txt` should look something like this:
