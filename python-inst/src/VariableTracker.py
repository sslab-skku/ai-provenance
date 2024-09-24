# NOTE: type here means semantic type, not datatype
# e.g. self.typemap["df"] = ["dataset"], not ["pandas.DataFrame"]

import ast
import json
from util import *

class VariableTracker():
    def __init__(self):
        self.typemap = {}
        self.alias = {}

    def insert_typemap(self, varname, typename):
        if varname not in self.typemap:
            self.typemap[varname] = []
        if typename not in self.typemap[varname]:
            self.typemap[varname].append(typename)
