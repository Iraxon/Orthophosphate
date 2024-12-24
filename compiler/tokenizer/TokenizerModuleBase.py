from Token import Token

class TokenizerModuleBase:
    """
    extend this to add a seperate module to the tokenizer.. (ADD IT TO THE LIST OF MODULES)
    """


    #all the tokens that will call this module
    tokens = tuple()

    #if the module needs white space to be considered a token. CAN ONLY BE ONE CHARACTER!! THIS IS A VERY DANGEROUS VARIABLE TO CHANGE!!!
    isTerminating: bool = True

    #OUTPUT: tokenizer output
    #calculates the tokenizer output given the data
    def calculate(cursor: int, compiledTokens: list[Token], data: str) -> tuple:
        """
        OUTPUT: tokenizer output
        calculates the tokenizer output given the data
        """
        
        pass
