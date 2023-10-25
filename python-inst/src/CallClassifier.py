# heusristically classify methods
# same role with KB (knowledge base) from Vamsa (KDD '20)

import ast
from util import *

class CallClassifier():
    def __init__(self, import_as, from_import_all):
        self.import_as = import_as
        self.from_import_all = from_import_all

    def getMethodFullName(self, node):
        assert isinstance(node, ast.Call), RED("Given node is not ast.Call")

        func = node.func

        if isinstance(func, ast.Attribute):
            if func.value.id in self.import_as:
                return f"{self.import_as[func.value.id]}.{func.attr}"
            else:
                # always var.method
                return f"{func.attr}"
                # return f"{func.value.id}.{func.attr}"
        else:
            if func.id in self.import_as:
                return f"{self.import_as[func.id]}"
            else:
                return f"{func.id}"

    def getPossibleMethodFullName(self, node):
        assert isinstance(node, ast.Call), RED("Given node is not ast.Call")

        func = node.func

        fullname = self.getMethodFullName(node)

        result = []
        result.append(fullname)

        if "." not in fullname:
            for import_all in self.from_import_all:
                result.append(f"{import_all}.{fullname}")

        print(result)
        return result


    def isSplit(self, node):
        assert isinstance(node, ast.Call), RED("Given node is not ast.Call")

        func = node.func
        fullnames = self.getMethodFullName(node)

        if "sklearn.model_selection.train_test_split" in fullnames:
            return True

        return False

    def isFit(self, node):
        assert isinstance(node, ast.Call), RED("Given node is not ast.Call")

        func = node.func
        fullnames = self.getMethodFullName(node)

        # TODO: how can we differentiate model.fit and another fit methods?
        if len(node.args) != 2:
            return False

        if "fit" in fullnames:
            return True

        return False

    def isDrop(self, node):
        assert isinstance(node, ast.Call), RED("Given node is not ast.Call")

        func = node.func
        fullnames = self.getMethodFullName(node)

        if "drop" in fullnames:
            return True

        return False

    def isReadDataset(self, node):
        assert isinstance(node, ast.Call), RED("Given node is not ast.Call")

        func = node.func
        fullnames = self.getMethodFullName(node)

        if "pandas.read_csv" in fullnames:
            return True

        return False
