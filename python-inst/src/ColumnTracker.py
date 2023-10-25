# prerequisition: we already mark all dataset variables
#                 .. or not..

import ast
from util import *

class ColumnTracker(ast.NodeTransformer):
    def __init__(self, train_variables):
        self.dataset_variables = ["df", ]
        self.train_variables = train_variables

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

    def visit_Expr(self, node):
        def isTrainCall(node):
            # TODO: generalize training function here
            # for now, it only detects **.fit(**, **) as training function
            return isinstance(node.value, ast.Call) \
                and isinstance(node.value.func, ast.Attribute) \
                and node.value.func.attr == "fit"

        result = []
        if isTrainCall(node):
            callnode = node.value
            for arg in callnode.args:
                print(RED(arg.id))
                # TODO: for now, there are only two arguments
                # fit(x_train, y_train)
                
                # insert column info here
                # Assign(
                #   targets=[
                #     Name=(id='__cols_x_train', ctx=Store())],
                #   value=Attribute(
                #     value=Name(id='x_train', ctx=Load()),
                #     attr='columns'
                #     ctx=Load())),

                lhs_id = "__cols_" + arg.id
                node_Assign = ast.Assign(
                        targets=[
                            ast.Name(id=lhs_id, ctx=ast.Store())],
                        value=ast.Attribute(
                            value=ast.Name(id=arg.id, ctx=ast.Load()),
                            attr="columns",
                            ctx=ast.Load()))

                result.append(node_Assign)
        result.append(node)
        if isTrainCall(node):
            print(BLU("====="))
            for r in result:
                print(ast.dump(r, indent=2))
            print(BLU("====="))
        return result

    def visit_Call(self, node):
        return [node]

        def isTrainCall(node):
            # TODO: generalize training function here
            # for now, it only detects **.fit(**, **) as training function
            return isinstance(node.func, ast.Attribute) and node.func.attr == "fit"

        result = []

        if isTrainCall(node):
            for arg in node.args:
                print(RED(arg.id))
                # TODO: for now, there are only two arguments
                # fit(x_train, y_train)
                
                # insert column info here
                # Assign(
                #   targets=[
                #     Name=(id='__cols_x_train', ctx=Store())],
                #   value=Attribute(
                #     value=Name(id='x_train', ctx=Load()),
                #     attr='columns'
                #     ctx=Load())),

                lhs_id = "__cols_" + arg.id
                node_Assign = ast.Assign(
                        targets=[
                            ast.Name(id=lhs_id, ctx=ast.Store())],
                        value=ast.Attribute(
                            value=ast.Name(id=arg.id, ctx=ast.Load()),
                            attr="columns",
                            ctx=ast.Load()))
                result.append(node_Assign)

        result.append(node)

        if isTrainCall(node):
            print(GRN("====="))
            print(result)
            print(GRN("====="))

        return result
