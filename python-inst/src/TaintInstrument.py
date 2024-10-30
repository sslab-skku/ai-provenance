import ast

from util import *
from ASTUtil import *
from Logger import *

def log_flatten(node, code, lineno):
    if isinstance(node, tuple):
        if node[0] == "subscript":
            # node[1][node[2]]
            # log: subscript, node[1] <- node[1][node[2]]
            node1 = log_flatten(node[1], code, lineno)
            node2 = log_flatten(node[2], code, lineno)
            code.append(create_log("\"-\"", lineno, f"\"subscript\"",
                f"\"{node1} <- {node1}[{node2}]\""))
            return f"{node1}[{node2}]"
        elif node[0] == "attribute":
            # node[1].node[2]
            # log: attribute, node[1] <- node[1].node[2]
            node1 = log_flatten(node[1], code, lineno)
            node2 = log_flatten(node[2], code, lineno)
            code.append(create_log("\"-\"", lineno, f"\"attribute\"",
                f"\"{node1} <- {node1}.{node2}\""))
            return f"{node1}.{node2}"
        else:
            print(RED("what else"))
    elif isinstance(node, list):
        result = []
        for n in node:
            result.append(log_flatten(n, code, lineno))
        return result
    else:
        return node


class TaintInstrument(ast.NodeTransformer):
    def __init__(self, visitor):
        self.visitor = visitor

    '''
    def generic_visit(self, node):
        return node
    '''

    def visit_Assign(self, node):
        # ast.Assign(targets, value, type_comment)
        # targets is a list of nodes
        # value is a single node

        result = [node]

        lhss = node.targets
        rhs = node.value

        print("==========")
        rhsnodes = self.visitor.visit(rhs)
        for lhs in lhss:
            lhsnodes = self.visitor.visit(lhs)
            print(f"{node.lineno}: {lhsnodes}")
            print(f"{node.lineno}: {rhsnodes}")

            # connect internals first
            code = []

            lhs_flat = log_flatten(lhsnodes, code, node.lineno)
            rhs_flat = log_flatten(rhsnodes, code, node.lineno)

            if not isinstance(lhs_flat, list):
                lhs_flat = [lhs_flat]
            if not isinstance(rhs_flat, list):
                rhs_flat = [rhs_flat]

            result.extend(code)

            # connect lhs <- rhs
            if isinstance(rhs, ast.Call):
                fnname = expr_to_string(rhs)

                combinations = [[l, r] for l in lhs_flat for r in rhs_flat]
                for combination in combinations:
                    # result.append(create_log("\"-\"", node.lineno, f"\"call: {fnname}\"", f"\"{combination[0]} <- {combination[1]}" + " :: \" + " + "f\"{id(" + f"{combination[0]}" + ")}\""))
                    result.append(create_log("\"-\"", node.lineno, f"\"call: {fnname}\"", f"\"{combination[0]} <- {combination[1]}\""))
            else:
                if len(lhs_flat) == len(rhs_flat) and hasattr(rhs, "elts"):
                    # HACK: this is likely to be (a, b, c) = (1, 2, 3)
                    for pair in zip(lhs_flat, rhs_flat):
                        # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{pair[0]} <- {pair[1]}" + " :: \" + " + "f\"{id(" + f"{pair[0]}" + ")}\""))
                        result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{pair[0]} <- {pair[1]}\""))
                else:
                    combinations = [[l, r] for l in lhs_flat for r in rhs_flat]
                    for combination in combinations:
                        # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{combination[0]} <- {combination[1]}" + " :: \" + " + "f\"{id(" + f"{combination[0]}" + ")}\""))
                        result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{combination[0]} <- {combination[1]}\""))
                
        return result

        lhs_names = []
        for lhs_element in lhss:
            flattened = flatten(lhs_element)
            for flat in flattened:
                lhs_names.append(expr_to_string(flat))
        lhs_names = list(map(lambda name: name.split(".")[0], lhs_names))

        if isinstance(rhs, ast.Call):
            # rhs is call, handle it carefully
            rhs_name = expr_to_string(rhs)
            args = extract_args_from_call(rhs)

            combinations = [[l, r] for l in lhs_names for r in args]
            for combination in combinations:
                # result.append(create_log("\"-\"", node.lineno, f"\"call: {rhs_name}\"", f"\"{combination[0]} <- {combination[1]}" + " :: \" + " + "f\"{id(" + f"{combination[0]}" + ")} <- {id(" + f"{combination[1]}" + ")}\""))
                # result.append(create_log("\"-\"", node.lineno, f"\"call: {rhs_name}\"", f"\"{combination[0]} <- {combination[1]}" + " :: \" + " + "f\"{id(" + f"{combination[0]}" + ")}\""))
                result.append(create_log("\"-\"", node.lineno, f"\"call: {rhs_name}\"", f"\"{combination[0]} <- {combination[1]}\""))
            # result.append(node)
            return result
        else:
            rhs_names = []
            flattened = flatten(rhs)
            for flat in flattened:
                rhs_names.append(expr_to_string(flat))
            rhs_names = list(map(lambda name: name.split(".")[0], rhs_names))

        if len(lhs_names) == len(rhs_names) and hasattr(rhs, "elts"):
            # HACK: this is likely to be (a, b, c) = (1, 2, 3)
            for pair in zip(lhs_names, rhs_names):
                # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{pair[0]} <- {pair[1]}" + " :: \" + " + "f\"{id(" + f"{pair[0]}" + ")} <- {id(" + f"{pair[1]}" + ")}\""))
                # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{pair[0]} <- {pair[1]}" + " :: \" + " + "f\"{id(" + f"{pair[0]}" + ")}\""))
                result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{pair[0]} <- {pair[1]}\""))
        else:
            combinations = [[l, r] for l in lhs_names for r in rhs_names]
            for combination in combinations:
                # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{combination[0]} <- {combination[1]}" + " :: \" + " + "f\"{id(" + f"{combination[0]}" + ")} <- {id(" + f"{combination[1]}" + ")}\""))
                # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{combination[0]} <- {combination[1]}" + " :: \" + " + "f\"{id(" + f"{combination[0]}" + ")}\""))
                result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{combination[0]} <- {combination[1]}\""))

        # result.append(node)
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
            rhs_name = expr_to_string(rhs)
            args = extract_args_from_call(rhs)

            for arg in args:
                # result.append(create_log("\"-\"", node.lineno, f"\"call: {rhs_name}\"", f"\"{lhs_name} <- {arg}" + " :: \" + " + "f\"{id(" + f"{lhs_name}" + ")} <- {id(" + f"{arg}" + ")}\""))
                # result.append(create_log("\"-\"", node.lineno, f"\"call: {rhs_name}\"", f"\"{lhs_name} <- {arg}" + " :: \" + " + "f\"{id(" + f"{lhs_name}" + ")}\""))
                result.append(create_log("\"-\"", node.lineno, f"\"call: {rhs_name}\"", f"\"{lhs_name} <- {arg}\""))
            # result.append(node)
            return result
        else:
            rhs_names = []
            flattened = flatten(rhs)
            for flat in flattened:
                rhs_names.append(expr_to_string(flat))
            rhs_names = list(map(lambda name: name.split(".")[0], rhs_names))

            # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{lhs_name} <- {lhs_name}" + " :: \" + " + "f\"{id(" + f"{lhs_name}" + ")} <- {id(" + f"{lhs_name}" + ")}\""))
            # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{lhs_name} <- {lhs_name}" + " :: \" + " + "f\"{id(" + f"{lhs_name}" + ")}\""))
            result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{lhs_name} <- {lhs_name}\""))
            for rhs_name in rhs_names:
                # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{lhs_name} <- {rhs_name}" + " :: \" + " + "f\"{id(" + f"{lhs_name}" + ")} <- {id(" + f"{rhs_name}" + ")}\""))
                # result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{lhs_name} <- {rhs_name}" + " :: \" + " + "f\"{id(" + f"{lhs_name}" + ")}\""))
                result.append(create_log("\"-\"", node.lineno, "\"assign\"", f"\"{lhs_name} <- {rhs_name}\""))

        # result.append(node)
        return result

    def visit_Call(self, node):
        return node

    def visit_FunctionDef(self, node):
        # visit children first
        self.generic_visit(node)

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

    def visit_For(self, node):
        # visit children first
        self.generic_visit(node)

        prologue = create_log("\"-\"", node.lineno, "\"loop_start\"", "\"\"")
        epilogue = create_log("\"-\"", node.lineno, "\"loop_end\"", "\"\"")

        '''
        node.body.insert(0, prologue)
        insert_epilogue_here = []
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Break):
                insert_epilogue_here.append(i)
        for i in reversed(insert_epilogue_here):
            node.body.insert(i, epilogue)

        node.body.append(epilogue)
        '''

        return [prologue, node, epilogue]

    def visit_Subscript(self, node):
        print(ast.dump(node))
        return node
