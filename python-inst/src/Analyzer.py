# prerequisition: we already mark all dataset variables
#                 .. or not..

import ast
from util import *

class Analyzer(ast.NodeTransformer):
    def __init__(self):
        # self.stats = {"import": [], "class": [], "function": []}
        self.tmp = 0
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
        lhs = node.targets
        if isinstance(lhs[0], ast.Name):
            print(lhs[0].id)

        return [node]

        print(type(node.value))
        if isinstance(node.value, ast.Constant):
            print(node.value.value)
        elif isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                print(node.value.func.attr)
            elif isinstance(node.value.func, ast.Name):
                print(node.value.func.id)
            else:
                print(RED("what else?"))
        # print(node)
        # print(node.value)
        return [node]
 
    def visit_Call(self, node):
        buf = ""
        for arg in node.args:
            if isinstance(arg, ast.Constant):
                buf += arg.value + ", "
            elif isinstance(arg, ast.Name):
                buf += arg.id + ", "
            else:
                buf += str(type(arg)) + ", "

        if "data, " in buf:
            print(buf)

        if buf != "" and False:
            print(buf)

        return node

        if isinstance(node.func, ast.Attribute):
            print(node.func.attr)
        elif isinstance(node.func, ast.Name):
            print(node.func)
            # print(BLU(node.func.id))
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
