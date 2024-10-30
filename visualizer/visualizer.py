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
                graph += "    " + nodename + "(\"" + node + "\")\n"
            for edge in script.edges:
                lhs = edge.split("--")[0]
                rhs = edge.split("-->")[1]
                if lhs not in script.databases.values() \
                    and rhs not in script.models.values():
                    graph += "    " + edge + "\n"
            graph += "end\n"

        print(graph)

class Script:
    def __init__(self, name, sid):
        self.name = name
        self.nodes = dict()
        self.edges = []
        self.var_last_appear = dict()

        self.stmts = set()

        self.databases = dict()
        self.models = dict()

        self.scriptid = sid

    def create_node(self, node):
        pass

    def create_edge(self):
        pass

    def new_node(self, action):
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

    def insert_dataflow(self, lineno, action, dataflow):
        if (lineno, action, dataflow) in self.stmts:
            return

        if "loop_" in action:
            return

        if "fn_" in action:
            return

        self.stmts.add((lineno, action, dataflow))

        lhs, rhs = dataflow.split(" <- ", maxsplit=1)
        # lhs <- rhs

        newnode = self.new_node(f"{lhs}")
        if rhs not in self.var_last_appear:
            # rhs must be const, just make lhs out of nowhere without edge
            self.var_last_appear[lhs] = newnode
        else:
            rhs_appear = self.var_last_appear[rhs]
            self.var_last_appear[lhs] = newnode

            self.edges.append(f"{rhs_appear}--->{newnode}")

    def insert_retedge(self, callee, caller):
        lineno = caller[3]

        callee = eval(callee[5])
        caller = eval(caller[5].split("to ")[1])

        for (lhs, rhss) in zip(caller, callee):
            for rhs in rhss:
                self.insert_dataflow(lineno, "return", f"{lhs} <- {rhs}")

def main():
    logfile = "logfile"
    graph = Graph()

    with open(logfile, "r") as f_log:
        csvreader = csv.reader(f_log)
        prevline = ""
        for (i, line) in enumerate(csvreader):
            (time, script, dbfile, lineno, action, dataflow) = line

            # for id()
            dataflow = dataflow.split(" ::")[0]

            script = graph.get_script(script)

            if "fn_return" in action and dataflow != "":
                prevline = line
                continue
            if "callret" in action:
                script.insert_retedge(prevline, line)
                continue

            script.insert_dataflow(lineno, action, dataflow)

    graph.visualize()

if __name__ == "__main__":
    main()
