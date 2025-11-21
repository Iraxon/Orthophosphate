import typing
from .token import Token


class TokenizerModuleBase(typing.NamedTuple):
    """
    extend this to add a seperate module to the tokenizer.. (ADD IT TO THE LIST OF MODULES)
    """

    # all the strings that this token matches
    matches: tuple[str, ...]

    # OUTPUT: tokenizer output
    # calculates the tokenizer output given the data
    @staticmethod
    def calculate(
        cursor: int, compiledTokens: list[Token], data: str
    ) -> tuple[int, list, str]:
        """
        OUTPUT: tokenizer output
        calculates the tokenizer output given the data
        """
        if len(TokenizerModuleBase.matches) > 1:
            token_string = ""
            while (
                cursor < len(data)
                and token_string + data[cursor] in TokenizerModuleBase.matches
            ):
                token_string += data[cursor]
                cursor += 1
            return cursor, compiledTokens, data

        if len(TokenizerModuleBase.matches) == 1:
            if compiledTokens[cursor] not in TokenizerModuleBase.matches:
                raise ValueError(
                    f"Calculate called for single-character token {compiledTokens[cursor]}, "
                    f"which is not a match for {typing.Self}; "
                    f"matches: {TokenizerModuleBase.matches}"
                )
            cursor += 1
            return cursor, compiledTokens, data
        raise ValueError(f"{TokenizerModuleBase} has zero listed matches")
