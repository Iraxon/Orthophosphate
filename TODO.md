# TODO

## Tokenizer

Currently working.

## Parser

Rewrite how sequences of nodes are handled, to fix the following parse error:
`a b(2)` -> `<a b> (2)`
This should be:
`a b(2)` -> `a(b(2))`

Intended fix is to make parsing of node sequences depend on a right paren or
newline to start. Building of the sequence would then go right to left.

## Datapack Generator

Waiting on parser work.
