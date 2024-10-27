from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QAction, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTabBar, QFileDialog, QMessageBox
from PyQt5.QtGui import QFont
import json
import os

from browser.extension import ExtensionManager
from browser.settings import SettingsDialog

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tab_count = 0
        self.theme_file_path = "styles.json"  # Default path for the theme file
        
        # Load styles and initialize UI
        self.styles = self.load_styles(self.theme_file_path)  
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create ExtensionManager instance
        self.extension_manager = ExtensionManager(self)
        
        # Connect extension signals to slots
        self.extension_manager.extension_enabled.connect(self.on_extension_enabled)
        self.extension_manager.extension_disabled.connect(self.on_extension_disabled)
        
        self.add_new_tab()  # Create the initial tab

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        back_btn = QPushButton('←')
        back_btn.clicked.connect(self.current_browser().back)

        forward_btn = QPushButton('→')
        forward_btn.clicked.connect(self.current_browser().forward)
        
        refresh_btn = QPushButton('⟳')
        refresh_btn.clicked.connect(self.refresh_current_tab)

        # Create a horizontal layout for the buttons and URL bar
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(forward_btn)
        nav_layout.addWidget(refresh_btn)
        nav_layout.addWidget(self.url_bar)

        # Create the main vertical layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.create_menu()
        self.tabs.currentChanged.connect(self.update_url_bar)

        self.set_styles()

        self.show()
        
        # Load cookies from a file if it exists
        self.load_cookies()
    
    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()


    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if key == Qt.Key_N and modifiers == Qt.ControlModifier:
            self.add_new_tab()
        elif key == Qt.Key_W and modifiers == Qt.ControlModifier:
            self.close_tab(self.tabs.currentIndex())

    def refresh_current_tab(self):
        if self.current_browser() is not None:
            self.current_browser().reload()

    def load_styles(self, file_path):
        # Load styles from the specified JSON file
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return {}

    def json_to_stylesheet(self, styles):
        stylesheet = ""
        for selector, properties in styles.items():
            props = "; ".join(f"{key}: {value}" for key, value in properties.items())
            stylesheet += f"{selector} {{{props};}}\n"
        return stylesheet

    def set_styles(self):
        stylesheet = self.json_to_stylesheet(self.styles)
        self.setStyleSheet(stylesheet)

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        new_tab_action = QAction('New Tab (Ctrl + N)', self)
        file_menu.addAction(new_tab_action)

        theme_menu = menu_bar.addMenu('Theme')
        theme_action = QAction('Set Theme File', self)
        theme_menu.addAction(theme_action)

        help_menu = menu_bar.addMenu('Help')
        about_action = QAction('About', self)
        help_menu.addAction(about_action)
        
        settings_menu = menu_bar.addMenu('Settings')
        settings_action = QAction('Preferences', self)
        settings_menu.addAction(settings_action)

        # Connect actions to methods
        new_tab_action.triggered.connect(self.add_new_tab)
        theme_action.triggered.connect(self.set_theme_file)
        about_action.triggered.connect(self.show_about)
        settings_action.triggered.connect(self.show_settings)
        extensions_menu = menu_bar.addMenu('Extensions')
            
        for ext_name in self.extension_manager.extensions.keys():
            enable_action = QAction(f'Enable {ext_name}', self)
            enable_action.triggered.connect(lambda _, name=ext_name: self.extension_manager.enable_extension(name))
            extensions_menu.addAction(enable_action)

            disable_action = QAction(f'Disable {ext_name}', self)
            disable_action.triggered.connect(lambda _, name=ext_name: self.extension_manager.disable_extension(name))
            extensions_menu.addAction(disable_action)

            remove_action = QAction(f'Remove {ext_name}', self)
            remove_action.triggered.connect(lambda _, name=ext_name: self.extension_manager.remove_extension(name))
            extensions_menu.addAction(remove_action)
            
    def on_extension_enabled(self, name):
        QMessageBox.information(self, "Extension Enabled", f"Extension '{name}' has been enabled.")

    def on_extension_disabled(self, name):
        QMessageBox.information(self, "Extension Disabled", f"Extension '{name}' has been disabled.")

    def add_new_tab(self):
        self.tab_count += 1
        new_browser = QWebEngineView()
        
        custom_user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Netrophobe/1.0 Safari/537.36"
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(custom_user_agent)

        new_browser.setUrl(QUrl('http://www.google.com'))
        new_browser.titleChanged.connect(lambda title: self.update_tab_title(title, self.tab_count))

        self.tabs.addTab(new_browser, "New Tab")
        self.tabs.setCurrentWidget(new_browser)

        close_button = QPushButton('×', self)
        close_button.setFixedSize(26, 25)
        close_button.clicked.connect(lambda: self.close_tab(self.tab_count - 1))
        self.tabs.tabBar().setTabButton(self.tabs.indexOf(new_browser), QTabBar.RightSide, close_button)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_to_url(self, url=None):
        if url is None:
            url = self.url_bar.text().strip()
        
        if not url.startswith('http://') and not url.startswith('https://'):
            if '.' not in url:
                search_query = '+'.join(url.split())
                url = f'https://www.google.com/search?q={search_query}'
            else:
                url = 'http://' + url
        
        self.current_browser().setUrl(QUrl(url))
        self.update_url_bar()

    def current_browser(self):
        return self.tabs.currentWidget()

    def update_url_bar(self):
        current_url = self.current_browser().url().toString()
        self.url_bar.setText(current_url)

    def update_tab_title(self, title, tab_index):
        self.tabs.setTabText(tab_index - 1, title)

    def show_about(self):
        self.add_new_tab()
        self.navigate_to_url("https://github.com/hydrophobis/Netrophobe")

    def set_theme_file(self):
        options = QFileDialog.Options()  # Initialize options
        options |= QFileDialog.ReadOnly  # Set to read-only
        file_name, _ = QFileDialog.getOpenFileName(self, 
                                                    "Select Theme File", 
                                                    "", 
                                                    "JSON Files (*.json);;All Files (*)", 
                                                    options=options)  # Pass options as a keyword argument

        if file_name:
            self.theme_file_path = file_name  # Save the selected file path
            self.styles = self.load_styles(self.theme_file_path)
            if self.styles:  # Ensure styles were loaded
                self.set_styles()
                self.save_theme_file_path()  # Save the path for future use
            else:
                print("No valid styles found in the selected file.")




    def save_theme_file_path(self):
        # Save the theme file path to a JSON file
        with open("theme_path.json", "w") as file:
            json.dump({"theme_file": self.theme_file_path}, file)

    def load_cookies(self):
        # Load cookies if they exist
        cookies_file = "cookies.json"
        if os.path.exists(cookies_file):
            with open(cookies_file, "r") as file:
                cookies = json.load(file)
                profile = QWebEngineProfile.defaultProfile()
                for cookie in cookies:
                    profile.cookieStore().setCookie(cookie)

    def closeEvent(self, event):
        # Save cookies to a file when closing the application
        cookies_file = "cookies.json"
        profile = QWebEngineProfile.defaultProfile()
        cookies = []
        profile.cookieStore().allCookies().then(lambda all_cookies: [
            cookies.append(cookie) for cookie in all_cookies
        ])
        
        with open(cookies_file, "w") as file:
            json.dump(cookies, file)

        event.accept()
        
