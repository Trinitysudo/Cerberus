# Cerberus Payload Builder 🛠️

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
[![Discord](https://img.shields.io/discord/YOUR_SERVER_ID?label=Join%20Our%20Discord&logo=discord&logoColor=white&color=7289DA&style=for-the-badge)](https://discord.gg/3ZSVqbbUwJ)
<!-- Replace YOUR_SERVER_ID with your actual Discord Server ID -->
<!-- You can generate more badges here: https://shields.io/ -->

**Cerberus Builder** is a Python GUI application (PyQt6) for IT departments to create custom information-gathering Windows payloads. Payloads collect system info and send it to a Discord webhook.

---

## ✨ Core Features

*   **Intuitive GUI Builder**: Easy payload configuration with font size adjustment.
*   **System Information**: Collects OS, CPU, RAM, disk, IP, geolocation, network details (MAC, IPs, gateway, Wi-Fi), and GPU info.
*   **Discord Integration**: Sends data as formatted embeds to a specified webhook.
*   **Payload Customization**: Custom `.ico` icon and EXE size inflation.
*   **Asynchronous & Standalone**: Non-blocking GUI during compilation; generates single `.exe` payloads.
*   **Organized Code**: Modular design for better maintainability.

---

## 🖼️ Screenshots

**(Coming Soon! Add screenshots of the Builder and a Discord report.)**

*   **Cerberus Builder GUI:** `![Cerberus Builder GUI](path/to/your/builder_gui_screenshot.png)`
*   **Sample Discord Embed:** `![Sample Discord Embed](path/to/your/discord_embed_screenshot.png)`

---

## 🚀 Getting Started

### Prerequisites

*   Python 3.9+
*   PyQt6, PyInstaller, and other dependencies (see `requirements.txt` section).
*   A Discord Webhook URL.

### Installation

1.  **Clone:**
    ```bash
    git clone https://github.com/[YourGitHubUsername]/CerberusMalware.git
    cd CerberusMalware
    ```
    *(Replace `[YourGitHubUsername]`)*

2.  **Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # Windows: .\venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
    ```

3.  **Install Dependencies (Create `requirements.txt` first):**
    ```bash
    pip install -r requirements.txt
    ```
    **`requirements.txt` content:**
    ```
    PyQt6>=6.0.0
    requests>=2.25.0
    psutil>=5.8.0
    PyInstaller>=5.0.0
    wmi; platform_system == "Windows"
    pywin32; platform_system == "Windows"
    ```

4.  **Configure Links (Optional):**
    Update placeholders in `app_config.py` (Discord invite is already set to yours).
    *   `YOUTUBE_URL = "https://www.youtube.com/@TrinityT"`
    *   `GITHUB_URL = "https://github.com/Trinitysudo"`

5.  **Prepare Icons:**
    Ensure `cerberus_icon.png` (app), `cerberus_icon.ico` (payload), `discord_icon.png`, `youtube_icon.png`, `github_icon.png` are in the project root.

### Running

```bash
python cerberus_app.py
