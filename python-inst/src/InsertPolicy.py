import ast
import csv
import os

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
            filename = os.path.abspath(rhs.args[0].value)
            var = lhs[0].id

            (filepath, ext) = os.path.splitext(filename)
            policy_filepath = filepath + ".policy.csv"

            policy_file = open(policy_filepath)
            reader = csv.DictReader(policy_file)
            cols = {}
            for row in reader:
                field = row["field"]
                priv = (row["priv"] == "True")
                datatype = row["type"]
                target = (row["target"] == "True")

                cols[field] = { "priv": priv, "type": datatype, "target": target }

            insert_code = (
                f"__policy_{var} = {cols}\n"
            )
            insert_node = ast.parse(insert_code)
            result.extend(insert_node.body)

        result.append(node)
        return result
