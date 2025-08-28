
import ply.yacc as yacc
import token_def as td
# from lexer import lex_input

tokens = td.ALL_TOKENS

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
    "E : T E_PRIME"
    p[0] = Node('E', children=[p[1], p[2]])

# E´→ +TE´|Ɛ 
def p_E_PRIME(p):
    "E_PRIME : PLUS T E_PRIME"
    p[0] = Node('E_PRIME', children=[Node(td.TOKEN_PLUS, value=p[1]), p[2], p[3]])

def p_E_PRIME_empty(p):
    "E_PRIME :"
    p[0] = Node('E_PRIME', children=[])

# T → FT´ 
def p_T(p):
    "T : F T_PRIME"
    p[0] = Node('T', children=[p[1], p[2]])

# T´→ *FT´|Ɛ 
def p_T_PRIME(p):
    "T_PRIME : STAR F T_PRIME"
    p[0] = Node('T_PRIME', children=[Node(td.TOKEN_MUL, value=p[1]), p[2], p[3]])

def p_T_PRIME_empty(p):
    "T_PRIME :"
    p[0] = Node('T_PRIME', children=[])

# F → (E)|id 
def p_F_paren(p):
    "F : LPAREN E RPAREN"
    p[0] = Node('F', children=[Node(td.TOKEN_LPAREN, value=p[1]), p[2], Node(td.TOKEN_RPAREN, value=p[3])])

# id → 0|1|2|3|4|5|6|7|8|9|a…z|A…Z
def p_ID(p):
    "F : IDENTIFIER"
    p[0] = Node(td.TOKEN_ID, children=[], value=p[1])

# Error rule for syntax errors
def p_error(p):
    print("Syntax error at", p.value)

parser = yacc.yacc()

# Use this function with the output of the lexer
# lex_output = lex_input(text)
# parse_tree = parse_tokens(lex_output)
def parse_tokens(lex_output):
    expr_str = "".join([tok['value'] for tok in lex_output])
    return parser.parse(expr_str)

# use parser.parse(user_input) with the user input itself. But the Lexer should still be present
# user_input = "3+4"
# parse_tree = parser.parse(user_input)

# test
if __name__ == "__main__":
    user_input = "3+4"
    # lex_out = lex_input(user_input)
    tree = parser.parse(user_input) # or lex_output
    print(tree)