from enum import Enum

class Token:
    """Token for AST"""
    def __init__(self, token_text: str, token_type):
        self.name = token_type
        self.value = token_text


class TokenType(Enum):
    """Token's types"""
    # specials
    COLON = 0
    EOF = 1
    LBRACE = 2
    MINUS = 3
    NWLINE = 4
    RBRACE = 5
    # reserved
    ENDUML = 101
    IDENTIFYIER = 102
    MODIFYER = 103
    RELATION = 104
    STARTUML = 105
    SPLITTER = 106
    STRING = 107
    STEREOTYPE = 108
    # keywords
    ENTITY = 200
    TITLE = 201
