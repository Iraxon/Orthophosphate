import dataclasses
import typing

from .abstract_syntax_tree import *
from ..tokenizer.token import Token, TokenType

type Parser[T] = typing.Callable[[ParseState], T]

@dataclasses.dataclass
class ParseState:
    tokens: typing.Sequence[Token]
    cursor: int = 0
    function_bindings: dict[ColonIdentifier, MCFunction] = dataclasses.field(default_factory=dict)
    scope: list[str] = dataclasses.field(default_factory=list)

    def grab(self) -> Token:
        r_val = self.tokens[self.cursor]
        self.skip()
        return r_val

    def skip(self) -> None:
        self.cursor += 1

    def peek(self, i: int = 0) -> Token:
        return self.tokens[self.cursor + i]

    def in_range(self) -> bool:
        return 0 <= self.cursor < len(self.tokens)

    def display_token(self, n: int = 0) -> str:
        return str(self.peek(n)) if (self.cursor + n >= 0 and self.cursor + n < len(self.tokens)) else ''

    def error_readout(self, i: int = -1) -> str:
        return f"".join(tuple(f"\t{self.display_token(n)}{' <<< HERE' if n == i else ''}\n" for n in range(-20, 10)))

    def scope_in(self, next: str) -> None:
        self.scope.append(next)

    def scope_out(self) -> None:
        self.scope.pop()

    def bind_function(self, name: ColonIdentifier, fn: MCFunction) -> MCFunction:
        if (name in self.function_bindings):
            err(self, f"Function {name} already exists:")
        self.function_bindings[name] = fn
        return fn

    def checkref_function(self, name: ColonIdentifier) -> Ref[MCFunction]:
        return Ref(self.deref_function(name))

    def deref_function(self, name: ColonIdentifier) -> MCFunction:
        fn = self.function_bindings.get(name)
        if fn is None:
            err(self, "Unknown function:")
        return fn

def parse_top_level(state: ParseState) -> TextFile:
    t = state.grab()
    match t:
        case (TokenType.NAME, "function"):
            name = ColonIdentifier.of(state.grab().require_name().value)
            body = parse_block(state)
            return state.bind_function(name, MCFunction(name, body))
        case (TokenType.NAME, "tag"):
            type = state.grab().require_name().value
            name = ColonIdentifier.of(state.grab().require_name().value)
            match type:
                case "function":
                    return Tag[MCFunction](name, parse_tag_list(state))
                case _:
                    err(state, "Not a supported tag type:")
        case _:
            err(state)

def parse_block(state: ParseState) -> Block:
    if (state.peek() == Token(TokenType.PUNC, "{")):
        state.grab()
        body = _resolve_node_tuple(state, Token(TokenType.PUNC, "}"), parse_cmd)
        return Block(body)
    return Block((parse_cmd(state),))

def parse_cmd(state: ParseState) -> CMD:
    t = state.grab()
    match t:
        case (TokenType.LITERAL, cmd):
            if state.grab() != (TokenType.PUNC, ";"):
                err(state, "Missing semicolon:")
            return LiteralCMD(value=cmd)
        case (TokenType.NAME, "obj"):
            obj_name = state.grab().require_name()
            return LiteralCMD("   PLACEHOLDER   obj")
        case (TokenType.NAME, "score"):
            operand1 = parse_score(state, prohibit_const=True)
            operation = ScoreboardOperator.of(state.grab().require(TokenType.OP).value)
            operand2 = parse_score(state)
            return ScoreboardOperation(operand1, operand2, operation)
        case (TokenType.NAME, "while"):
            raise NotImplementedError
        case (TokenType.NAME, "call"):
            function_id = state.grab().require_name()
            raise NotImplementedError
        case _:
            err(state)

def parse_score(state: ParseState, prohibit_const: bool = False) -> Score:
    score = (state.grab(), state.grab())
    match score:
        case ((TokenType.NAME, "constant"), (TokenType.INT, x)):
            if prohibit_const:
                err(state, "A constant score is not allowed here:")
            return ConstantScore(int(x))
        case ((TokenType.NAME, n), (TokenType.NAME, obj)):
            return VariableScore(n, OBJ(obj))
        case ((TokenType.SELECTOR, s), (TokenType.NAME, obj)):
            return VariableScore(TargetSelector.of(s), OBJ(obj))
        case _:
            err(state)

def parse_tag_list(state: ParseState) -> tuple[Ref[MCFunction], ...]:
    vals: tuple[ColonIdentifier, ...]
    if (state.peek() == Token(TokenType.PUNC, "{")):
        state.grab()
        body = _resolve_node_tuple(state, Token(TokenType.PUNC, "}"), parse_colon_id)
        vals = body
    else:
        vals = (parse_colon_id(state),)
    return tuple(state.checkref_function(v) for v in vals)

def parse_colon_id(state: ParseState) -> ColonIdentifier:
    t = state.grab()
    match t:
        case (TokenType.NAME, n):
            return ColonIdentifier.of(n)
        case _:
            err(state)

def parse(tokens: tuple[Token, ...]) -> Root:
    """
    Accepts a tuple of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified

    This function is recursive, both itself and
    mutually with _resolve_node_tuple and _resolve_finite_tuple;
    it uses the private cursor parameter
    in the recursion calls; that parameter should not be set
    by outsider callers
    """
    state = ParseState(tokens)
    assert state.grab() == Token(TokenType.PUNC, "file_start")
    return Root(
        value=_resolve_node_tuple(
            state,
            Token(TokenType.PUNC, "EOF"),
            parse_top_level
        )
    )

def _resolve_node_tuple[T](state: ParseState, end_token: Token, parse_function: Parser[T]) -> tuple[T, ...]:
    """
    Makes a flat tuple of nodes from the tokens
    until it hits the specfied end token or EOF
    """
    node_list: list[T] = []

    # While not out of file and it is not the case
    # that the current token matches end_token

    while state.in_range():

        # Check for end tokens
        next_token = state.peek()
        if next_token.type == end_token.type and (next_token.value == end_token.value or end_token.value == "*"):
            state.skip() # Skip closing token
            break

        next_node = parse_function(state)
        if next_node is not None:
            node_list.append(next_node)
    return tuple(node_list)

def err(state: ParseState, message: str | None = None) -> typing.Never:
    raise ValueError(f"{f'Invalid token {state.peek(-1)} at:' if message is None else message}\n{state.error_readout()}")

if __name__ == "__main__":
    pass
    # It is prefered that tests be run from compiler.py,
    # because that module can import token and other
    # modules that are cousins to parser.py
