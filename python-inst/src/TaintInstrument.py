import ast

from util import *
from ASTUtil import *
from Logger import *

class TaintInstrument(ast.NodeTransformer):
    def __init__(self):
        pass

    '''
    def generic_visit(self, node):
        return node
    '''

    def visit_Assign(self, node):
        # ast.Assign(targets, value, type_comment)
        # targets is a list of nodes
        # value is a single node

        result = [node]

        lhs = node.targets
        rhs = node.value

        print("==========")
        lhs_names = []
        for lhs_element in lhs:
            flattened = flatten(lhs_element)
            for flat in flattened:
                lhs_names.append(expr_to_string(flat))
        # print(lhs_names)

        if isinstance(rhs, ast.Call):
            # rhs is call, handle it carefully
            pass
            return result
        else:
            rhs_names = []
            flattened = flatten(rhs)
            for flat in flattened:
                rhs_names.append(expr_to_string(flat))

        if len(lhs_names) == len(rhs_names) and hasattr(rhs, "elts"):
            # HACK: this is likely to be (a, b, c) = (1, 2, 3)
            for pair in zip(lhs_names, rhs_names):
                result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{pair[0]} <- {pair[1]}\""))
        else:
            combinations = [[l, r] for l in lhs_names for r in rhs_names]
            for combination in combinations:
                result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{combination[0]} <- {combination[1]}\""))
            print(combinations)

        # print(lhs_names)
        # print(rhs_names)
        # print(ast.dump(lhs))

        return result

    def visit_AugAssign(self, node):
        # ast.AugAssign(target, op, value)
        # e.g., a += 3

        result = [node]

        lhs = node.target
        rhs = node.value

        # no need to flatten
        lhs_name = expr_to_string(lhs)

        if isinstance(rhs, ast.Call):
            # rhs is call, handle it carefully
            pass
            return result
        else:
            rhs_names = []
            flattened = flatten(rhs)
            for flat in flattened:
                rhs_names.append(expr_to_string(flat))

            result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{lhs_name} <- {lhs_name}\""))
            for rhs_name in rhs_names:
                result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{lhs_name} <- {rhs_name}\""))

        return result

    def visit_Call(self, node):
        return node

    def visit_FunctionDef(self, node):
        prologue = create_log("\"-\"", node.lineno, "\"fn_start\"", f"\"{node.name}\"")
        epilogue = create_log("\"-\"", node.lineno, "\"fn_end\"", f"\"{node.name}\"")

        node.body.insert(0, prologue)
        insert_epilogue_here = []
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Return):
                insert_epilogue_here.append(i)
        for i in reversed(insert_epilogue_here):
            node.body.insert(i, epilogue)

        node.body.append(epilogue)

        return node
