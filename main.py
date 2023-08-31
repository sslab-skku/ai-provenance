#!/usr/bin/env python3

import ast
from analyzer import Analyzer

def main():
    filename = "fig1.py"
    # filename = "simple.py"

    with open(filename, "r") as src:
        node = ast.parse(src.read())

    print(ast.dump(node, indent=" "))

    analyzer = Analyzer()
    transformed = analyzer.visit(node)

    with open("transformed.py", "w") as dst:
        dst.write(ast.unparse(transformed))
    # print(ast.dump(transformed))

if __name__ == "__main__":
    main()
