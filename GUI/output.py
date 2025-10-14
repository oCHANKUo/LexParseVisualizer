from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QPushButton, QHBoxLayout, QScrollArea
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
        self.resize(900, 600)
        self.setStyleSheet("background-color: black; color: #00FF66;")
        self.showMaximized()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(20)

        # --- Title ---
        title = QLabel("LEXICAL ANALYSIS RESULT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00FF66;
                font-size: 28px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                letter-spacing: 2px;
            }
        """)
        main_layout.addWidget(title)

        # --- Horizontal Layout (Table + Parse Tree) ---
        row_layout = QHBoxLayout()
        row_layout.setSpacing(40)

        # --- TOKEN TABLE ---
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
                border: 1px solid #00FF66;
            }
            QHeaderView::section {
                background-color: #00FF66;
                color: black;
                font-weight: bold;
            }
        """)
        self.load_tokens(tokens)
        row_layout.addWidget(self.table, stretch=1)

        # --- PARSE TREE AREA ---
        try:
            parse_tree, error_msg = parse_tokens(tokens)
            tree_str = self.format_tree(parse_tree)
            print("[DEBUG] Parse tree string:\n", tree_str)
        except Exception as e:
            tree_str = f"Parse Error: {e}"
            error_msg = str(e)
            print("[DEBUG] Exception in parse tree:", e)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(10, 10, 10, 10)

        self.tree_display = QLabel(tree_str)
        self.tree_display.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.tree_display.setStyleSheet("""
            QLabel {
                color: #00FF66;
                font-size: 17px;
                font-family: 'Courier New', monospace;
                background: #000;
                border: 1px solid #00FF66;
                border-radius: 6px;
                padding: 14px 20px;
                line-height: 180%;
            }
        """)
        self.tree_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        tree_layout.addWidget(self.tree_display)

        # --- ERROR LABEL ---
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
        tree_layout.addWidget(self.error_label)

        scroll.setWidget(tree_container)
        row_layout.addWidget(scroll, stretch=2)
        main_layout.addLayout(row_layout)

        # --- NEXT INPUT BUTTON ---
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
                border-radius: 10px;
                padding: 12px 36px;
                margin-top: 30px;
            }
            QPushButton:hover {
                background-color: #00cc55;
            }
        """)
        self.next_input_btn.clicked.connect(self.next_input_requested.emit)
        btn_layout.addWidget(self.next_input_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    # --- Populate token table ---
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

    # --- Corrected tree formatting ---
    def format_tree(self, node, prefix="", is_last=True):
        if node is None:
            return f"{prefix}└── [Empty Parse Tree]"

        branch = "└── " if is_last else "├── "
        spacing = "  "  # small gap between levels

        # Leaf node with value
        if hasattr(node, "value") and node.value is not None and not node.children:
            return f"{prefix}{branch}{node.value}"

        # Skip epsilon/empty
        if hasattr(node, "children") and not node.children and node.value is None:
            return ""

        # Determine visible (non-empty) children
        visible_children = []
        if hasattr(node, "children"):
            for c in node.children:
                if c is not None:
                    s = self.format_tree(c)
                    if s.strip():
                        visible_children.append(c)

        # Current node
        lines = [f"{prefix}{branch}{node.name}"]

        # Recurse properly with last-child check
        for i, child in enumerate(visible_children):
            last_child = (i == len(visible_children) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            child_str = self.format_tree(child, child_prefix + spacing, last_child)
            if child_str.strip():
                lines.append(child_str)

        return "\n".join(lines)
