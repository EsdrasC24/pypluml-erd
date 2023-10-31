import re
from typing import Union

from pypluml_erd.notifier import Notifier
from pypluml_erd.token import Token, TokenType

class Lexer(Notifier):
    """Lexical analyzer"""
    def __init__(self, content:  str) -> None:
        self.source = content + '\n'
        self.cur_pos = -1
        self.cur_char = ''
        self.next_char()

    def abort(self, msg: str) -> None:
        """Stops operations"""
        self.fatal_error('Error!. ' + msg)

    def get_token(self) -> Union[None, Token]:
        """Gets token from character"""
        self.skip_whitespace()
        self.skip_comments_and_directives()
        token = None

        char = self.cur_char

        if char == '\0':
            token = Token(char, TokenType.EOF)

        elif char == '\n':
            token = Token(char, TokenType.NWLINE)

        elif char == ':':
            token = Token(char, TokenType.COLON)

        elif char == '@':
            first_pos = self.cur_pos
            while self.peek().isalpha():
                self.next_char()

            string = self.source[first_pos : self.cur_pos + 1]
            if string == '@startuml':
                token = Token(string, TokenType.STARTUML)
            elif string == '@enduml':
                token = Token(string, TokenType.ENDUML)
            else:
                self.abort('Directiva desconocida: '+ string)
        
        elif char == '-':
            if self.peek() == '-':
                first_pos = self.cur_pos
                while self.cur_char == '-':
                    self.next_char()
                token = Token(self.source[first_pos : self.cur_pos], TokenType.SPLITTER)
            else:
                token = Token(char, TokenType.MINUS)

        elif char == '"':
            first_pos = self.cur_pos
            self.next_char()
            while self.cur_char != '"':
               if self.peek() == '\0':
                   self.abort('Falta especificar comillas <"> de cierre')
               self.next_char()

            token = Token(self.source[first_pos : self.cur_pos + 1], TokenType.STRING)
    
        elif char == '{':
            token = Token(char, TokenType.RBRACE)

        elif char in ['}', '|']:
            if self.peek() in [' ', '\t', '\r', '\n', '\0']:
                if char == '}':
                    token = Token(char, TokenType.LBRACE)
                else:
                    self.abort('Se espera que los carácteres siguientes a | definan un relacion')
            else:
                first_pos = self.cur_pos
                while self.peek() not in [' ', '\t', '\r', '\n', '\0']:
                    self.next_char()

                string = self.source[first_pos : self.cur_pos + 1]
                if re.search(r'(\}|\|)(o|\|)-(right|left|down|up)?-(o|\|)(\||\{)', string):
                    token = Token(string, TokenType.RELATION)
                else:
                    self.abort('Desconocido tipo de relacion: '+string)

        elif char == '<':
            first_pos = self.cur_pos
            while self.cur_char != '>':
                if self.cur_char == '\0':
                    self.abort('Falta caracteres: >> para cerrar definición de estereotipo')
                self.next_char()
            self.next_char() # for have double >>

            string = self.source[first_pos  : self.cur_pos + 1]

            if string[:2] != '<<':
                self.abort('Falta carácter: <  para definicion de estereotipo en ' + string)
            if string[-2:] != '>>':
                self.abort('Falta carácter: >  para definicion de estereotipo en ' + string)

            token = Token(string, TokenType.STEREOTYPE)

        elif char == "[":
            current = self.cur_pos
            while self.cur_char != ']':
                if self.cur_char == '\0' or self.cur_char == '\n':
                    self.abort('Falta caracter: ] para cerrar definición de estereotipo')
                self.next_char()

            string = self.source[current  : self.cur_pos + 1]
            token = Token(string, TokenType.MODIFYER)

        elif char.isalnum() or char == '_':
            first_pos = self.cur_pos
            while self.peek().isalnum() or self.peek() == '_':
                self.next_char()

            string = self.source[first_pos : self.cur_pos + 1]
            if Lexer.is_keyword(string.upper()):
                token = Token(string, TokenType[string.upper()])
            else:
                token = Token(string, TokenType.IDENTIFYIER)
        else:
            self.abort('Desconocido carárter para tokenización: ' + char)
        
        self.next_char()
        return token

    def peek(self) -> str:
        """Devuelve el proximo caracter a tokenizar"""
        pos = self.cur_pos + 1
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]

    def next_char(self)-> None:
        """Mueve el cursor hacia el proximo carácter a tokenizar"""
        self.cur_pos += 1
        if self.cur_pos >= len(self.source):
            self.cur_char = '\0'
        else:
            self.cur_char = self.source[self.cur_pos]

    def skip_comments_and_directives(self) -> None:
        """Omite los comentarios y directivas (no relevantes) dentro del contenido a tokenizar"""
        if self.cur_char == "'" or self.cur_char == '!':
            while self.cur_char != '\n':
                self.next_char()

    def skip_whitespace(self) -> None:
        """Omite los espacios en blanco dentro del contenido a tokenizar"""
        while self.cur_char in [' ', '\t', '\r']:
            self.next_char()

    @staticmethod
    def is_keyword(word: str) -> bool:
        """Verifica si la cadena pasada como parámetro es un palabra reservada"""
        kinds = [x.name for x in TokenType if x.value >= 200 and x.value < 300]
        return word in kinds
