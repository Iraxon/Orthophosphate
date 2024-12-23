from helper.TokenizerInfo import TokenizerInfo

from helper.TokenizerOutput import TokenizerOutput

class TokenizerModuleBase:
    """
    extend this to add a seperate module to the tokenizer.. (ADD IT TO THE LIST OF MODULES)
    """


    #all the tokens that will call this module
    tokens = tuple()

    #OUTPUT: tokenizer output
    #calculates the tokenizer output given the data
    def calculate(info: TokenizerInfo) -> TokenizerOutput:
        """
        OUTPUT: tokenizer output
        calculates the tokenizer output given the data
        """
        
        pass
