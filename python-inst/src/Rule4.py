# rule 4: GDPR 5-(1)-(c) Data Minimization
#     The column that abs(correlation) is below given threshold to target column may not be used

import ast
from util import *
from CallClassifier import CallClassifier 

class Rule4(ast.NodeTransformer):
    def __init__(self, call_classifier):
        self.call_classifier = call_classifier
        self.cc = self.call_classifier

    def visit_Expr(self, node):
        if not isinstance(node.value, ast.Call):
            return [node]

        call = node.value
        
        result = []
        if self.cc.isFit(call):
            args = [name.id for name in call.args]
            
            # TODO: relate args to origin dataset variable name
            insert_code = (
                f"__corrwith_{args[1]} = df.corrwith(df[__cols_{args[1]}])\n"
                f"__rule4_violated = []\n"
                f"for __col_arg0 in __cols_{args[0]}:\n"
                f"    if abs(__corrwith_{args[1]}[__col_arg0]) < 0.1:\n"
                f"        __rule4_violated.append(__col_arg0)\n"
                f"if __rule4_violated != []:\n"
                f"    print(f\"[Log] Rule 4 violated: {{__rule4_violated}}\")\n"
                # f"print(\"[Log]    correlation with {{__cols_{args[1]}}}\")\n"
            )
            insert_node = ast.parse(insert_code).body
            result.extend(insert_node)

        result.append(node)
        return result
