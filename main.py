# F:/Cerebus/main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Assuming cerberus_gui.py is in the same directory
from cerberus_gui import CerberusBuilderApp 
from app_config import ORGANIZATION_NAME, APPLICATION_NAME, DEFAULT_APP_ICON_FILENAME 

if __name__ == '__main__':
    QApplication.setOrganizationName(ORGANIZATION_NAME)
    QApplication.setApplicationName(APPLICATION_NAME)
    
    app = QApplication(sys.argv)
    
    # Set application icon
    # project_root is determined relative to this main.py file
    project_root = os.path.dirname(os.path.abspath(sys.argv[0]))
    app_icon_path = os.path.join(project_root, "icons", DEFAULT_APP_ICON_FILENAME)
    if os.path.exists(app_icon_path): 
        app.setWindowIcon(QIcon(app_icon_path))
    else: 
        print(f"Warning: Main application icon not found at '{app_icon_path}' from main.py")

    builder_app = CerberusBuilderApp() # CerberusBuilderApp's __init__ now knows its project_root
    builder_app.show()
    sys.exit(app.exec())