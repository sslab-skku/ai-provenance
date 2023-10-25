import ast
from util import *
from CallClassifier import CallClassifier 

class InsertPolicy(ast.NodeTransformer):
    def __init__(self, call_classifier):
        self.call_classifier = call_classifier
        self.cc = self.call_classifier

    def visit_Assign(self, node):
        lhs = node.targets
        rhs = node.value

        if not isinstance(rhs, ast.Call):
            return [node]
        
        result = []
        if self.cc.isReadDataset(rhs):
            filename = rhs.args[0].value
            var = lhs[0].id

            # TODO: read policy.xml here using filename (heart.csv)
            # seriously, why xml?
            cols = {"age": 1, "sex": 1, "cp": 1, "trestbps": 0, "chol": 0, "fbs": 1, "restecg": 1,
                "thalach": 0, "exang": 0, "oldpeak": 0, "slope": 0, "ca": 1, "thal": 1, "target": 1}
            
            insert_code = (
                f"__policy_{var} = {cols}\n"
            )
            insert_node = ast.parse(insert_code)
            result.extend(insert_node.body)

        result.append(node)
        return result
