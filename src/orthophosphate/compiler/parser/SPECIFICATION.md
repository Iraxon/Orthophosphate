# Orthophosphate Specification

## Grammar

```peg
program        <- expr+ EOF

expr           <- application / inline_expr NEWLINE
inline_expr    <- inline_app / literal

// Variables are considered functions
// of zero args and not treated
// separately

application    <- NAME inline_expr* NEWLINE INDENT (expr+ / args_block) DEDENT
inline_app     <- NAME ('('expr+ ')')?

literal        <- INT / STR / list_literal
list_literal   <- '[' expr+ ']' / '{' expr+ '}'

# Function definitions are parsed as a function
# application of `$` on arguments
```

## Example

```opo4
// Static function for making MCFunction files

$ function [name cmds] [str list(cmd)] -> mcfunction

    text_file
        path [NAMESPACE name]
        mcfunction_of_str
            join "\n" cmds

```
