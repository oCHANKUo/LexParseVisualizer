import sys
import os
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QLabel, QFrame, QSizePolicy, QStackedLayout,
    QGraphicsDropShadowEffect, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# --- Add the backend folder to Python’s path ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "backend"))

# --- Import the lexer function and output window ---
from backend.lexer import lexer
from GUI.output import OutputWindow


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Matrix Rain</title>
<style>
  html, body { height: 100%; margin: 0; overflow: hidden; background: #000; }
  main { display: flex; width: 100%; height: 100%; }
  p { line-height: 1; margin: 0; padding: 0 4px; }
  span {
    display: block; width: 2vmax; height: 2vmax;
    font-size: 2vmax; color: #9bff9b11;
    text-align: center; font-family: "Helvetica Neue", Helvetica, sans-serif;
  }
</style>
</head>
<body><main></main>
<script>
function r(f,t){return~~(Math.random()*(t-f+1)+f)}
function pick(){return arguments[r(0,arguments.length-1)]}
function getChar(){return String.fromCharCode(pick(r(0x3041,0x30ff),r(0x2000,0x206f),r(0x0020,0x003f)))}
function loop(fn,delay){let s=Date.now();function L(){if(Date.now()-s>=delay){fn();s=Date.now()}requestAnimationFrame(L)}requestAnimationFrame(L)}
class Char{constructor(){this.element=document.createElement('span');this.mutate()}mutate(){this.element.textContent=getChar()}}
class Trail{constructor(list=[],o){this.list=list;this.options=Object.assign({size:10,offset:0},o);this.body=[];this.move()}traverse(fn){this.body.forEach((n,i)=>{let last=(i==this.body.length-1);if(n)fn(n,i,last)})}move(){this.body=[];let{offset,size}=this.options;for(let i=0;i<size;++i){let item=this.list[offset+i-size+1];this.body.push(item)}this.options.offset=(offset+1)%(this.list.length+size-1)}}
class Rain{constructor({target,row}){this.element=document.createElement('p');this.build(row);if(target)target.appendChild(this.element);this.drop()}build(row=20){let root=document.createDocumentFragment();let chars=[];for(let i=0;i<row;++i){let c=new Char();root.appendChild(c.element);chars.push(c);if(Math.random()<.5){loop(()=>c.mutate(),r(1e3,5e3))}}this.trail=new Trail(chars,{size:r(10,30),offset:r(0,100)});this.element.appendChild(root)}drop(){let t=this.trail;let len=t.body.length;let delay=r(10,100);loop(()=>{t.move();t.traverse((c,i,last)=>{c.element.style=`color:hsl(136,100%,${85/len*(i+1)}%)`;if(last){c.mutate();c.element.style=`color:hsl(136,100%,85%);`}})},delay)}}
const main=document.querySelector('main');
for(let i=0;i<50;++i){new Rain({target:main,row:50})}
</script></body></html>
"""


class MatrixMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matrix Input")
        self.setStyleSheet("QMainWindow { background: black; }")
        self.setWindowState(Qt.WindowState.WindowMaximized)

        root = QFrame(self)
        self.setCentralWidget(root)
        self.stacked = QStackedLayout(root)
        self.stacked.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # Background animation
        self.web = QWebEngineView(self)
        self.web.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stacked.addWidget(self.web)

        # Overlay setup (input page)
        self.overlay = QWidget(self)
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.setSpacing(40)

        # Typing label
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 72px;
                font-weight: 500;
                font-family: 'Courier New', 'Consolas', 'Fira Code', monospace;
                letter-spacing: 3px;
            }
        """)
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(40)
        glow.setColor(QColor(255, 255, 255))
        glow.setOffset(0, 0)
        self.label.setGraphicsEffect(glow)
        overlay_layout.addWidget(self.label)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setFixedWidth(800)
        self.input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 48px;
                font-family: 'Courier New', 'Consolas', 'Fira Code', monospace;
                selection-background-color: rgba(255,255,255,0.25);
                selection-color: white;
            }
            QLineEdit:focus {
                border: none;
                outline: none;
            }
        """)

        pal = self.input_field.palette()
        pal.setColor(QPalette.ColorRole.Text, QColor("white"))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(255, 255, 255, 50))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("white"))
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        self.input_field.setPalette(pal)

        self.input_field.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        QTimer.singleShot(300, self.input_field.setFocus)

        # Connect Enter key to backend lexer
        self.input_field.returnPressed.connect(self.process_input)

        # Error label below input field
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("""
            QLabel {
                color: #ff3333;
                font-size: 24px;
                font-family: 'Courier New', monospace;
                margin-top: 10px;
            }
        """)
        overlay_layout.addWidget(self.input_field)
        overlay_layout.addWidget(self.error_label)  # Add error label below input
        self.stacked.addWidget(self.overlay)
        self.stacked.setCurrentWidget(self.overlay)

        # Load Matrix animation
        QTimer.singleShot(100, lambda: self.web.setHtml(HTML, QUrl("about:blank")))

        # Typing animation setup
        self.full_text = "ENTER YOUR INPUT"
        self.displayed_text = ""
        self.index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.type_next_char)
        self.timer.start(250)

        self.output_window = None

    def type_next_char(self):
        if self.index < len(self.full_text):
            self.displayed_text += self.full_text[self.index]
            self.label.setText(f"{self.displayed_text}|")
            self.index += 1
        else:
            self.timer.stop()
            self.label.setText(self.full_text)

    def process_input(self):
        user_input = self.input_field.text().strip()
        self.error_label.setText("")  # Clear previous error
        if not user_input:
            self.error_label.setText("Input cannot be empty.")
            return

        try:
            tokens = lexer(user_input)
            print("\nInput:", user_input)
            print("Tokens:", tokens)

            # Create OutputWindow and switch to it
            self.output_window = OutputWindow(tokens)
            self.output_window.next_input_requested.connect(self.show_input_page)
            self.stacked.addWidget(self.output_window)
            self.stacked.setCurrentWidget(self.output_window)

        except Exception as e:
            self.error_label.setText(str(e))

    def show_input_page(self):
        # Remove output window from stacked layout
        if self.output_window:
            self.stacked.removeWidget(self.output_window)
            self.output_window.deleteLater()
            self.output_window = None

        # Clear input field
        self.input_field.clear()
        self.input_field.setFocus()

        # Reset typing animation and label
        self.displayed_text = ""
        self.index = 0
        self.label.setText("")
        self.timer.start(250)

        # Switch to input overlay
        self.stacked.setCurrentWidget(self.overlay)
        self.error_label.setText("")  # Clear error when returning to input


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MatrixMainWindow()
    window.show()
    sys.exit(app.exec())
