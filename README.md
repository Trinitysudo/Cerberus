# Cerberus Payload Builder 🛠️

<!-- Main Badges -->
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=for-the-badge&logo=python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT) <!-- Ensure this matches your chosen license -->
[![GitHub Stars](https://img.shields.io/github/stars/Trinitysudo/CerberusMalware?style=for-the-badge&logo=github)](https://github.com/Trinitysudo/CerberusMalware/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Trinitysudo/CerberusMalware?style=for-the-badge&logo=github)](https://github.com/Trinitysudo/CerberusMalware/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/Trinitysudo/CerberusMalware?style=for-the-badge&logo=github)](https://github.com/Trinitysudo/CerberusMalware/issues)
[![Discord](https://img.shields.io/discord/YOUR_SERVER_ID?label=Join%20Discord&logo=discord&logoColor=white&color=7289DA&style=for-the-badge)](https://discord.gg/3ZSVqbbUwJ) <!-- Replace YOUR_SERVER_ID with your actual Discord Server ID -->

<!-- Optional Social/Activity Badges (Uncomment and fill if desired) -->
<!--
[![GitHub last commit](https://img.shields.io/github/last-commit/Trinitysudo/CerberusMalware?style=flat-square&logo=github)](https://github.com/Trinitysudo/CerberusMalware/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/Trinitysudo/CerberusMalware?style=flat-square)](https://github.com/Trinitysudo/CerberusMalware)
-->

**Cerberus Builder** is a Python (v3.9+) GUI application built with PyQt6, designed for creating payloads that gather system information. This tool is intended as a **proof-of-concept** and for **educational purposes only** to demonstrate information gathering techniques and payload generation.

⚠️ **Disclaimer:** This tool is for educational use ONLY. You are solely responsible for your actions. Unauthorized access to computer systems is illegal. The developers assume no liability and are not responsible for any misuse or damage caused by this program.

## ✨ Core Features

The generated payloads can gather:

*   🖥️ **Operating System Details**: Version, release, build, architecture.
*   ⚙️ **Hardware Specifications**: CPU model, cores, frequency; total/available RAM; GPU info (Windows via WMI).
*   💾 **Disk Usage**: Mounted drives, filesystem type, total, used, and free space.
*   🌐 **Network Configuration**: Details about network interfaces.

The builder application itself provides:

*   📊 **Real-time Progress & Logging**: A visual progress bar and a detailed build log area.

---

## 🖼️ Screenshots

*   **Cerberus Builder Interface:**
    ![GUI PREVIEW](https://github.com/user-attachments/assets/1c549e43-1baa-4795-932b-8275851c9d26)

*   **Example Discord Report Embed:**
    `<!-- ![Sample Discord Embed](path/to/your/discord_embed_screenshot.png) -->`
    <!-- Add your Discord embed screenshot here and uncomment the line above -->

---

## 🚀 Getting Started

### Prerequisites

*   **Python 3.9 or higher**
*   **Git** (for cloning the repository)
*   A **Discord Webhook URL** (if you intend to use the Discord reporting feature of the generated payloads).

### Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Trinitysudo/CerberusMalware.git
    cd CerberusMalware
    ```
    *(If you've forked this, replace `Trinitysudo` with your GitHub username).*

2.  **Install Dependencies:**
    Navigate to the project's root folder (`CerberusMalware`) in your terminal or command prompt and run:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Cerberus Builder

Once dependencies are installed, launch the builder application:
```bash
python main.py
