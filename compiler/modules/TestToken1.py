from compiler.Tokenizer import Tokenizer

class TestToken1:
    tokens = ("2")

    def calculate(info):
        info.cursor += 1
        print("found 2")