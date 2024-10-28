from PyQt5.QtCore import QObject, QJsonDocument, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
import os

class ExtensionManager(QObject):
    extension_enabled = pyqtSignal(str)  # Signal to notify when an extension is enabled
    extension_disabled = pyqtSignal(str)  # Signal to notify when an extension is disabled

    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.extensions = {}
        self.load_extensions()

    # Loads extensions from the extension dir
    def load_extensions(self):
        # Load extensions from a directory (e.g., "extensions/")
        extension_dir = "extensions/"
        if not os.path.exists(extension_dir):
            os.makedirs(extension_dir)  # Create directory if it doesn't exist

        for filename in os.listdir(extension_dir):
            if filename.endswith('.json'):
                self.load_extension(os.path.join(extension_dir, filename))

    # Loads an extension given the path
    def load_extension(self, path):
        with open(path, 'r') as file:
            data = QJsonDocument.fromJson(file.read().encode()).object()
            name = data.get('name', 'Unnamed Extension')
            self.extensions[name] = data
            print(f"Loaded extension: {name}")

    # Enables an extension
    def enable_extension(self, name):
        if name in self.extensions:
            # Implement enabling logic
            extension_data = self.extensions[name]
            # Example: Execute a script if provided
            scripts = extension_data.get('scripts', [])
            for script in scripts:
                self.execute_script(script)  # Implement script execution logic

            self.extension_enabled.emit(name)  # Emit signal
            print(f"Enabled extension: {name}")
        else:
            QMessageBox.warning(self.browser, "Error", f"Extension '{name}' not found.")

    # Disables an extension
    def disable_extension(self, name):
        if name in self.extensions:
            # Implement disabling logic (if needed)
            self.extension_disabled.emit(name)  # Emit signal
            print(f"Disabled extension: {name}")
        else:
            QMessageBox.warning(self.browser, "Error", f"Extension '{name}' not found.")

    # Removes an extension
    def remove_extension(self, name):
        if name in self.extensions:
            del self.extensions[name]
            print(f"Removed extension: {name}")
        else:
            QMessageBox.warning(self.browser, "Error", f"Extension '{name}' not found.")

    # Executes a javascript file as an extension
    def execute_script(self, script_name):
        # Example: Load and execute a JavaScript file
        script_path = os.path.join("extensions/scripts", script_name)
        if os.path.exists(script_path):
            with open(script_path, 'r') as script_file:
                script_content = script_file.read()
                # Here you would need to execute the script in the browser context
                # For example, using `QWebEngineView`'s `page().runJavaScript()`
                self.browser.current_browser().page().runJavaScript(script_content)
                print(f"Executed script: {script_name}")
        else:
            print(f"Script '{script_name}' not found.")
