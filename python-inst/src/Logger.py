import ast
from util import *
from CallClassifier import CallClassifier 
from VariableTracker import VariableTracker
import os
import csv

def create_log(dbfile, lineno, tx, desc):
    log_code = f"logger.log({dbfile},{lineno},{tx},{desc})"
    log_node = ast.parse(log_code).body[0]
    return log_node

def get_id_or_value(node):
    try:
        ret = (node.id, True)
    except AttributeError:
        ret = (node.value, False)

    return ret

class Logger(ast.NodeTransformer):
    def __init__(self, call_classifier, variable_tracker):
        self.call_classifier = call_classifier
        self.cc = self.call_classifier
        self.variable_tracker = variable_tracker
        self.vt = self.variable_tracker

    def visit_Module(self, node):
        insert_code = (
            # f"import time\n"
            f"from time import ctime\n"
            f"class ProvenanceLogger:\n"
            f"    def __init__(self, filename):\n"
            f"        self.logfile = open(filename, \'a\')\n"
            f"    def log(self, dbfile, lineno, tx, desc):\n"
            # f"        curtime = time.ctime()\n"
             f"        curtime = ctime()\n"
            f"        self.logfile.write(f'{{curtime}},{{__file__}},{{dbfile}},{{lineno}},{{tx}},\"{{desc}}\"\\n')"
            f"\n"
            f"logger = ProvenanceLogger(\"logfile\")\n"
        )
        insert_node = ast.parse(insert_code).body
        node.body = insert_node + node.body

        self.generic_visit(node)

        return node
