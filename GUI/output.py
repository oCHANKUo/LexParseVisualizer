from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from backend.parser import parse_tokens
from backend.lexer import lexer


class OutputWindow(QWidget):
    next_input_requested = pyqtSignal()

    def __init__(self, tokens):
        super().__init__()
        self.setWindowTitle("Lexer Output")
        self.resize(700, 500)
        self.setStyleSheet("background-color: black; color: #00FF66;")
        self.showMaximized()  # Show window maximized

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(60, 40, 60, 40)  # Add padding around the page
        main_layout.setSpacing(10)  # Keep table and tree close

        # Title
        title = QLabel("LEXICAL ANALYSIS RESULT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00FF66;
                font-size: 28px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(title)

        # Horizontal layout for table and parse tree
        row_layout = QHBoxLayout()
        row_layout.setSpacing(30)

        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Lexeme", "Token"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #000;
                color: #00FF66;
                font-size: 18px;
                font-family: 'Courier New', monospace;
                gridline-color: #00FF66;
            }
            QHeaderView::section {
                background-color: #00FF66;
                color: black;
                font-weight: bold;
            }
        """)
        self.load_tokens(tokens)
        row_layout.addWidget(self.table, stretch=1)

        # Parse tree display
        try:
            parse_tree, error_msg = parse_tokens(tokens)
            tree_str = self.format_tree(parse_tree)
            print("[DEBUG] Parse tree string:\n", tree_str)
        except Exception as e:
            tree_str = f"Parse Error: {e}"
            error_msg = str(e)
            print("[DEBUG] Exception in parse tree:", e)

        tree_vbox = QVBoxLayout()

        self.tree_display = QLabel(tree_str)
        self.tree_display.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tree_display.setStyleSheet("""
            QLabel {
                color: #00FF66;
                font-size: 16px;
                font-family: 'Courier New', monospace;
                background: #000;
                border: 1px solid #00FF66;
                padding: 8px;
            }
        """)
        self.tree_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        tree_vbox.addWidget(self.tree_display)

        # Error label below tree
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("""
            QLabel {
                color: #ff3333;
                font-size: 18px;
                font-family: 'Courier New', monospace;
                margin-top: 10px;
            }
        """)
        if error_msg:
            self.error_label.setText(error_msg)
        tree_vbox.addWidget(self.error_label)
        row_layout.addLayout(tree_vbox, stretch=2)

        main_layout.addLayout(row_layout)

        # "Enter Next Input" button centered below
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_input_btn = QPushButton("Enter Next Input")
        self.next_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #00FF66;
                color: black;
                font-size: 20px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 32px;
                margin-top: 24px;
            }
            QPushButton:hover {
                background-color: #00cc55;
            }
        """)
        self.next_input_btn.clicked.connect(self.next_input_requested.emit)
        btn_layout.addWidget(self.next_input_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def load_tokens(self, tokens):
        self.table.setRowCount(len(tokens))
        for row, token_data in enumerate(tokens):
            lexeme_item = QTableWidgetItem(str(token_data.get("lexeme", "")))
            token_item = QTableWidgetItem(str(token_data.get("token", "")))

            for item in (lexeme_item, token_item):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor("#00FF66"))
                item.setFont(QFont("Courier New", 14))

            self.table.setItem(row, 0, lexeme_item)
            self.table.setItem(row, 1, token_item)

    def format_tree(self, node, prefix="", is_last=True):
        if node is None:
            return f"{prefix}└── [Empty Parse Tree]"
        branch = "└── " if is_last else "├── "
        # Leaf node with value
        if hasattr(node, "value") and node.value is not None and not node.children:
            return f"{prefix}{branch}{node.value}"
        # Node with no children and no value (epsilon) -- SKIP, do not add any line
        if hasattr(node, "children") and not node.children and node.value is None:
            return ""
        # Otherwise, show node name and recurse for children
        lines = [f"{prefix}{branch}{node.name}"]
        if hasattr(node, "children") and node.children:
            child_prefix = prefix + ("    " if is_last else "│   ")
            visible_children = [child for child in node.children if child is not None]
            for i, child in enumerate(visible_children):
                last = (i == len(visible_children) - 1)
                child_str = self.format_tree(child, child_prefix, last)
                if child_str.strip():
                    lines.append(child_str)
        return "\n".join(lines)
