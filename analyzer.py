# prerequisition: we already mark all dataset variables
#                 .. or not..

import ast
from util import *

class Analyzer(ast.NodeTransformer):
    def __init__(self):
        # self.stats = {"import": [], "class": [], "function": []}
        pass

    def visit_Import(self, node):
        Import_names = [name.name for name in node.names]

        print_Expr = GadgetGen.gen_Print(Import_names)

        return [node, print_Expr]

        '''
        for Import_name in Import_names:
            # print(Import_name.name, Import_name.asname)
            Arg_print = [ast.Constant(value=f"{Import_name.name} as {Import_name.asname}")]

        Call_print = ast.Call(func=Name_print, args=Arg_print, keywords=[])
        Expr_print = ast.Expr(value=Call_print)
        '''

    def visit_Assign(self, node):
        super(Analyzer, self).generic_visit(node)
        return [node]
 
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            print(node.func.attr)
        elif isinstance(node.func, ast.Name):
            print(BLU(node.func.id))
        else:
            print(RED("what else?"))
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
