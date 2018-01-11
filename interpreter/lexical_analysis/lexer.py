""" SCI - Simple C Interpreter """

from .token_type import *
from .token import Token

# maps strings that have a special meaning to corresponding tokens
RESERVED_KEYWORDS = {
    'char': Token(CHAR, 'char'),
    'int': Token(INT, 'int'),
    'float': Token(FLOAT, 'float'),
    'double': Token(DOUBLE, 'double'),
    'long': Token(LONG, 'long'),
    'short': Token(SHORT, 'short'),
    'signed': Token(SIGNED, 'signed'),
    'unsigned': Token(UNSIGNED, 'unsigned'),
    'if': Token(IF, 'if'),
    'else': Token(ELSE, 'else'),
    'for': Token(FOR, 'for'),
    'while': Token(WHILE, 'while'),
    'do': Token(DO, 'do'),
    'return': Token(RETURN, 'return'),
    'break': Token(BREAK, 'break'),
    'continue': Token(CONTINUE, 'continue'),
    'switch': Token(SWITCH, 'switch'),
    'case': Token(CASE, 'case'),
    'default': Token(DEFAULT, 'default'),
}

class LexicalError(Exception):
    pass

class Lexer(object):
    def __init__(self, text):
        """
        Initializes the lexer.

        text: the source code to be lexically analyzed
        pos: the current lexer position
        current_char: the character at the current lexer position
        line: the current line number
        """
        self.text = text.replace('\\n', '\n')
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.line = 1

    def error(self, message):
        """ Raises a lexical error. """
        raise LexicalError("LexicalError: " + message)

    def advance(self, n = 1):
        """ Advances the `pos` pointer and sets the `current_char` variable. """
        self.pos += n
        if self.pos >= len(self.text):
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def peek(self, n):
        """ Returns the n-th char from the current positions but don't change state. """
        peek_pos = self.pos + n
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        """ Skips all whitespace starting from the current position. """
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
            self.advance()

    def skip_comment(self):
        """ Skips a single line comment starting at the current position. """
        self.advance(2)
        while self.current_char is not None:
            if self.current_char == '\n':
                self.line += 1
                self.advance()
                return
            self.advance()

    def skip_multiline_comment(self):
        """ Skip a multi line comment starting at the current position. """
        self.advance(2)
        while self.current_char is not None:
            if self.current_char == '*' and self.peek(1) == '/':
                self.advance(2)
                return
            if self.current_char == '\n':
                self.line += 1
            self.advance()
        self.error("Unterminated comment at line {}".format(self.line))

    def number(self):
        """Handles an integer or a real number."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

            token = Token(REAL_CONST, float(result))
        else:
            token = Token(INTEGER_CONST, int(result))

        return token

    def string(self):
        """ Handles a string literal. """
        result = ''
        self.advance()
        while self.current_char is not '"':
            if self.current_char is None:
                self.error(
                    message='Unterminated string literal at line {}'.format(self.line)
                )
            result += self.current_char
            self.advance()
        self.advance()
        return Token(STRING, result)

    def char(self):
        """ Handles a character literal. """
        self.advance()
        ch = self.current_char
        self.advance()
        if self.current_char != '\'':
            self.error("Unterminated char literal at line {}".format(self.line))
        self.advance()
        return Token(CHAR_CONST, ord(ch))

    def _id(self):
        """ Handles identifiers and reserved keywords. """
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        # Return a reserved keyword token or an id token.
        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    @property
    def get_next_token(self):
        """ The main lexer method that returns the next token in the text. """

        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and self.peek(1) == '/':
                self.skip_comment()
                continue

            if self.current_char == '/' and self.peek(1) == '*':
                self.skip_multiline_comment()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '"':
                return self.string()

            if self.current_char == '\'':
                return self.char()

            # three-char tokens

            if self.current_char == '<' and self.peek(1) == '<' and self.peek(2) == '=':
                self.advance(3)
                return Token(LEFT_ASSIGN, '<<=')

            if self.current_char == '>' and self.peek(1) == '>' and self.peek(2) == '=':
                self.advance(3)
                return Token(RIGHT_ASSIGN, '>>=')

            # two-char tokens

            if self.current_char == '+' and self.peek(1) == '=':
                self.advance(2)
                return Token(ADD_ASSIGN, '+=')

            if self.current_char == '-' and self.peek(1) == '=':
                self.advance(2)
                return Token(SUB_ASSIGN, '-=')

            if self.current_char == '*' and self.peek(1) == '=':
                self.advance(2)
                return Token(MUL_ASSIGN, '*=')

            if self.current_char == '/' and self.peek(1) == '=':
                self.advance()
                self.advance()
                return Token(DIV_ASSIGN, '/=')

            if self.current_char == '%' and self.peek(1) == '=':
                self.advance(2)
                return Token(MOD_ASSIGN, '%=')

            if self.current_char == '&' and self.peek(1) == '=':
                self.advance(2)
                return Token(AND_ASSIGN, '&=')

            if self.current_char == '^' and self.peek(1) == '=':
                self.advance(2)
                return Token(XOR_ASSIGN, '^=')

            if self.current_char == '|' and self.peek(1) == '=':
                self.advance(2)
                return Token(OR_ASSIGN, '|=')

            if self.current_char == '>' and self.peek(1) == '>':
                self.advance(2)
                return Token(RIGHT_OP, '>>')

            if self.current_char == '<' and self.peek(1) == '<':
                self.advance(2)
                return Token(LEFT_OP, '<<')

            if self.current_char == '+' and self.peek(1) == '+':
                self.advance(2)
                return Token(INC_OP, '++')

            if self.current_char == '-' and self.peek(1) == '-':
                self.advance(2)
                return Token(DEC_OP, '--')

            if self.current_char == '&' and self.peek(1) == '&':
                self.advance(2)
                return Token(LOG_AND_OP, '&&')

            if self.current_char == '|' and self.peek(1) == '|':
                self.advance(2)
                return Token(LOG_OR_OP, '||')

            if self.current_char == '<' and self.peek(1) == '=':
                self.advance(2)
                return Token(LE_OP, '<=')

            if self.current_char == '>' and self.peek(1) == '=':
                self.advance(2)
                return Token(GE_OP, '>=')

            if self.current_char == '=' and self.peek(1) == '=':
                self.advance(2)
                return Token(EQ_OP, '==')

            if self.current_char == '!' and self.peek(1) == '=':
                self.advance(2)
                return Token(NE_OP, '!=')

            # one-char tokens

            if self.current_char == '<':
                self.advance()
                return Token(LT_OP, '<')

            if self.current_char == '>':
                self.advance()
                return Token(GT_OP, '>')

            if self.current_char == '=':
                self.advance()
                return Token(ASSIGN, '=')

            if self.current_char == '!':
                self.advance()
                return Token(LOG_NEG, '!')

            if self.current_char == '&':
                self.advance()
                return Token(AMPERSAND, '&')

            if self.current_char == '|':
                self.advance()
                return Token(OR_OP, '|')

            if self.current_char == '^':
                self.advance()
                return Token(XOR_OP, '|')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(ASTERISK, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV_OP, '/')

            if self.current_char == '%':
                self.advance()
                return Token(MOD_OP, '%')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '{':
                self.advance()
                return Token(LBRACKET, '{')

            if self.current_char == '}':
                self.advance()
                return Token(RBRACKET, '}')

            if self.current_char == ';':
                self.advance()
                return Token(SEMICOLON, ';')

            if self.current_char == ':':
                self.advance()
                return Token(COLON, ':')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')

            if self.current_char == '#':
                self.advance()
                return Token(HASH, '#')

            if self.current_char == '?':
                self.advance()
                return Token(QUESTION_MARK, '?')

            self.error(
                message="Invalid char {} at line {}".format(self.current_char, self.line)
            )

        return Token(EOF, None)
