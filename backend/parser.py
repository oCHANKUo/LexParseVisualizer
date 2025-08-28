
import ply.yacc as yacc
from lexer import lex_input
from token_def import td

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
        

# Grammar Rules
# E → TE´ 
def p_E(p):
    'E: T E_PRIME'
    p[0] = Node('E', children=[p[1], p[2]])

# E´→ +TE´|Ɛ 
def p_E_PRIME(p):
    'E_PRIME: PLUS T E_PRIME'
    p[0] = Node('E_PRIME', children=[Node(td.TOKEN_PLUS, value=p[1]), p[2], p[3]])

# T → FT´ 
# T´→ *FT´|Ɛ 
# F → (E)|id 
# id → 0|1|2|3|4|5|6|7|8|9|a…z|A…Z
