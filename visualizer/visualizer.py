#!/usr/bin/env python3

import csv

set_dbfile = set()

class Graph:
    def __init__(self):
        self.scripts = dict()

    def get_script(self, sname):
        if sname not in self.scripts:
            self.scripts[sname] = Script(sname, len(self.scripts) + 1)
        return self.scripts[sname]

    def visualize(self):
        graph = ""
        graph += "graph LR\n"
        graph += "\n"

        for script in self.scripts.values():
            for (dbname, dbnode) in script.databases.items():
                graph += f"{dbnode}(\"{dbname}\")\n"
            for (modelname, modelnode) in script.models.items():
                graph += f"{modelnode}(\"{modelname}\")\n"
        graph += "\n"

        for script in self.scripts.values():
            for edge in script.edges:
                lhs = edge.split("--")[0]
                rhs = edge.split("-->")[1]
                if lhs in script.databases.values():
                    graph += edge + "\n"
                if rhs in script.models.values():
                    graph += edge + "\n"
        graph += "\n"

        for script in self.scripts.values():
            graph += f"subgraph sc{script.scriptid} [\"{script.name}\"]\n"
            for (nodename, node) in script.nodes.items():
                if script.tags.get(nodename) != None:
                    graph += "    " + nodename + "(\"" + node + "\")\n"

            sensitive_edges = []
            skipped = 0
            for (i, edge) in enumerate(script.edges):
                lhs = edge.split("--")[0]
                rhs = edge.split("-->")[1]
                if script.tags.get(lhs) == None or script.tags.get(rhs) == None:
                    skipped += 1
                    continue

                if script.tags.get(lhs) == "UNLEARN":
                    sensitive_edges.append(i - skipped)

                if lhs in script.databases.values() \
                    or rhs in script.models.values():
                    continue

                graph += "    " + edge + "\n"
            
            for sensitive in sensitive_edges:
                graph += f"    linkStyle {sensitive} stroke:red, stroke-width:2px\n"

            graph += "end\n"

        print(graph)
        with  open("graph.mmd", "w") as f:
            f.write(graph)
            f.close()


class Script:
    def __init__(self, name, sid):
        self.name = name
        self.nodes = dict()
        self.edges = []
        self.var_last_appear = dict()

        self.stmts = set()

        self.tags = dict()

        self.databases = dict()
        self.models = dict()

        self.scriptid = sid

    def create_node(self, node):
        pass

    def create_edge(self):
        pass

    def new_node(self, action):
        for (k, v) in self.nodes.items():
            if v == action:
                return k

        nodename = f"SC{self.scriptid}N{len(self.nodes)+1}"
        self.nodes[nodename] = action

        return nodename

    def new_db(self, filename):
        # CAUTION: it is filename -> dbname relation, which is opposite of node

        if filename in self.databases:
            return self.databases[filename]

        dbname = f"D{len(self.databases)+1}"
        self.databases[filename] = dbname

        return dbname
    
    def new_model(self, modelname):
        # CAUTION: it is varname -> modelid relation, which is opposite of node

        if modelname in self.models:
            return self.models[modelname]

        modelid = f"SC{self.scriptid}M{len(self.models)+1}"
        self.models[modelname] = modelid

        return modelid

    def insert_dataflow(self, scope, lineno, action, dataflow):
        if (lineno, action, dataflow) in self.stmts:
            return

        if "loop_" in action:
            return

        if "fn_" in action:
            return

        self.stmts.add((lineno, action, dataflow))

        # print(dataflow, "\t", action)
        lhs, rhs = dataflow.split(" <- ", maxsplit=1)

        if "callarg" in action:
            # diff scope
            callee = action.split(": ")[1]
            self.dataflow(lineno, action, f"{lhs} ({callee})", f"{rhs} ({scope})")
        else:
            self.dataflow(lineno, action, f"{lhs} ({scope})", f"{rhs} ({scope})")

    def insert_retedge(self, callee, caller):
        lineno = caller[4]

        calleescope = callee[3]
        callerscope = caller[3]

        callee = eval(callee[6])
        caller = eval(caller[6].split("to ")[1])

        for (lhs, rhss) in zip(caller, callee):
            for rhs in rhss:
                self.dataflow(lineno, "return", f"{lhs} ({callerscope})", f"{rhs} ({calleescope})")

    def dataflow(self, lineno, action, lhs, rhs):
        # lhs <- rhs

        if "(const)" in rhs:
            return

        newnode = self.new_node(f"{lhs}")

        if "path" in action and "extcall" not in action:
            import ast
            # Heuristic to detect list
            rhs = rhs.split(" (")[0]
            if rhs[1] == "[" and rhs[-2]=="]":
                rhs = rhs[1:-1]
            paths = ast.literal_eval(rhs)
            if isinstance(paths, list):
                for p in paths:
                    '''
                    if not self.var_last_appear.get(p):
                        newnode_path = self.new_db(f"{p}")
                        self.var_last_appear[p] = newnode_path
                    else:
                        newnode_path = self.var_last_appear[p]
                    '''
                    newnode_path = self.new_db(f"{p}")
                    self.var_last_appear[p] = newnode_path

                    self.edges.append(f"{newnode_path}--->{newnode}")
            else:
                p = paths
                '''
                if not self.var_last_appear.get(p):
                    newnode_path = self.new_db(f"{p}")
                    self.var_last_appear[p] = newnode_path
                else:
                    newnode_path = self.var_last_appear[p]
                '''
                newnode_path = self.new_db(f"{p}")
                self.var_last_appear[p] = newnode_path
                self.edges.append(f"{newnode_path}--->{newnode}")
        else:
            if rhs not in self.var_last_appear:
                # rhs must be const, just make lhs out of nowhere without edge
                self.var_last_appear[lhs] = newnode
            else:
                rhs_appear = self.var_last_appear[rhs]
                self.var_last_appear[lhs] = newnode

                self.edges.append(f"{rhs_appear}--{lineno}-->{newnode}")

    def taint(self):
        for database in self.databases.values():
            self.tags[database] = "DATABASE"

        # SCENARIO: Won_bin is now private and needs to be unlearned
        self.tags[self.databases["Won_bin"]] = "UNLEARN"

        changed = True
        while changed:
            changed = False
            for edge in self.edges:
                lhs = edge.split("--")[0]
                rhs = edge.split("-->")[1]
                if self.tags.get(lhs) == "DATABASE" \
                    and (self.tags.get(rhs) != "DATABASE" and self.tags.get(rhs) != "UNLEARN"):
                    changed = True
                    self.tags[rhs] = "DATABASE"
                if self.tags.get(lhs) == "UNLEARN" \
                    and self.tags.get(rhs) != "UNLEARN":
                    changed = True
                    self.tags[rhs] = "UNLEARN"

    def sort_edges(self):
        result = []

        for edge in self.edges:
            lhs = edge.split("--")[0]
            rhs = edge.split("-->")[1]
            if lhs in self.databases.values():
                result.append(edge)

        for edge in self.edges:
            lhs = edge.split("--")[0]
            rhs = edge.split("-->")[1]
            if lhs not in self.databases.values() and rhs in self.models.values():
                result.append(edge)

        for edge in self.edges:
            lhs = edge.split("--")[0]
            rhs = edge.split("-->")[1]
            if lhs not in self.databases.values() and rhs not in self.models.values():
                result.append(edge)

        self.edges = result

def main():
    logfile = "logfile"
    graph = Graph()

    with open(logfile, "r") as f_log:
        csvreader = csv.reader(f_log)
        prevline = ""
        for (i, line) in enumerate(csvreader):
            (time, script, dbfile, scope, lineno, action, dataflow) = line

            # for id()
            dataflow = dataflow.split(" ::")[0]

            script = graph.get_script(script)

            if "fn_return" in action and dataflow != "":
                prevline = line
                continue
            if "callret" in action:
                script.insert_retedge(prevline, line)
                continue

            script.insert_dataflow(scope, lineno, action, dataflow)

    for script in graph.scripts:
        graph.get_script(script).taint()
        graph.get_script(script).sort_edges()

    graph.visualize()

if __name__ == "__main__":
    main()
