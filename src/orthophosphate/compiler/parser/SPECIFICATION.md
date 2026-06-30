# Orthophosphate Specification

## Grammar

The grammar is specified as a PEG, but the parser
is not a packrat parser (allowing left recursion).

```peg
program             <- multiline_expr+ EOF

multiline_expr      <- multiline_args indented_args? / list_literal
multiline_args      <- inline_expr+ NEWLINE
indented_args       <- INDENT multiline_expr+ DEDENT

inline_expr         <- inline_expr inline_args / inline_list_literal / literal_or_var
inline_args         <- '(' inline_expr+ ')'

literal_or_var      <- NAME / INT / STR
list_literal        <- '[' multiline_expr* ']'
inline_list_literal <- '[' inline_expr* ']'
```
