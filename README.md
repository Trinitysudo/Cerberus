# Cerberus Payload Builder 🛠️

<!-- Main Badges -->
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=for-the-badge&logo=python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT) <!-- REPLACE WITH YOUR CHOSEN LICENSE -->
[![GitHub Stars](https://img.shields.io/github/stars/[YourGitHubUsername]/CerberusMalware?style=for-the-badge&logo=github)](https://github.com/[Trinitysudo]/CerberusMalware/stargazers) <!-- Replace [YourGitHubUsername] -->
[![GitHub Forks](https://img.shields.io/github/forks/[YourGitHubUsername]/CerberusMalware?style=for-the-badge&logo=github)](https://github.com/[Trinitysudo]/CerberusMalware/network/members) <!-- Replace [YourGitHubUsername] -->
[![GitHub Issues](https://img.shields.io/github/issues/[YourGitHubUsername]/CerberusMalware?style=for-the-badge&logo=github)](https://github.com/[Trinitysudo]/CerberusMalware/issues) <!-- Replace [YourGitHubUsername] -->
[![Discord](https://img.shields.io/discord/YOUR_SERVER_ID?label=Join%20Discord&logo=discord&logoColor=white&color=7289DA&style=for-the-badge)](https://discord.gg/3ZSVqbbUwJ) <!-- Replace YOUR_SERVER_ID -->

<!-- Optional Social/Activity Badges -->
<!--
[![GitHub last commit](https://img.shields.io/github/last-commit/[YourGitHubUsername]/CerberusMalware?style=flat-square&logo=github)](https://github.com/[YourGitHubUsername]/CerberusMalware/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/[YourGitHubUsername]/CerberusMalware?style=flat-square)](https://github.com/[YourGitHubUsername]/CerberusMalware)
-->

**Cerberus Builder** is a Python (v3.9+) GUI application built with PyQt6, designed for R.A.T (Remote Accese Tool) , made for proof of concept and to be the best not malcious
i  am not responsibile for what you do what so ever with this and if you sell it i will slime you out (no kizzy)

## ✨ Core Features & Capabilities

Cerberus Builder offers a robust set of features for efficient payload creation and information retrieval:

*   **Intuitive GUI Builder**: A clean, themed graphical interface for easy configuration of all payload settings. Includes a built-in font size adjuster (`+`/`-` buttons) for enhanced user comfort and readability.
*   **Comprehensive System Information Gathering**: Payloads can collect a wide array of data from the target Windows machine:
    *   🖥️ **Operating System Details**: Version, release, build, architecture.
    *   ⚙️ **Hardware Specifications**: CPU model, cores, frequency; total and available RAM; GPU information (via WMI on Windows).
    *   💾 **Disk Usage**: Mounted drives, filesystem type, total, used, and free space.
    *   🌐 **Network Configuration**:
    *   📊 **Real-time Progress & Logging**: A visual progress bar and a detailed build log area within the application provide feedback to the user throughout the compilation stages.
*   **Standalone Windows Executables**: The builder generates single, portable `.exe` files. These payloads can run on target Windows machines without requiring Python or any external dependencies to be pre-installed, making deployment straightforward.
*   **Organized & Maintainable Codebase**: The project is structured with a focus on readability and future development. Configuration constants, UI styling (QSS), and UI element setup are modularized into separate Python files (`app_config.py`, `ui_styler.py`, `ui_setup.py`).

---

## 🖼️ Screenshots

**(Screenshots demonstrating the Builder GUI and an example Discord report are highly recommended here. Replace the placeholders below.)**

*   **Cerberus Builder Interface:**
    `![Cerberus Builder GUI](path/to/your/builder_gui_screenshot.png)`

*   **Example Discord Report Embed:**
    `![Sample Discord Embed](path/to/your/discord_embed_screenshot.png)`

---

## 🚀 Getting Started & Usage

### Prerequisites

*   **Python 3.9 or higher**
*   **Git** (for cloning the repository)
*   A **Discord Webhook URL** for receiving reports from the generated payloads.

### Installation & Setup

1.  **Clone the Repository:**
    Open your terminal or command prompt and run:
    ```bash
    git clone https://github.com/[YourGitHubUsername]/CerberusMalware.git
    cd CerberusMalware
    ```
    *(Remember to replace `[YourGitHubUsername]` with your actual GitHub username!)*

2.  **Install Dependencies:**
    The necessary Python packages are listed below. Create a file named `requirements.txt` in the project's root directory with the following content:
    ```
    PyQt6>=6.0.0
    requests>=2.25.0
    psutil>=5.8.0
    PyInstaller>=5.0.0
    wmi; platform_system == "Windows"
    pywin32; platform_system == "Windows"
    ```
    Then, install them using pip:
    ```bash
    pip install -r requirements.txt
    ```


### Running the Cerberus Builder

Once dependencies are installed, launch the builder application:
```bash
python cerberus_app.py
