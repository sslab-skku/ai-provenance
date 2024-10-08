import ast
from util import *
from CallClassifier import CallClassifier 
from VariableTracker import VariableTracker
import os

def create_log(dbfile, tx, desc):
    log_code = f"logger.log({dbfile},\'{tx}\',{desc})"
    log_node = ast.parse(log_code).body[0]
    return log_node

class Logger(ast.NodeTransformer):
    def __init__(self, call_classifier, variable_tracker):
        self.call_classifier = call_classifier
        self.cc = self.call_classifier
        self.variable_tracker = variable_tracker
        self.vt = self.variable_tracker

    def visit_Module(self, node):
        insert_code = (
            f"import time\n"
            f"class ProvenanceLogger:\n"
            f"    def __init__(self, filename):\n"
            f"        self.logfile = open(filename, \'a\')\n"
            f"    def log(self, dbfile, tx, desc):\n"
            f"        curtime = time.ctime()\n"
            f"        self.logfile.write(f'{{curtime}},{{__file__}},{{dbfile}},{{tx}},\"{{desc}}\"\\n')"
            f"\n"
            f"logger = ProvenanceLogger(\"logfile\")\n"
        )
        insert_node = ast.parse(insert_code).body
        node.body = insert_node + node.body

        self.generic_visit(node)

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

            var_cols_x = f"__cols_{args[0]}"
            var_cols_y = f"__cols_{args[1]}"


            '''
            insert_code = (
                f"{var_cols_x} = list({args[0]}.columns.values)\n"
                f"{var_cols_y} = {args[1]}.name\n"
            )
            insert_node = ast.parse(insert_code).body
            result.extend(insert_node)
            '''

            dbfile = "\"DBFILE\""
            tx = "train"
            descx = f"{var_cols_x}"
            descy = f"{var_cols_y}"

            desc = "\"args0:\"+" + "f\"{" + descx + "}\""
            desc += "\" args1:\"+" + "f\"{" + descy + "}\""
            desc += "\" priv:\"+" + f"f\"{{[col for col in {var_cols_x} if __policy_df[col]['priv']]}}\""
            result.append(create_log(dbfile, tx, desc))

        result.append(node)
        return result

    def visit_Assign(self, node):
        lhs = node.targets
        rhs = node.value

        if isinstance(rhs, ast.Call):
            return self.check_assign_call(node)
        elif isinstance(rhs, ast.Subscript):
            # check dataset slicing/indexing
            print(rhs.value.id)
            ret0 = lhs[0].id
            rhs0 = rhs.value.id
            rhs1 = rhs.slice.value

            ret0_db = f"__dbfile_{ret0}"
            rhs0_db = f"__dbfile_{rhs0}"

            ret0_cols = f"__cols_{ret0}"

            insert_code = ""
            if f"{ret0_db}" !=  f"{rhs0_db}":
                insert_code += f"{ret0_db} = {rhs0_db}\n"
            insert_code += f"{ret0_cols} = [\"{rhs1}\"]\n"
            insert_node = ast.parse(insert_code).body
            result = [node]
            result.append(insert_node)
            print(insert_code)
            # print(f"{ret0} = {rhs0}")
            return result
        else:
            return [node]

    def check_assign_call(self, node):
        lhs = node.targets
        rhs = node.value
        
        result = [node]

        if self.cc.isReadDataset(rhs):
            tx = "read"

            arg0 = rhs.args[0].value
            ret0 = lhs[0].id

            filename = os.path.abspath(arg0)

            ret0_db = f"__dbfile_{ret0}"
            ret0_cols = f"__cols_{ret0}"

            insert_code = (
                f"{ret0_db} = \"{filename}\"\n"
                f"{ret0_cols} = list({ret0}.columns)\n"
            )
            insert_node = ast.parse(insert_code).body
            result.append(insert_node)

            dbfile = "\"" + f"{filename}" + "\""

            desc =  "\"" + f"{ret0}: " + "\"" + "f\"{" + f"{ret0_cols}" + "}\""

            result.append(create_log(dbfile, tx, desc))

            self.vt.insert_typemap(f"{arg0}", "filename")
            self.vt.insert_typemap(f"{ret0}", "dataset")
        elif self.cc.isDrop(rhs):
            tx = "drop"

            aself = self.cc.extractSelf(rhs)
            arg0 = rhs.args[0].value
            ret0 = lhs[0].id

            aself_db = f"__dbfile_{aself}"
            ret0_db = f"__dbfile_{ret0}"

            aself_cols = f"__cols_{aself}"
            ret0_cols = f"__cols_{ret0}"

            insert_code = ""
            if f"{ret0_db}" != f"{aself_db}":
                insert_code += f"{ret0_db} = {aself_db}\n"
            if f"{ret0_cols}" != f"{aself_cols}":
                insert_code += f"{ret0_cols} = {aself_cols}[:]\n"
            insert_code += f"{ret0_cols}.remove(\"{arg0}\")\n"
            # insert_code += f"{ret0_cols} = list({ret0}.columns)\n"
            insert_node = ast.parse(insert_code).body
            result.append(insert_node)

            dbfile = "f\"{" + f"{ret0_db}" + "}\""
            desc = "\"" + f"{ret0}: " + "\"" + "f\"{" + f"{ret0_cols}" + "}\""

            result.append(create_log(dbfile, tx, desc))

            self.vt.insert_typemap(f"{aself}", "dataset")
            self.vt.insert_typemap(f"{ret0}", "dataset")
        elif self.cc.isSplit(rhs):
            tx = "assign"

            arg0 = rhs.args[0].id
            arg1 = rhs.args[1].id

            ret0 = lhs[0].elts

            arg0_db = f"__dbfile_{arg0}"
            arg1_db = f"__dbfile_{arg1}"
            ret00_db = f"__dbfile_{ret0[0].id}"
            ret01_db = f"__dbfile_{ret0[1].id}"
            ret02_db = f"__dbfile_{ret0[2].id}"
            ret03_db = f"__dbfile_{ret0[3].id}"

            arg0_cols = f"__cols_{arg0}"
            arg1_cols = f"__cols_{arg1}"
            ret00_cols = f"__cols_{ret0[0].id}"
            ret01_cols = f"__cols_{ret0[1].id}"
            ret02_cols = f"__cols_{ret0[2].id}"
            ret03_cols = f"__cols_{ret0[3].id}"

            insert_code = (
                f"{ret00_db} = {arg0_db}\n"
                f"{ret01_db} = {arg0_db}\n"
                f"{ret02_db} = {arg1_db}\n"
                f"{ret03_db} = {arg1_db}\n"
                f"{ret00_cols} = {arg0_cols}\n"
                f"{ret01_cols} = {arg0_cols}\n"
                f"{ret02_cols} = {arg1_cols}\n"
                f"{ret03_cols} = {arg1_cols}\n"
                # f"{ret00_cols} = list({ret0[0].id}.columns)\n"
                # f"{ret01_cols} = list({ret0[1].id}.columns)\n"
                # f"{ret02_cols} = list({ret0[2].id}.name)\n"
                # f"{ret03_cols} = list({ret0[3].id}.name)\n"
            )
            insert_node = ast.parse(insert_code).body
            result.append(insert_node)

            dbfile00 = "f\"{" + f"{ret00_db}" + "}\""
            desc00 = "\"" + f"{ret0[0].id}: " + "\"" + "f\"{" + f"{ret00_cols}" + "}\""
            result.append(create_log(dbfile00, tx, desc00))

            dbfile01 = "f\"{" + f"{ret01_db}" + "}\""
            desc01 = "\"" + f"{ret0[1].id}: " + "\"" + "f\"{" + f"{ret01_cols}" + "}\""
            result.append(create_log(dbfile01, tx, desc01))

            dbfile02 = "f\"{" + f"{ret02_db}" + "}\""
            desc02 = "\"" + f"{ret0[2].id}: " + "\"" + "f\"{" + f"{ret02_cols}" + "}\""
            result.append(create_log(dbfile02, tx, desc02))

            dbfile03 = "f\"{" + f"{ret03_db}" + "}\""
            desc03 = "\"" + f"{ret0[3].id}: " + "\"" + "f\"{" + f"{ret03_cols}" + "}\""
            result.append(create_log(dbfile03, tx, desc03))

        return result
