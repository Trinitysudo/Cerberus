# Cerberus Payload Builder 🛠️

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
[![Discord](https://img.shields.io/discord/YOUR_SERVER_ID?label=Join%20Our%20Discord&logo=discord&logoColor=white&color=7289DA&style=for-the-badge)](https://discord.gg/3ZSVqbbUwJ)
<!-- Replace YOUR_SERVER_ID with your actual Discord Server ID -->
<!-- You can generate more badges here: https://shields.io/ -->

**Cerberus Builder** is a Python GUI application (PyQt6) it is a R.A.T Builder (Remote Accese Tool) This is for proof of concept

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

2.  **Install Dependencies (Create `requirements.txt` first):**
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

### Running

```bash
python cerberus_app.py
```

## 🛠️ How to Use

Launch cerberus_app.py.

Enter your Discord Webhook URL.
Customize Payload Filename, Icon, System Info inclusion, and EXE Size.
Adjust GUI font size using +/- buttons.
Click "Compile Payload".
Find the .exe in the dist/ folder.


## 📁 Project Structure Highlight

cerberus_app.py: Main GUI
app_config.py: Constants & Links
ui_styler.py: Styling (QSS)
ui_setup.py: GUI Layout
system_info.py / webhook_utils.py: Payload logic

## 🤝 Support & Community

Issues/Suggestions: Open an Issue
Join our Community:
![alt text](https://img.shields.io/badge/Discord-Join%20Us-7289DA?style=flat&logo=discord)
My Links:
![alt text](https://img.shields.io/badge/YouTube-%40TrinityT-c4302b?style=social&logo=youtube)
![alt text](https://img.shields.io/badge/GitHub-Trinitysudo-181717?style=social&logo=github)

## ⚖️ Disclaimer

This tool is for legitimate IT administration and educational use within authorized environments only. Misuse is strictly prohibited. Developers assume no liability for unauthorized use. Use responsibly and ethically.

