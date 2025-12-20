# Orthophosphate Specification

## Grammar

```bnf
<program> ::= {<expr>}

<expr> ::= <application> | <literal> | (<expr>) | {<def>}
<application> ::= <ID> [({<expr>})]
<literal> ::= <INT> | <STR> | <list_literal>
<list_literal> ::= \[ {<expr>} \] | \{ {<expr>} \}

<def> ::= $ <ID> \[ {<ID>} \] \[ {<expr>} \] -> <expr>: <expr>
```

## Present State

```opo4
// Static function for making MCFunction files
$ function [name cmds] [str list(cmd)] -> mcfunction

    text_file(
        path([NAMESPACE name])
        mcfunction_of_str(
            join("\n" cmds)
    ))
```

## Future Intention

```opo4
// Static function for making MCFunction files

$ function [name cmds] [str list(cmd)] -> mcfunction

    text_file
        path [NAMESPACE name]
        mcfunction_of_str
        join "\n" cmds

```
