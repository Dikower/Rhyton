# import ast

# from rich.console import Console
# from astor import code_gen


# console = Console()

# code = """
# r = 120
# if r > (100 + 2) and (r < 100 or r == 0 and not r):
#     print(r + 40)
#     print(r + 50)
# else:
#     print(r + 10)
#     print(r + 12)
# """

# code = """
# def my_function(a, b):
#   sum = a + b
#   print(sum)


# my_function(1, 2) 
# """

# parsed = ast.parse(code)

# console.log(ast.dump(parsed, indent=2))

# print(code_gen.to_source(parsed))

from transpiler import transpile
