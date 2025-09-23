# lexer.py

# Import the official token names from the shared module.
from token_def import TOKEN_ID, TOKEN_PLUS, TOKEN_MUL, TOKEN_MINUS, TOKEN_DIV, TOKEN_LPAREN, TOKEN_RPAREN


def lexer(input_string):
    """
    Simulates a lexical analyzer by converting an input string into a list of tokens.
    """
    tokens = []
    current_position = 0

    while current_position < len(input_string):
        char = input_string[current_position]

        # Skip whitespace characters (like spaces and tabs).
        if char.isspace():
            current_position += 1
            continue
        
        # Check for identifiers (digits 0-9 and letters a-z, A-Z).
        if char.isdigit() or char.isalpha():
            lexeme = char
            tokens.append({"lexeme": lexeme, "token": TOKEN_ID})
            current_position += 1
            continue

        # Check for operators and parentheses.
        if char == '+':
            tokens.append({"lexeme": "+", "token": TOKEN_PLUS})
            current_position += 1
            continue
        if char == '*':
            tokens.append({"lexeme": "*", "token": TOKEN_MUL})
            current_position += 1
            continue
        if char == '-':
            tokens.append({"lexeme": "-", "token": TOKEN_MINUS})
            current_position += 1
            continue
        if char == '/':
            tokens.append({"lexeme": "/", "token": TOKEN_DIV})
            current_position += 1
            continue
        if char == '(':
            tokens.append({"lexeme": "(", "token": TOKEN_LPAREN})
            current_position += 1
            continue
        if char == ')':
            tokens.append({"lexeme": ")", "token": TOKEN_RPAREN})
            current_position += 1
            continue

        # If a character doesn't match any of the above, it's an error.
        raise ValueError(f"Invalid character '{char}' at position {current_position}")

    return tokens

# You can add a simple test case here to run the function directly.
if __name__ == '__main__':
    test_string = "3 + a * (9 - b)"
    try:
        token_list = lexer(test_string)
        print("Input String:", test_string)
        print("Tokens:", token_list)
    except ValueError as e:
        print(f"Lexical error: {e}")
