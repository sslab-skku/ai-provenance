import ast

from util import *

class TaintAnalyzer(ast.NodeVisitor):
    tainted_node = []

    def __init__(self):
        # self.stats = {"import": [], "class": [], "function": []}
        pass

    def visit_Import(self, node):
        Import_names = [name.name for name in node.names]

        return [node]

        '''
        for Import_name in Import_names:
            # print(Import_name.name, Import_name.asname)
            Arg_print = [ast.Constant(value=f"{Import_name.name} as {Import_name.asname}")]

        Call_print = ast.Call(func=Name_print, args=Arg_print, keywords=[])
        Expr_print = ast.Expr(value=Call_print)
        '''

    def visit_Assign(self, node):
        super(TaintAnalyzer, self).generic_visit(node)
        return [node]
 
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            print(node.func.attr)
        elif isinstance(node.func, ast.Name):
            print(node.func)
            # print(BLU(node.func.id))
        else:
            print(RED("what else?"))
        return node
