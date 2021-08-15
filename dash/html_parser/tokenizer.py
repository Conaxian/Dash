from typing import Iterator
from html_parser.constants import *
from html_parser.tokens import *

# https://www.w3.org/TR/html53/syntax.html#tokenization

class Tokenizer:
    """
    Represents a single tokenizable HTML text.
    """
    def __init__(self, html: str) -> None:
        self.html = html

    def reset(self) -> None:
        """
        Resets the tokenizer state.
        """
        self.state = "DATA"
        self.temp: Token = None
        self.pos = -1
        self.last_start_tag: Token = Token.null()
        self.next()

    def next(self) -> str:
        """
        Advances the position by 1 character.
        """
        self.pos += 1
        try:
            self.char = self.html[self.pos]
        except IndexError:
            self.char = EOF
        return self.char

    def lookahead(self, count: int=1) -> str:
        """
        Looks ahead for the next `count` characters.
        """
        return self.html[self.pos:self.pos + count]

    def temp_clear(self) -> Token:
        """
        Clears the temporary token and returns it.
        """
        temp = self.temp
        self.temp = None
        return temp

    def correct_end_tag(self) -> bool:
        """
        Returns a boolean indicating whether the temporary end tag
        name and the last start tag name match.
        """
        return self.temp.name == self.last_start_tag.name

    def tokenize(self) -> Iterator[Token]:
        """
        Tokenizes the HTML and returns a list of tokens.
        """
        self.reset()
        while self.pos <= len(self.html):
            state_func = self.state.lower() + "_state"
            tokens: Token = getattr(self, state_func)()
            if isinstance(tokens, tuple):
                for token in tokens:
                    if isinstance(token, StartTag):
                        self.last_start_tag = token
                    yield token
                    if token.new_state: self.state = token.new_state
            elif tokens:
                if isinstance(tokens, StartTag):
                    self.last_start_tag = tokens
                yield tokens
                if tokens.new_state: self.state = tokens.new_state
            self.next()

    def data_state(self):
        if self.char == "&":
            self.return_state = "DATA"
            self.state = "CHAR_REF"
        elif self.char == "<":
            self.state = "TAG_OPEN"
        elif self.char == NULL:
            # Parse Error
            return Character(self.char)
        elif self.char == EOF:
            return Eof()
        else:
            return Character(self.char)

    def rcdata_state(self):
        if self.char == "&":
            self.return_state = "RCDATA"
            self.state = "CHAR_REF"
        elif self.char == "<":
            self.state = "RCDATA_LESSTHAN"
        elif self.char == NULL:
            # Parse Error
            return Character(self.char)
        elif self.char == EOF:
            return Eof()
        else:
            return Character(self.char)

    def tag_open_state(self):
        if self.char == "!":
            self.state = "MARKUP_OPEN"
        elif self.char == "/":
            self.state = "END_TAG_OPEN"
        elif self.char in ASCII_LETTERS:
            self.temp = StartTag()
            self.state = "TAG_NAME"
            self.pos -= 1
        elif self.char == "?":
            # Parse Error
            self.temp = Comment()
            self.state = "BOGUS_COMMENT"
            self.pos -= 1
        else:
            # Parse Error
            self.state = "DATA"
            self.pos -= 1
            return Character("<")

    def end_tag_open_state(self):
        if self.char in ASCII_LETTERS:
            self.temp = EndTag()
            self.state = "TAG_NAME"
            self.pos -= 1
        elif self.char == ">":
            # Parse Error
            self.state = "DATA"
        elif self.char == EOF:
            # Parse Error
            return (Character("<"), Character("/"), Eof())
        else:
            # Parse Error
            self.temp = Comment()
            self.state = "BOGUS_COMMENT"
            self.pos -= 1

    def tag_name_state(self):
        if self.char in SPACE:
            self.state = "PRE_ATTR_NAME"
        elif self.char == "/":
            self.state = "SELFCLOSING_TAG"
        elif self.char == ">":
            self.state = "DATA"
            return self.temp_clear()
        elif self.char in ASCII_LETTERS_UPPER:
            self.temp.name += self.char.lower()
        elif self.char == NULL:
            # Parse Error
            self.temp.name += REPLACEMENT_CHAR
        elif self.char == EOF:
            # Parse Error
            return Eof()
        else:
            self.temp.name += self.char

    def rcdata_lessthan_state(self):
        if self.char == "/":
            self.temp_string = ""
            self.state = "RCDATA_END_TAG_OPEN"
        else:
            self.state = "RCDATA"
            self.pos -= 1
            return Character("<")

    def rcdata_end_tag_open_state(self):
        if self.char in ASCII_LETTERS:
            self.temp = EndTag()
            self.state = "RCDATA_END_TAG_NAME"
            self.pos -= 1
        else:
            self.state = "RCDATA"
            self.pos -= 1
            return (Character("<"), Character("/"))

    def rcdata_end_tag_name_state(self):
        if self.char in SPACE and self.correct_end_tag():
            self.state = "PRE_ATTR_NAME"
        elif self.char == "/" and self.correct_end_tag():
            self.state = "SELFCLOSING_TAG"
        elif self.char == ">" and self.correct_end_tag():
            self.state = "DATA"
            return self.temp_clear()
        elif self.char in ASCII_LETTERS_UPPER:
            self.temp.name += self.char.lower()
            self.temp_string += self.char
        elif self.char in ASCII_LETTERS_LOWER:
            self.temp.name += self.char
            self.temp_string += self.char
        else:
            chars = [Character("<"), Character("/")]
            for char in self.temp_string:
                chars.append(Character(char))
            self.state = "RCDATA"
            self.pos -= 1
            return (*chars,)

    def selfclosing_tag_state(self):
        if self.char == ">":
            self.temp.save_attr()
            self.temp.self_closing = True
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == EOF:
            # Parse Error
            return Eof()
        else:
            # Parse Error
            self.state = "PRE_ATTR_NAME"
            self.pos -= 1

    def pre_attr_name_state(self):
        while self.char in SPACE:
            self.next()
        if self.char in ("/", ">", EOF):
            self.state = "POST_ATTR_NAME"
            self.pos -= 1
        elif self.char == "=":
            # Parse Error
            self.temp.new_attr(self.char, "")
            self.state = "ATTR_NAME"
        else:
            self.temp.new_attr("", "")
            self.state = "ATTR_NAME"
            self.pos -= 1

    def attr_name_state(self):
        if self.char in SPACE or self.char in ("/", ">", EOF):
            if self.temp.temp_attr[0] in self.temp.attrs:
                # Parse Error
                self.temp.temp_attr_invalid = True
            self.state = "POST_ATTR_NAME"
            self.pos -= 1
        elif self.char == "=":
            if self.temp.temp_attr[0] in self.temp.attrs:
                # Parse Error
                self.temp.temp_attr_invalid = True
            self.state = "PRE_ATTR_VALUE"
        elif self.char in ASCII_LETTERS_UPPER:
            self.temp.temp_attr[0] += self.char.lower()
        elif self.char == NULL:
            # Parse Error
            self.temp.temp_attr[0] += REPLACEMENT_CHAR
        elif self.char in QUOTES + "<":
            # Parse Error
            self.temp.temp_attr[0] += self.char
        else:
            self.temp.temp_attr[0] += self.char

    def post_attr_name_state(self):
        while self.char in SPACE:
            self.next()
        if self.char == "/":
            self.state = "SELFCLOSING_TAG"
        elif self.char == "=":
            self.state = "PRE_ATTR_VALUE"
        elif self.char == ">":
            self.temp.save_attr()
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == EOF:
            # Parse Error
            return Eof()
        else:
            self.temp.new_attr("", "")
            self.state = "ATTR_NAME"
            self.pos -= 1

    def pre_attr_value_state(self):
        while self.char in SPACE:
            self.next()
        if self.char in '"':
            self.state = "ATTR_VALUE_DQUOTED"
        elif self.char in "'":
            self.state = "ATTR_VALUE_SQUOTED"
        elif self.char in ">":
            # Parse Error
            self.state = "ATTR_VALUE_UNQUOTED"
            self.pos -= 1
        else:
            self.state = "ATTR_VALUE_UNQUOTED"
            self.pos -= 1

    def attr_value_dquoted_state(self):
        if self.char == '"':
            self.state = "POST_ATTR_VALUE_QUOTED"
        elif self.char == "&":
            self.return_state = "ATTR_VALUE_DQUOTED"
            self.state = "CHAR_REF"
        elif self.char == NULL:
            # Parse Error
            self.temp.temp_attr[1] += REPLACEMENT_CHAR
        elif self.char == EOF:
            # Parse Error
            return Eof()
        else:
            self.temp.temp_attr[1] += self.char

    def attr_value_squoted_state(self):
        if self.char == "'":
            self.state = "POST_ATTR_VALUE_QUOTED"
        elif self.char == "&":
            self.return_state = "ATTR_VALUE_SQUOTED"
            self.state = "CHAR_REF"
        elif self.char == NULL:
            # Parse Error
            self.temp.temp_attr[1] += REPLACEMENT_CHAR
        elif self.char == EOF:
            # Parse Error
            return Eof()
        else:
            self.temp.temp_attr[1] += self.char

    def attr_value_unquoted_state(self):
        if self.char in SPACE:
            self.state = "PRE_ATTR_NAME"
        elif self.char == "&":
            self.return_state = "ATTR_VALUE_UNQUOTED"
            self.state = "CHAR_REF"
        elif self.char == ">":
            self.temp.save_attr()
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == NULL:
            # Parse Error
            self.temp.temp_attr[1] += REPLACEMENT_CHAR
        elif self.char in QUOTES + "<=`":
            # Parse Error
            self.temp.temp_attr[1] += self.char
        elif self.char == EOF:
            # Parse Error
            return Eof()
        else:
            self.temp.temp_attr[1] += self.char

    def post_attr_value_quoted_state(self):
        if self.char in SPACE:
            self.state = "PRE_ATTR_NAME"
        elif self.char == "/":
            self.state = "SELFCLOSING_TAG"
        elif self.char == ">":
            self.temp.save_attr()
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == EOF:
            # Parse Error
            return Eof()
        else:
            # Parse Error
            self.state = "PRE_ATTR_NAME"
            self.pos -= 1

    def markup_open_state(self):
        if self.lookahead(2) == "--":
            self.pos += 1
            self.temp = Comment()
            self.state = "COMMENT_START"
        elif self.lookahead(7).upper() == "DOCTYPE":
            self.pos += 6
            self.state = "DOCTYPE"
        elif self.lookahead(7) == "[CDATA[":
            self.pos += 6
            self.state = "CDATA"
        else:
            # Parse Error
            self.temp = Comment()
            self.state = "BOGUS_COMMENT"
            self.pos -= 1

    def comment_start_state(self):
        if self.char == "-":
            self.state = "COMMENT_START_DASH"
        elif self.char == ">":
            # Parse Error
            self.state = "DATA"
            return self.temp_clear()
        else:
            self.state = "COMMENT"
            self.pos -= 1

    def comment_start_dash_state(self):
        if self.char == "-":
            self.state = "COMMENT_END"
        elif self.char == ">":
            # Parse Error
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == EOF:
            # Parse Error
            return (self.temp, Eof())
        else:
            self.temp.data += "-"
            self.state = "COMMENT"
            self.pos -= 1

    def comment_state(self):
        if self.char == "<":
            self.temp.data += "<"
            self.state = "COMMENT_LESSTHAN"
        elif self.char == "-":
            self.state = "COMMENT_END_DASH"
        elif self.char == NULL:
            # Parse Error
            self.temp.data += REPLACEMENT_CHAR
        elif self.char == EOF:
            # Parse Error
            return (self.temp, Eof())
        else:
            self.temp.data += self.char

    def comment_lessthan_state(self):
        if self.char == "!":
            self.temp.data += "!"
            self.state = "COMMENT_LESSTHAN_BANG"
        elif self.char == "<":
            self.temp.data += "<"
        else:
            self.state = "COMMENT"
            self.pos -= 1

    def comment_lessthan_bang_state(self):
        if self.char == "-":
            self.state = "COMMENT_LESSTHAN_BANG_DASH"
        else:
            self.state = "COMMENT"
            self.pos -= 1

    def comment_lessthan_bang_dash_state(self):
        if self.char == "-":
            self.state = "COMMENT_LESSTHAN_BANG_DDASH"
        else:
            self.state = "COMMENT_END_DASH"
            self.pos -= 1

    def comment_lessthan_bang_ddash_state(self):
        if self.char in (">", EOF):
            self.state = "COMMENT_END"
            self.pos -= 1
        else:
            # Parse Error
            self.state = "COMMENT_END"
            self.pos -= 1

    def comment_end_dash_state(self):
        if self.char == "-":
            self.state = "COMMENT_END"
        elif self.char == EOF:
            # Parse Error
            return (self.temp, Eof())
        else:
            self.temp.data += "-"
            self.state = "COMMENT"
            self.pos -= 1

    def comment_end_state(self):
        if self.char == ">":
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == "!":
            self.state = "COMMENT_END_BANG"
        elif self.char == "-":
            self.temp.data += "-"
        elif self.char == EOF:
            # Parse Error
            return (self.temp, Eof())
        else:
            self.temp.data += "--"
            self.state = "COMMENT"
            self.pos -= 1

    def comment_end_bang_state(self):
        if self.char == "-":
            self.temp.data += "--!"
            self.state = "COMMENT_END_DASH"
        elif self.char == ">":
            # Parse Error
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == EOF:
            # Parse Error
            return (self.temp, Eof())
        else:
            self.temp.data += "--!"
            self.state = "COMMENT"
            self.pos -= 1

    def doctype_state(self):
        if self.char in SPACE:
            self.state = "PRE_DOCTYPE_NAME"
        elif self.char == EOF:
            # Parse Error
            doctype = Doctype(force_quirks=True)
            return (doctype, Eof())
        else:
            # Parse Error
            self.state = "PRE_DOCTYPE_NAME"
            self.pos -= 1

    def pre_doctype_name_state(self):
        while self.char in SPACE:
            self.next()
        if self.char in ASCII_LETTERS_UPPER:
            self.temp = Doctype(self.char.lower())
            self.state = "DOCTYPE_NAME"
        elif self.char == NULL:
            # Parse Error
            self.temp = Doctype(REPLACEMENT_CHAR)
            self.state = "DOCTYPE_NAME"
        elif self.char == ">":
            # Parse Error
            doctype = Doctype(force_quirks=True)
            self.state = "DATA"
            return doctype
        elif self.char == EOF:
            # Parse Error
            doctype = Doctype(force_quirks=True)
            return (doctype, Eof())
        else:
            self.temp = Doctype(self.char)
            self.state = "DOCTYPE_NAME"

    def doctype_name_state(self):
        if self.char in SPACE:
            self.state = "POST_DOCTYPE_NAME"
        elif self.char == ">":
            self.state = "DATA"
            return self.temp_clear()
        elif self.char in ASCII_LETTERS_UPPER:
            self.temp.name += self.char.lower()
        elif self.char == NULL:
            # Parse Error
            self.temp.name += REPLACEMENT_CHAR
        elif self.char == EOF:
            # Parse Error
            self.temp.force_quirks = True
            return (self.temp, Eof())
        else:
            self.temp.name += self.char

    def post_doctype_name_state(self):
        while self.char in SPACE:
            self.next()
        if self.char == ">":
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == EOF:
            # Parse Error
            self.temp.force_quirks = True
            return (self.temp, Eof())
        else:
            if self.lookahead(6).upper() == "PUBLIC":
                self.pos += 5
                self.state = "POST_DOCTYPE_PUBLIC"
            elif self.lookahead(6).upper() == "SYSTEM":
                self.pos += 5
                self.state = "POST_DOCTYPE_SYSTEM"
            else:
                # Parse Error
                self.temp.force_quirks = True
                self.state = "BOGUS_DOCTYPE"

    def bogus_doctype_state(self):
        while self.char not in (">", EOF):
            self.next()
        if self.char == ">":
            self.state = "DATA"
            return self.temp_clear()
        else:
            return (self.temp, Eof())

    def bogus_comment_state(self):
        if self.char == ">":
            self.state = "DATA"
            return self.temp_clear()
        elif self.char == EOF:
            return (self.temp, Eof())
        elif self.char == NULL:
            self.temp.data += REPLACEMENT_CHAR
        else:
            self.temp.data += self.char
