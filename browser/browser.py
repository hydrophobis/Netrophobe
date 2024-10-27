from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QAction, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTabBar
from PyQt5.QtCore import Qt
import json

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tab_count = 0
        
        # Load styles and initialize UI
        self.styles = self.load_styles()  
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.add_new_tab()  # Create the initial tab

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        back_btn = QPushButton('←')
        back_btn.clicked.connect(self.current_browser().back)

        forward_btn = QPushButton('→')
        forward_btn.clicked.connect(self.current_browser().forward)
        
        refresh_btn = QPushButton('⟳')
        refresh_btn.clicked.connect(self.refresh_current_tab)  # Connect to the refresh method

        # Create a horizontal layout for the buttons and URL bar
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(forward_btn)
        nav_layout.addWidget(refresh_btn)  # Add the refresh button to the layout
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
        
    def keyPressEvent(self, event):
        # Check for Ctrl + N
        if event.key() == Qt.Key_N and event.modifiers() == Qt.ControlModifier:
            self.add_new_tab()

    def refresh_current_tab(self):
        if self.current_browser() is not None:
            self.current_browser().reload()


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
        new_tab_action = QAction('New Tab(Ctrl + N)', self)
        file_menu.addAction(new_tab_action)

        # Create the Help menu
        help_menu = menu_bar.addMenu('Help')
        about_action = QAction('About', self)
        help_menu.addAction(about_action)
        
        # Create the Help menu
        help_menu = menu_bar.addMenu('Theme')
        about_action = QAction('Set file', self)
        help_menu.addAction(about_action)

        # Connect actions to methods
        new_tab_action.triggered.connect(self.add_new_tab)
        about_action.triggered.connect(self.show_about)

    def add_new_tab(self):
        self.tab_count += 1

        # Create a new QWebEngineView
        new_browser = QWebEngineView()
        
        # Set the custom user agent
        custom_user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Netrophobe/1.0 Chrome/87.0.4280.144 Safari/537.36"
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(custom_user_agent)

        # Set the initial URL
        new_browser.setUrl(QUrl('http://www.google.com'))

        new_browser.titleChanged.connect(lambda title: self.update_tab_title(title, self.tab_count))

        # Add the new tab
        self.tabs.addTab(new_browser, "New Tab")
        self.tabs.setCurrentWidget(new_browser)

        # Add close button to the tab
        close_button = QPushButton("✕")
        close_button.setFixedSize(20, 20)
        close_button.setObjectName("CloseButton")
        close_button.clicked.connect(lambda: self.close_tab(self.tab_count - 1))  # Close the tab
        self.tabs.tabBar().setTabButton(self.tabs.indexOf(new_browser), QTabBar.RightSide, close_button)
        
    def close_tab(self, index):
        if self.tabs.count() > 1:  # Prevent closing the last tab
            self.tabs.removeTab(index)

    def navigate_to_url(self, url=None):
        if url is None:  # If no URL is provided, get it from the URL bar
            url = self.url_bar.text().strip()
        
        # Check if the input is a search
        if not url.startswith('http://') and not url.startswith('https://'):
            # If the input doesn't contain a dot, assume it's a search query
            if '.' not in url:
                search_query = '+'.join(url.split())  # Replace spaces with '+'
                url = f'https://www.google.com/search?q={search_query}'
            else:
                url = 'http://' + url  # Otherwise, treat it as a URL
        
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
        self.add_new_tab()
        self.navigate_to_url("https://github.com/hydrophobis/Netrophobe")
