import ast
from util import *
from CallClassifier import CallClassifier 
import os

def create_log(dbfile, tx, desc):
    log_code = f"logger.log(\'{dbfile}\',\'{tx}\',{desc})"
    log_node = ast.parse(log_code).body[0]
    return log_node

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

            insert_code = (
                f"{var_cols_x} = list({args[0]}.columns.values)\n"
                f"{var_cols_y} = {args[1]}.name\n"
            )
            insert_node = ast.parse(insert_code).body
            result.extend(insert_node)

            dbfile = "DBFILE"
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

        if not isinstance(rhs, ast.Call):
            return [node]
        
        result = []
        if self.cc.isReadDataset(rhs):
            filename = rhs.args[0].value
            var = lhs[0].id
            filename = os.path.abspath(filename)
            dbfile = f"{filename}"
            tx = "read"
            desc = f"\"{var}=read({filename})\""
            result.append(create_log(dbfile, tx, desc))
        elif self.cc.isDrop(rhs):
            aself = self.cc.extractSelf(rhs)
            arg0 = rhs.args[0]
            ret0 = lhs[0]
            print(f"{ret0.id}=drop({arg0.value})")
            tx = "drop"
            desc = f"\"{ret0.id}=drop({arg0.value})\""
            dbfile = "DBFILFE"
            result.append(create_log(dbfile, tx, desc))

        result.append(node)
        return result
