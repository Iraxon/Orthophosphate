# Orthophosphate Specification

## Grammar

```peg
program        <- expr+ EOF

expr           <- inline_expr+ NEWLINE (INDENT expr+ DEDENT)?
inline_expr    <- NAME ('('expr+ ')')* / NAME / literal

// Variables are considered functions
// of zero args and not treated
// separately

literal        <- INT / STR / list_literal
list_literal   <- '[' expr+ ']' / '{' expr+ '}'

```
