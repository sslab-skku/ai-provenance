import ast
from util import *
from CallClassifier import CallClassifier 

class Logger(ast.NodeTransformer):
    def __init__(self, call_classifier):
        self.call_classifier = call_classifier
        self.cc = self.call_classifier

    def visit_Module(self, node):
        insert_code = (
            f"import time\n"
            f"class ProvenanceLogger:\n"
            f"    def __init__(self, filename):\n"
            f"        self.logfile = open(filename, \'a\')\n"
            f"    def log(self, msg):\n"
            f"        timestamp = time.ctime()\n"
            f"        self.logfile.write(timestamp + \": \" + msg + \"\\n\")"
            f"\n"
            f"logger = ProvenanceLogger(\"logfile\")\n"
        )
        insert_node = ast.parse(insert_code).body
        node.body = insert_node + node.body
        return node

    def visit_Call(self, node):
        return node

    def visit_Expr(self, node):
        if not isinstance(node.value, ast.Call):
            return [node]

        call = node.value
        
        result = []
        if self.cc.isFit(call):
            args = [name.id for name in call.args]
            # TODO: relate args to original dataset variable
            # e.g., relate x_train, y_train with df
            insert_code = (
                f"print(\"[Log] Training model with argument {args}\")\n"
                f"__cols_{args[0]} = list({args[0]}.columns.values)\n"
                f"__cols_{args[1]} = {args[1]}.name\n"
                f"print(f\"[Log] columns from {args[0]}: {{__cols_{args[0]}}}\")\n"
                f"print(f\"[Log]   private columns: {{[col for col in __cols_{args[0]} if __policy_df[col] == 1]}}\")\n"
                f"print(f\"[Log] columns from {args[1]}: {{__cols_{args[1]}}}\")\n"
            )
            insert_node = ast.parse(insert_code).body
            result.extend(insert_node)

        result.append(node)
        return result

    def visit_Assign(self, node):
        lhs = node.targets
        rhs = node.value

        print("Loggerassign")

        if not isinstance(rhs, ast.Call):
            return [node]
        
        result = []
        if self.cc.isReadDataset(rhs):
            filename = rhs.args[0].value
            var = lhs[0].id
            msg = f"Read dataset from {filename} to {var}\n"
            result.append(create_log(msg))

        result.append(node)
        return result
