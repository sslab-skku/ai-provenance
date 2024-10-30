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
    def __init__(self, visitor, int_funcs):
        self.visitor = visitor
        self.int_funcs = int_funcs # set of internal function names
        self.scope = "__main__"

    '''
    def generic_visit(self, node):
        return node
    '''

    def assign_family(self, node, lhss, rhs):
        # result = [node]
        result = []

        rhsnodes = self.visitor.visit(rhs)

        flag_internal_fn = False
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
                fnname = expr_to_string(rhs)[:-2]

                print(fnname)
                for func in self.int_funcs:
                    if func.name != fnname:
                        continue

                    # now func is what we're searching for
                    for (arg, param) in zip(rhs.args, func.node.args.args):
                        result.append(create_log("\"-\"", node.lineno, f"\"callarg: {fnname}\"", f"\"{param.arg} <- {expr_to_string(arg)}\""))
                        flag_internal_fn = True
                    break
                else:
                    # func is external fn
                    combinations = [[l, r] for l in lhs_flat for r in rhs_flat]
                    loading_apis = ["ImageFolder", "torch.load"]
                    for combination in combinations:
                        if fnname in loading_apis:
                            # if "args.data_path" in rhs_flat:
                                # print("print fname")
                                # print("print fname")
                            print(fnname)
                            new_rhs_flat = rhs_flat
                            if any(isinstance(r, list) for r in new_rhs_flat):
                                # handle list of list lol
                                new_rhs_flat = [r for r in new_rhs_flat[0]]
 

                            print(new_rhs_flat)
                            if len(new_rhs_flat) == 2:
                                result.append(
                                    create_log(
                                        '"-"',
                                        node.lineno,
                                        f'"path"',
                                        # f"\"{combination[0]} <- '\" + str(os.listdir(os.path.join({new_rhs_flat[0]}, \"{new_rhs_flat[1].replace(" (const)","")}\")))  + \"'\" ",
                                        f'"{combination[0]} <- \'" + str(os.listdir(os.path.join({new_rhs_flat[0]}, "{new_rhs_flat[1].replace(" (const)","")}")))  + "\'" ',
                                    )
                                )
                            else:
                                result.append(
                                    create_log(
                                        '"-"',
                                        node.lineno,
                                        f'"path"',
                                        f'"{combination[0]} <- \'" + str(os.listdir({new_rhs_flat[0]}) if os.path.isdir({new_rhs_flat[0]}) else {new_rhs_flat[0]}) + "\'"',
                                    )
                                )

                        # result.append(create_log("\"-\"", node.lineno, f"\"call: {fnname}\"", f"\"{combination[0]} <- {combination[1]}" + " :: \" + " + "f\"{id(" + f"{combination[0]}" + ")}\""))
                        result.append(create_log("\"-\"", node.lineno, f"\"extcall: {fnname}\"", f"\"{combination[0]} <- {combination[1]}\""))

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

        result.append(node)
        if flag_internal_fn:
            for lhs in lhss:
                lhsnodes = self.visitor.visit(lhs)

                lhs_flat = log_flatten(lhsnodes, [], node.lineno)

                if not isinstance(lhs_flat, list):
                    lhs_flat = [lhs_flat]

                result.append(create_log("\"-\"", node.lineno, f"\"callret: {fnname}\"", f"\"return to {lhs_flat}\""))
        return result

    def visit_Assign(self, node):
        # ast.Assign(targets, value, type_comment)
        # targets is a list of nodes
        # value is a single node

        lhss = node.targets
        rhs = node.value

        return self.assign_family(node, lhss, rhs)

    def visit_AugAssign(self, node):
        # ast.AugAssign(target, op, value)
        # e.g., a += 3

        lhss = [node.target]
        rhs = node.value

        return self.assign_family(node, lhss, rhs)

    def visit_Call(self, node):
        return node

    def visit_FunctionDef(self, node):
        # visit children first
        self.generic_visit(node)

        prologue = create_log("\"-\"", node.lineno, "\"fn_start\"", f"\"{node.name}\"")
        epilogue = create_log("\"-\"", node.lineno, "\"fn_return\"", f"\"{node.name}\"")

        callstack_push_code = f"ProvenanceLogger.callstack.append(\"{node.name}\")\n"
        callstack_push_node = ast.parse(callstack_push_code).body[0]
        callstack_pop_code = f"ProvenanceLogger.callstack.pop()\n"
        callstack_pop_node = ast.parse(callstack_pop_code).body[0]

        node.body.insert(0, prologue)
        node.body.insert(0, callstack_push_node)
        insert_epilogue_here = []
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Return):
                insert_epilogue_here.append((i, stmt.value))
        for (i, retval) in reversed(insert_epilogue_here):
            if isinstance(retval, ast.Tuple):
                retvec = flatten_elts(retval)
            else:
                retvec = [retval]

            ret = []
            for flat in retvec:
                ret.append(list(map(lambda fl: expr_to_string(fl), flatten(flat))))
            node.body.insert(i, callstack_pop_node)
            node.body.insert(i, create_log("\"-\"", node.lineno, f"\"fn_return({node.name})\"", f"\"{ret}\""))

        node.body.append(create_log("\"-\"", node.lineno, f"\"fn_return({node.name})\"", "\"\""))
        node.body.append(callstack_pop_node)

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
