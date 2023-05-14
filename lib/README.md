<div id="header" align="center">
<img src="https://i.ibb.co/9mxMf46/rhyton-logo.png" alt="Rhyton logo"/>
  <h1>
    <i>Rhyton</i> - R to Python transpiler
  </h1>
</div>

##📜 What is _Rhyton_

__Rhyton__ is a type of ancient Greek drinking vessel that is in the shape of an animal's head or horn and has a hole in the bottom for pouring the liquid. It was often used in religious ceremonies or feasts.

The name came after combination of language names: _R_ and _Python_

This library helps you to move R codebase to Python. Right now it supports conversion of _math equations_, _expressions_, _conditions_, _function definitions_ and _calls_

## 🧲 Installation
The project is published on [__PyPi__](https://pypi.org/project/rhyton/), so you can install it via __pip__

```shell
$: pip install rhyton
```

## 🚀 Launch
Use _transpile_ or _transpile_file_ to translate your __R__ code

```python
from rhyton import transpile, transpile_file

transpile('x <- 7') # returns transpiled string

# or

transpile_file(
  in_path='<path to your R file>.r', 
  out_path='<Path to generated Python file>.py'
)

```

## 🛠 How it works
__Rhyton__ uses tree-sitter under the hood, to compute _AST_ (Abstract Syntax Tree), after that it converts it to new _AST_ that is valid for Python. After that it generates a code, using [_ast module_](https://docs.python.org/3/library/ast.html) and [_astor_](https://astor.readthedocs.io/en/latest/)

## 📊 Feature plan
* ✅ Add tree parsers
* ✅ Semantic analysis for _AST_
  * ✅ Statements and expressions
  * ✅ Math operations
  * ✅ Conditions: _if_, _else_
  * ✅ Function definitions
  * ✅ Function calls
  * ❌ Cycles while and for
  * ❌ Arrays and operations
  * ❌ Function analogs
  * ❌ Import statements 
  * ❌ Nested transpilation

* ✅ Package demo publication
* ✅ Project site
