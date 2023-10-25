#!/usr/bin/env python3

import ast
import os

from Analyzer import Analyzer
from util import *
from TaintAnalyzer import TaintAnalyzer
# from ColumnTracker import ColumnTracker
from ImportAnalyzer import ImportAnalyzer
from CallClassifier import CallClassifier
from CallTracker import CallTracker
from InsertPolicy import InsertPolicy
from Rule3 import Rule3
from Rule4 import Rule4

def main():
    targets = [
        "../examples/target1_dpreg.py",
        "../examples/target2_dropfbs.py",
        "../examples/target3_randforest.py",
        "../examples/target4_sexpredict.py",
        "../examples/target5_svm.py",
        "../examples/target6_svmminmax.py",
    ]

    if not os.path.exists("transformed"):
        os.mkdir("transformed")

    for target in targets:
        with open(target, "r") as src:
            node = ast.parse(src.read())

        # print(ast.dump(node, indent=" "))
        # taint = TaintAnalyzer()
        # taint.visit(node) # intended dup-visit

        # print(GRN("======"))
        # print(taint.tainted_node)
        # print(GRN("======"))

        # print(ast.dump(node, indent=2))

        '''
        analyzer = Analyzer()
        transformed = analyzer.visit(node)
        '''
        # print(ast.dump(node, indent=2))
        # ta = TaintAnalyzer()
        # after_ta = ta.visit(node)
        # print(ast.dump(after_ta, indent=2))

        curnode = node

        import_analyzer = ImportAnalyzer()
        import_analyzer.visit(curnode)
        import_as = import_analyzer.import_as
        from_import_all = import_analyzer.from_import_all

        call_classifier = CallClassifier(import_as, from_import_all)

        insert_policy = InsertPolicy(call_classifier)
        curnode = insert_policy.visit(curnode)

        call_tracker = CallTracker(call_classifier)
        curnode = call_tracker.visit(curnode)

        rule3 = Rule3(call_classifier)
        curnode = rule3.visit(curnode)
        rule4 = Rule4(call_classifier)
        curnode = rule4.visit(curnode)

        curnode = ast.fix_missing_locations(curnode)

        filename = target.split("/")[-1]
        with open("./transformed/transformed_" + filename, "w") as dst:
            dst.write(ast.unparse(curnode))
        # print(ast.dump(after_ct, indent=2))

if __name__ == "__main__":
    main()
