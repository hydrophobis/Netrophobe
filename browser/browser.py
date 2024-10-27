from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QAction, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import json

class Browser(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.tab_count = 0
        
        self.styles = self.load_styles()  # Load styles at initialization
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.add_new_tab()  # Create the initial tab

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        back_btn = QPushButton('<-')
        back_btn.clicked.connect(self.current_browser().back)

        forward_btn = QPushButton('->')
        forward_btn.clicked.connect(self.current_browser().forward)

        # Create a horizontal layout for the buttons and URL bar
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(forward_btn)
        nav_layout.addWidget(self.url_bar)

        # Create the main vertical layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.create_menu()
        self.tabs.currentChanged.connect(self.update_url_bar)  # Update URL bar on tab change

        self.set_styles()  # Set initial styles

        self.show()

    def load_styles(self):
        # Load styles from JSON file
        with open("styles.json", "r") as file:
            return json.load(file)

    def json_to_stylesheet(self, styles):
        stylesheet = ""
        for selector, properties in styles.items():
            props = "; ".join(f"{key}: {value}" for key, value in properties.items())
            stylesheet += f"{selector} {{{props};}}\n"
        return stylesheet

    def set_styles(self):
        # Construct the stylesheet from the JSON structure
        stylesheet = self.json_to_stylesheet(self.styles)
        
        # Apply the constructed stylesheet
        self.setStyleSheet(stylesheet)


    def create_menu(self):
        menu_bar = self.menuBar()

        # Create the File menu
        file_menu = menu_bar.addMenu('File')
        new_tab_action = QAction('New Tab', self)
        file_menu.addAction(new_tab_action)

        # Create the Help menu
        help_menu = menu_bar.addMenu('Help')
        about_action = QAction('About', self)
        help_menu.addAction(about_action)

        # Connect actions to methods
        new_tab_action.triggered.connect(self.add_new_tab)
        about_action.triggered.connect(self.show_about)

    def add_new_tab(self):
        self.tab_count += 1
        new_browser = QWebEngineView()
        new_browser.setUrl(QUrl('http://www.google.com'))

        new_browser.titleChanged.connect(lambda title: self.update_tab_title(title, self.tab_count))

        self.tabs.addTab(new_browser, f'Tab {self.tab_count}')
        self.tabs.setCurrentWidget(new_browser)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        self.current_browser().setUrl(QUrl(url))
        self.update_url_bar()

    def current_browser(self):
        return self.tabs.currentWidget()  # Get the currently active QWebEngineView

    def update_url_bar(self):
        current_url = self.current_browser().url().toString()
        self.url_bar.setText(current_url)

    def update_tab_title(self, title, tab_index):
        self.tabs.setTabText(tab_index - 1, title)

    def show_about(self):
        print("About action triggered")  # Placeholder
