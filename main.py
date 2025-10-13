import sys
from PyQt6.QtWidgets import QApplication
from GUI.main_window import MatrixMainWindow

def main():
    app = QApplication(sys.argv)

    # Create and show the main Matrix UI
    window = MatrixMainWindow()
    window.show()

    # Run the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
