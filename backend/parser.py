
import ply.yacc as yacc
from lexer import lex_input
from token_def import ALL_TOKENS

tokens = ALL_TOKENS

# Node Class
class Node:
    def __init__(self, name, children=None, value=None):
        self.name = name
        self.children = children if children is not None else []
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f"{self.name}({self.value})"
        else:
            return f"{self.name}({self.children})"
