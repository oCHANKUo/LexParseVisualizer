
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
    "T_PRIME : MUL F T_PRIME"
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

class ListLexer:
    def __init__(self, token_list):
        self.tokens = token_list
        self.index = 0
        print("[DEBUG] Lexer input tokens:")
        for t in token_list:
            print(f"  {t}")

    def token(self):
        if self.index < len(self.tokens):
            t = self.tokens[self.index]
            print(f"[DEBUG] Yielding token: {t}")
            self.index += 1
            class DummyToken:
                pass
            tok = DummyToken()
            tok.type = t["token"]  # Should be 'IDENTIFIER', 'PLUS', etc.
            tok.value = t["lexeme"]
            tok.lineno = 1
            tok.lexpos = self.index - 1
            return tok
        else:
            print("[DEBUG] No more tokens.")
            return None

parser = yacc.yacc(write_tables=False, debug=True)

def parse_tokens(lex_output):
    print("[DEBUG] parse_tokens called with:")
    for t in lex_output:
        print(f"  {t}")
    lexer = ListLexer(lex_output)
    error_msg = None
    def custom_error(p):
        nonlocal error_msg
        if p:
            error_msg = f"Syntax error at '{p.value}' (type: {getattr(p, 'type', None)})"
        else:
            error_msg = "Syntax error at EOF"
        print(error_msg)
    parser.errorfunc = custom_error
    result = parser.parse(lexer=lexer)
    print("[DEBUG] Parse result:", result)
    return result, error_msg


# test
if __name__ == "__main__":
    from lexer import lexer
    user_input = "3 + a * (9 + b)"
    lex_out = lexer(user_input)
    tree = parse_tokens(lex_out)
    print(tree)