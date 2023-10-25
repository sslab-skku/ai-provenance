# prerequisition: we already mark all dataset variables
#                 .. or not..

import ast
from util import *

class TaintAnalyzer(ast.NodeTransformer):
    def __init__(self):
        self.dataset_variables = ["df", ]
        self.train_variables = []
        # self.stats = {"import": [], "class": [], "function": []}
        self.tmp = 0

    def generic_visit(self, node):
        if isinstance(node, ast.Name):
            if node.id in self.dataset_variables:
                self.tmp += 1

        for child in ast.iter_child_nodes(node):
            self.visit(child)

        return node

    def visit_Assign(self, node):
        lhs = node.targets
        if len(lhs) != 1:
            print(RED("lhs size is not 1"))
            return [node]

        if isinstance(lhs[0], ast.Name):
            if lhs[0].id in self.dataset_variables:
                print(f"{lhs[0].id} is in dataset variables")
        
        rhs = node.value
        self.tmp = 0
        self.generic_visit(rhs)

        # propagate every lhs = dataset_variables
        '''
        if self.tmp != 0:
            print(GRN("dataset propagated"))
            if isinstance(lhs[0], ast.Name):
                self.dataset_variables.append(lhs[0].id)
            elif isinstance(lhs[0], ast.Tuple):
                for name in lhs[0].elts:
                    self.dataset_variables.append(name.id)
        '''

        return [node]

    def visit_Call(self, node):
        def isTrainCall(node):
            # TODO: generalize training function here
            # for now, it only detects **.fit(**, **) as training function
            return isinstance(node.func, ast.Attribute) and node.func.attr == "fit"

        if isinstance(node.func, ast.Attribute):
            print(node.func.attr)
        elif isinstance(node.func, ast.Name):
            print(node.func)
        else:
            print(RED("call: node mismatch"))

        if isTrainCall(node):
            for arg in node.args:
                # TODO: for now, there are only two arguments
                # fit(x_train, y_train)
                self.train_variables.append(arg.id)

        return node


class GadgetGen():
    def gen_Print(args):
        # Expr(
        #   value=Call(
        #     func=Name(
        #       id='print',
        #       ctx=Load()
        #     ),
        #     args=[..]
        #   )
        # )

        print_Name = ast.Name(id="print", ctx=ast.Load())
        print_args = [ast.Constant(value=f"{arg}") for arg in args]
        print_Call = ast.Call(func=print_Name, args=print_args, keywords=[])
        print_Expr = ast.Expr(value=print_Call)

        return print_Expr
