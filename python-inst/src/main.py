#!/usr/bin/env python3

import ast
from Analyzer import Analyzer
from util import *
from TaintAnalyzer import TaintAnalyzer

def main():
    filename = "fig1.py"
    # filename = "simple.py"

    with open(filename, "r") as src:
        node = ast.parse(src.read())

    # print(ast.dump(node, indent=" "))
    taint = TaintAnalyzer()
    taint.visit(node) # intended dup-visit

    print(GRN("======"))
    print(taint.tainted_node)
    print(GRN("======"))

    analyzer = Analyzer()
    transformed = analyzer.visit(node)

    with open("transformed.py", "w") as dst:
        dst.write(ast.unparse(transformed))
    # print(ast.dump(transformed))

if __name__ == "__main__":
    main()
