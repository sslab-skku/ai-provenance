# rule 3: GDPR 4-(1) Personal Data
#     Any personal data's column should not be inferenced except target column

import ast
from util import *
from CallClassifier import CallClassifier 

class Rule3(ast.NodeTransformer):
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
                f"if __policy_df[__cols_{args[1]}] == 1 and __cols_{args[1]} != \"target\":\n"
                f"    print(\"[Log] Rule 3 violated\")\n"
            )
            insert_node = ast.parse(insert_code).body
            result.extend(insert_node)

        result.append(node)
        return result
