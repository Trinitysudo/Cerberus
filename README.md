# Cerberus Payload Builder 🛠️

<!-- Main Badges -->
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=for-the-badge&logo=python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT) <!-- Ensure this matches your chosen license -->
[![Discord](https://img.shields.io/discord/YOUR_SERVER_ID?label=Join%20Discord&logo=discord&logoColor=white&color=7289DA&style=for-the-badge)](https://discord.gg/3ZSVqbbUwJ) <!-- Replace YOUR_SERVER_ID with your actual Discord Server ID -->

**Cerberus Builder** is a Python (v3.9+) GUI application built with PyQt6, designed for creating payloads that gather system information and can optionally offer more interactive capabilities. This tool is intended as a **proof-of-concept** and for **educational purposes only** to demonstrate information gathering techniques, payload generation, and basic remote interaction concepts.

⚠️ **Disclaimer:** This tool is for educational use ONLY. You are solely responsible for your actions. Unauthorized access to computer systems is illegal. The developers assume no liability and are not responsible for any misuse or damage caused by this program.

## ✨ Core Features

*   🖥️ **Operating System Details**: Version, release, build, architecture.
*   ⚙️ **Hardware Specifications**: CPU model, cores, frequency; total/available RAM; GPU info (Windows via WMI).
*   💾 **Disk Usage**: Mounted drives, filesystem type, total, used, and free space.
*   🌐 **Network Configuration**: Details about network interfaces.

### 🤖 Optional Bot Functionality & Real-time Interaction (Payload Capabilities):

*   **Interactive Agent Mode**: Payloads can be configured to operate in a more persistent "bot" mode.
    *   *(Describe what this mode enables, e.g., "Allows the payload to listen for basic commands sent via a configured channel," or "Enables continuous data streaming to a specified endpoint.")*
*   **Configuration via "Real-time" Tab**:
    *   The **"Real-time" tab** in the Cerberus Builder GUI is used to enable and configure these advanced features for the payload.
    *   This may include settings such as:
        *   Connection parameters (e.g., C2 server address/port, different from the Discord webhook for initial reports).
        *   Check-in intervals.
        *   Specific commands the payload should listen for.
        *   Data streaming options.
    *   *(Be specific here about what can be configured in your "Real-time" tab for the bot functionality).*
*   **Updating Bot Behavior**: To change the bot's behavior or commands it responds to, you would typically re-configure these settings in the "Real-time" tab and generate a new payload.
    *   *(If the "Real-time" tab ALSO allows sending live commands or updates to an ALREADY RUNNING payload, clarify that here. E.g., "The 'Real-time' tab may also provide an interface to send commands to active bots, if a C2 communication channel is established.")*

### Builder Application Features:

*   📊 **Real-time Progress & Logging**: A visual progress bar and a detailed build log area within the application provide feedback during payload compilation.

---

## 🖼️ Screenshots

*   **Cerberus Builder Interface (Main Tab):**
*   
    ![GUI PREVIEW](https://github.com/user-attachments/assets/1c549e43-1baa-4795-932b-8275851c9d26)

*   **Cerberus Builder Interface (Real-time Tab):**
*    ![GUI PREVIEW]![python3 12_qpeJhfxdSw](https://github.com/user-attachments/assets/6a3f7db3-83ea-4fe9-957c-f0562c3f329b)

*   **Example Discord Report Embed (IP OPTIONS NOT INCLUDED):**
    ![NVIDIA_Overlay_LeQUXPUGWp](https://github.com/user-attachments/assets/2149edfc-052b-475d-b042-8f2217adbacd)



---

## 🚀 Getting Started

### Prerequisites

*   **Python 3.9 or higher**
*   **Git** (for cloning the repository)
*   A **Discord Webhook URL** (for receiving initial reports from generated payloads).
*   *(Add any other prerequisites specific to the bot/real-time functionality, e.g., a server endpoint if not using Discord for commands).*

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
