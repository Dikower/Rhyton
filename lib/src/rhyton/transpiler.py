import ast
import logging

import sexpdata
from astor import code_gen
from rich.console import Console
from rich.logging import RichHandler
from tree_sitter_languages import get_language, get_parser


logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=Console())]
)

logger = logging.getLogger("rich")

language = get_language("r")
parser = get_parser("r")

COMPARE_OPS = {
    "==",
    ">",
    ">=",
    "<",
    "<=",
}

BOOL_OPS = {"&", "|"}

BIN_OPS = {"+", "-", "*", "/", "^"}

NOT_OP = "!"


def t_definition(node):
    """Variable and function definition translator.

    Translate function_definition node to ast. FunctionDef node. This function is used for translating functions and their parameters.

    Args:
        node: AST node of function definition. It is assumed that function is defined in ast. FunctionDef node.

    Returns:
        return ast. FunctionDef node of translated function definition. It is assumed that function is defined in ast. FunctionDef node
    """
    left, op, right = node.children

    # function_definition func params body func func params body
    if right.type == "function_definition":
        func, params, body = right.children
        logger.debug(f"func: {params.children}")
        args = []
        # Return a list of arguments for the identifier.
        for n in filter(lambda n: n.type == "identifier", params.children):
            args.append(
                ast.arg(
                    n.text.decode("utf-8"),
                )
            )

        # TODO posonlyargs, kwonlyargs, kw_defaults, defaults
        args = ast.arguments(
            args=args, posonlyargs=[], kwonlyargs=[], kw_defaults=[], defaults=[]
        )

        lines = []
        # Add a line to the body.
        for l in body.children:
            lines.append(t_line(l))

        name = left.text.decode("utf-8")
        body = lines
        logger.debug(f"body: {body}")

        # TODO decorator_list
        return ast.FunctionDef(name=name, args=args, body=body, decorator_list=[])

    else:
        name = ast.Name(id=left.text.decode("utf-8"), ctx=ast.Store())
        value = t_expr(right)
        return ast.Assign(targets=[name], value=value)
    # if node.type == "function_definition":
    # logger.debug("children", node.children)


def t_condition(node):
    """Condition translator.

    Converts R { if } expression to ast.If. 
    This is used to convert Python expressions like if and else.

    Args:
        node: The node to convert. This should be an if expression.

    Returns:
        The Python AST equivalent of the expression. 
        This is a { ast.If } node with the body and orelse
    """
    body, orelse, test = [], [], None

    first_brace = True
    # The node is a binary expression.
    for n in node.children:
        if n.type == "binary":
            test = t_expr(node.children[2])
        elif n.type == "brace_list":
            # Add a line to the body of the node.
            for nc in n.children:
                if first_brace:
                    body.append(t_line(nc))
                else:
                    orelse.append(t_line(nc))
            first_brace = False

    return ast.If(test=test, body=body, orelse=orelse)


def t_call(node):
    """Callable translator.

    Translate call to ast. Call. This translates a function call to a python function call. 
    The result is returned as an ast. Expr with the value of the function call

    Args:
        node: the node to translate.

    Returns:
        the translated ast. Expr or None if no function call could be found in the AST.
    """
    # logger.debug("t_call:", node.children)
    name, args = None, None

    # The expression for the identifier and arguments.
    for n in node.children:
        if n.type == "identifier":
            name = t_expr(n, ctx=ast.Load())

        if n.type == "arguments":
            args = []
            # Add None values to args list
            for arg in n.children:
                exp = t_expr(arg, ctx=ast.Load())
                # Filter None values
                if exp:
                    args.append(exp)
    # logger.debug("t_call result:", name, args)
    # Return an expression representing the function name args keywords.
    if name and args:
        # TODO: what is keywords argument
        return ast.Expr(value=ast.Call(func=name, args=args, keywords=[]))


def t_expr(node, ctx=None):
    """Expression translator.

    Convert an expression to a TernaryExpression. 
    This is a recursive function so we don't have to worry about recursion

    Args:
        node: The node to be converted
        ctx: The context of the expression ( unused ).

    Returns:
        The ternary expression converted to a TernaryExpression if possible None otherwise. 
        Note that the context is needed to create a list
    """
    # logger.debug("t_expr:", node)
    # Returns an AST node representing the expression.
    if node.type == "binary":
        left, op, right = node.children
        symbol = op.type
        left = t_expr(left)
        op = t_op(op)
        right = t_expr(right)

        # Returns an AST node representing the current symbol.
        if symbol in BOOL_OPS:
            return ast.BoolOp(op=op, values=[left, right])

        elif symbol in COMPARE_OPS:
            return ast.Compare(left=left, ops=[op], comparators=[right])

        return ast.BinOp(left=left, op=op, right=right)

    elif node.type == "unary":
        op, exp = node.children
        op = t_op(op)
        exp = t_expr(exp)
        return ast.UnaryOp(op=op, operand=exp)

    elif node.type == "paren_list":
        # children[0], children[2] = "(", ")"
        res = t_expr(node.children[1])
        return res

    elif node.type == "identifier":
        return ast.Name(id=node.text.decode("utf-8"))

    elif node.type == "Number":
        return ast.Num(n=int(node.text))

    elif node.type == "float":
        return ast.Num(n=float(node.text))

    elif node.type == ",":
        logger.debug(f"Find ',': {node}")

    else:
        raise TypeError(f'Unknown expression: "{node.type}"')


def t_line(node):
    """Line translator.

    Translates a line to a tree. This is used to translate statements 
    like assignments, conditions, cycles etc.

    Args:
        node: The node that is translated. This should be a L { Node }

    Returns:
        The tree representation of the
    """
    logger.debug(f"t_line: {node}")
    # A left_assignment node is a left_assignment
    if node.type == "left_assignment":
        return t_definition(node)
    # Return the transpilation of a node.
    if node.type == "if":
        return t_condition(node)
    elif node.type == "call":
        return t_call(node)
    elif node.type == "\n":
        pass
    else:
        logger.debug(f"No transpilation provided for: {node.type}")


def t_op(node):
    """Operator translator.

    Translate an operator node to a Python AST operator. 
    This translates the type of the operator node into a ast.<Found operator> 
    which is used to perform the Python code generation

    Args:
        node: The node to translate.

    Returns:
        The ternary operator corresponding to the node's type or 
        TypeError if the unknown operator provided
    """
    operators = {
        "<-": ast.Assign(),
        "+": ast.Add(),
        "-": ast.Sub(),
        "*": ast.Mult(),
        "/": ast.Div(),
        "^": ast.Pow(),
        "==": ast.Eq(),
        ">": ast.Gt(),
        ">=": ast.GtE(),
        "<": ast.Lt(),
        "<=": ast.LtE(),
        "&": ast.And(),
        "|": ast.Or(),
        "!": ast.Not(),
    }

    symbol = node.type#.decode("utf-8")
    # TypeError if symbol is not a valid operator.
    if not operators.get(symbol, None):
        raise TypeError(f'Unknown operator "{node.text}"')
    return operators[symbol]


def transpile(code: str) -> str:
    """Transpile R.

    Translate code to Python source. This is a helper function for transpile_ * functions. 
    It takes a string of R code and translates it into Python source code.

    Args:
        code: String of R code. Must be valid R code.

    Returns:
        Code translated to Python source code. >>> transpile('x <- 7') returns 'x = 7'
    """
    # получаем дерево
    tree = parser.parse(code.encode())
    result = [t_line(child) for child in tree.root_node.children]
    return code_gen.to_source(ast.Module(body=result))


def transpile_file(in_path="/sample.r", out_path="result.py"):
    """Transpile R source file and write result to new one.

    Translate a file containing R code to Python and writes it to another file. 
    This is a wrapper around transpile to ensure UTF-8 encoding

    Args:
        in_path: Path to the input file of R source code
        out_path: Path to the output file ( result. py
    """
    with open(in_path, "r", encoding="utf-8") as file:
        translation = transpile(file.read())

    with open(out_path, "w", encoding="utf-8") as file:
        file.write(translation)

