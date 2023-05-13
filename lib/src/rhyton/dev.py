import logging
import pathlib
from transpiler import transpile

logging.basicConfig(
    level="NOTSET",
)

path = pathlib.Path(__file__).parent / "./transpile_test/func.r"

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

print(transpile(code))
