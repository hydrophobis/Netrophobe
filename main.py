import sys
from PyQt5.QtWidgets import QApplication
from browser.browser import Browser

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Browser() 
    window.setWindowTitle('Netrophobe')
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
