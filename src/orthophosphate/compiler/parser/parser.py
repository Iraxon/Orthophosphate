import typing

from .abstract_syntax_tree import *
from .parse_state import ParseState, err
from ..tokenizer.token import Token, TokenType

def parse(tokens: tuple[Token, ...]) -> PackRoot:
    """
    Accepts a tuple of tokens from the tokenizer

    Returns the root node of an abstract syntax tree
    representing the program specified

    This method is the entry point for this module
    """
    state = ParseState(tokens)
    assert state.next_token() == Token(TokenType.PUNC, "file_start")
    return PackRoot(
        files=_resolve_node_tuple(
            state,
            Token(TokenType.PUNC, "EOF"),
            _parse_top_level
        )
    )

type Parser[T] = typing.Callable[[ParseState], T]

"""
All of the pares_* methods below take the current ParseState
and return the AST object that the tokens at the cursor represent.

Parse methods can mutate the state
of the passed ParseState object. They call other parse
methods according to what elements of the language
should appear next.
"""

def _parse_top_level(state: ParseState) -> PackFile:
    t = state.next_token()
    match t:
        case (TokenType.NAME, "function"):
            name = state.next_token().require_name().value
            body = _parse_block(state)
            fn = MCFunction(name, body)
            state.bind_name(name, ColonIdentifier.of(name, fn), MCFunction)
            return fn
        case (TokenType.NAME, "tag"):
            type = state.next_token().require_name().value
            name = state.next_token().require_name().value
            match type:
                case "function":
                    tag = Tag(name, _parse_tag_list(state, MCFunction))
                    state.bind_name(name, ColonIdentifier.of(name, tag), Tag[MCFunction])
                    return tag
                case _:
                    err(state, "Not a supported tag type:")
        case _:
            err(state)

def _parse_block(state: ParseState) -> Block:
    if (state.peek() == Token(TokenType.PUNC, "{")):
        state.next_token()
        body = _resolve_node_tuple(state, Token(TokenType.PUNC, "}"), _parse_cmd)
        return Block(body)
    return Block((_parse_cmd(state),))

def _parse_cmd(state: ParseState) -> CMD:
    t = state.next_token()
    match t:
        case (TokenType.LITERAL, cmd):
            if state.next_token() != (TokenType.PUNC, ";"):
                err(state, "Missing semicolon:")
            return LiteralCMD(value=cmd)
        case (TokenType.NAME, "obj"):
            obj_name = state.next_token().require_name().value
            return OBJ(obj_name)
        case (TokenType.NAME, "score"):
            operand1 = _parse_score(state, prohibit_const=True)
            operation = ScoreboardOperator.of(state.next_token().require_type(TokenType.OP).value)
            operand2 = _parse_score(state)
            return ScoreboardOperation(operand1, operand2, operation)
        case (TokenType.NAME, "while"):
            raise NotImplementedError
        case (TokenType.NAME, "call"):
            function_id = state.next_token().require_name()
            raise NotImplementedError
        case _:
            err(state)

def _parse_score(state: ParseState, prohibit_const: bool = False) -> Score:
    score = (state.next_token(), state.next_token())
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

def _parse_tag_list[T: Taggable](state: ParseState, type: type[T]) -> tuple[Ref[T], ...]:
    vals: tuple[str, ...]
    if (state.peek() == Token(TokenType.PUNC, "{")):
        state.next_token()
        vals = _resolve_node_tuple(state, Token(TokenType.PUNC, "}"), _parse_colon_id)
    else:
        vals = (_parse_colon_id(state),)
    return tuple(state.get_ref(v, type) for v in vals)

def _parse_colon_id[T](state: ParseState, require_exists: bool = True) -> str:
    t = state.next_token()
    match t:
        case (TokenType.NAME, n):
            ColonIdentifier.split_namespace(n) # Checks validity as side effect
            return n
        case _:
            err(state)

def _resolve_node_tuple[T](state: ParseState, end_token: Token, parse_function: Parser[T]) -> tuple[T, ...]:
    """
    Makes a flat tuple of nodes from the tokens
    until it hits the specfied end token or EOF
    """
    node_list: list[T] = []

    # While not out of file and it is not the case
    # that the current token matches end_token

    while state.cursor_in_range():

        # Check for end tokens
        next_token = state.peek()
        if next_token.type == end_token.type and (next_token.value == end_token.value or end_token.value == "*"):
            state.skip() # Skip closing token
            break

        next_node = parse_function(state)
        node_list.append(next_node)
    return tuple(node_list)

if __name__ == "__main__":
    pass
    # It is prefered that tests be run from compiler.py,
    # because that module can import token and other
    # modules that are cousins to parser.py
