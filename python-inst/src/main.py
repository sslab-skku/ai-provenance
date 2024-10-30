#!/usr/bin/env python3

import ast
import os

from Analyzer import Analyzer
from util import *
from TaintInstrument import TaintInstrument
from MyVisitor import MyVisitor
from InternalFunctions import InternalFunctions
from ImportAnalyzer import ImportAnalyzer
from Logger import Logger

def main():
    basedir = os.getcwd()

    '''
    targets = [
        "../examples/target1_dpreg.py",
        "../examples/target2_dropfbs.py",
        "../examples/target3_randforest.py",
        "../examples/target4_sexpredict.py",
        "../examples/target5_svm.py",
        "../examples/target6_svmminmax.py",
    ]
    '''
    # targets = ["../scenario/script1.py"]
    # targets = ["../../ai-examples/facial_recog/detector.py"]
    targets = ["../../../privacy_demo/main.py"]

    '''
    if not os.path.exists("transformed"):
        os.mkdir("transformed")
    '''

    for target in targets:
        with open(target, "r") as src:
            node = ast.parse(src.read())

        print(target)

        curnode = node

        import_analyzer = ImportAnalyzer()
        import_analyzer.visit(curnode)
        import_as = import_analyzer.import_as
        from_import_all = import_analyzer.from_import_all

        # call_classifier = CallClassifier(import_as, from_import_all, basedir + "/KB.json")
        # variable_tracker = VariableTracker()

        visitor = MyVisitor()

        _internal = InternalFunctions()
        _internal.visit(curnode)
        int_funcs = _internal.int_funcs
        
        print(int_funcs)

        tainter = TaintInstrument(visitor, int_funcs)
        curnode = tainter.visit(curnode)

        # logger = Logger(call_classifier, variable_tracker)
        logger = Logger()
        curnode = logger.visit(curnode)

        # print(logger.vt.typemap)

        curnode = ast.fix_missing_locations(curnode)

        filename = target.split("/")[-1]

        # os.chdir(basedir)

        with open("transformed_" + filename, "w") as dst:
            dst.write(ast.unparse(curnode))

        # with open("../../../privacy_demo/transformed_" + filename, "w") as dst:
        #     dst.write(ast.unparse(curnode))
        # print(ast.dump(curnode, indent=2))

if __name__ == "__main__":
    main()
