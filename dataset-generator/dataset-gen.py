#!/usr/bin/env python3

import sys
import argparse
import numpy as np
from scipy.stats import skewnorm
import csv

import string
import random

def parse_args():
    parser = argparse.ArgumentParser(description="Fake dataset generator")
    subparser = parser.add_subparsers(dest="command")

    subparser_spec = subparser.add_parser("spec")
    subparser_spec.add_argument("-o", "--out-file", type=str, default="spec.csv")
    subparser_spec.add_argument("-a", "--append", action="store_true")

    subparser_gen = subparser.add_parser("gen")
    subparser_gen.add_argument("-i", "--in-file", type=str, default="spec.csv")
    subparser_gen.add_argument("-o", "--out-file", type=str, default="dataset.csv")

    if len(sys.argv) <= 1:
        parser.print_usage()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "spec":
        prompt_spec(ofile=args.out_file, append=args.append)
    elif args.command == "gen":
        gen_dataset(ifile=args.in_file, ofile=args.out_file)
    else:
        raise ValueError(f"Unexpected command: {args.command}")

def prompt_spec(ofile, append):
    of = open(ofile, "a" if append else "w")

    print("[*] Generating spec")
    of.write("field,type,weight,min,max,avg,priv\n")
    while True:
        to_write = ""
        field       =   str(input("Field              : "))
        if field.strip() == "":
            break
        to_write += f"{field},"
        datatype    =   str(input("Data type          : "))
        datatype = str_formatter(datatype)
        to_write += f"{datatype},"
        weight = "" if datatype == "str" else float(input("Weight             : "))
        to_write += f"{weight},"
        datarange = ",," if datatype == "str" or datatype == "bool" else str(input("Range (min,max,avg): "))
        vmin,vmax,vavg = datarange.split(",")
        to_write += f"{vmin},{vmax},{vavg},"
        private     =   str(input("Is private? (t/f)  : "))
        to_write += f"{str_formatter(private)}\n"
        of.write(to_write)
        print()

    of.close()

def gen_dataset(ifile, ofile):
    N = 1000

    csvfile = open(ifile)

    reader = csv.DictReader(csvfile)
    columns = []
    fields = {}
    weightsum = [0] * N

    for row in reader:
        field = row["field"]
        datatype = str_formatter(row["type"])
        private = str_formatter(row["priv"])

        if datatype == "str":
            fields[field] = [random_str() for _ in range(N)]
        elif datatype == "bool":
            weight = float(row["weight"])
            fields[field] = [random_bool() for _ in range(N)]

            weights = [weight * 0.5 * (1 if x else -1) for x in fields[field]]
            weightsum = [x + y for x, y in zip(weightsum, weights)]
        else:
            weight = float(row["weight"])
            vmin = float(row["min"])
            vmax = float(row["max"])
            aavg = (vmax - vmin) / 2
            vavg = aavg if row["avg"] == "" else float(row["avg"])

            if datatype == "float":
                fields[field] = random_floats(vmin, vmax, vavg, N)
            elif datatype == "int":
                fields[field] = random_ints(vmin, vmax, vavg, N)
            else:
                raise ValueError(f"Unexpected datatype: {datatype}")

            weights = [weight * (x - aavg) / (vmax - vmin) for x in fields[field]]
            weightsum = [x + y for x, y in zip(weightsum, weights)]

    csvfile.close()

    weightsum = weightsum - min(weightsum)
    weightsum = weightsum / max(weightsum)

    for i in range(N):
        columns.append({})
        for key in fields.keys():
            columns[i][key] = fields[key][i]
        columns[i]["Target"] = (weightsum[i] > 0.5)

    of = open(ofile, "w")
    writer = csv.DictWriter(of, fieldnames=list(columns[0].keys()))
    writer.writeheader()
    writer.writerows(columns)
    of.close()

def str_formatter(s):
    list_true = ["t", "T", "true", "True"]
    list_false = ["f", "F", "false", "False"]
    list_str = ["str", "Str", "string", "String"]
    list_int = ["int", "Int", "integer", "Integer"]
    list_float = ["float", "Float"]
    list_bool = ["bool", "Bool", "boolean", "Boolean"]

    if s in list_true:
        return "True"
    elif s in list_false:
        return "False"
    elif s in list_str:
        return "str"
    elif s in list_int:
        return "int"
    elif s in list_float:
        return "float"
    elif s in list_bool:
        return "bool"
    else:
        return ""

def random_str():
    return "".join(random.choices(string.ascii_uppercase, k=8))

def random_bool():
    return random.choice([True, False])

def random_floats(vmin, vmax, vavg, size):
    skew = (vmax - vmin) / 2 - vavg + vmin
    r = skewnorm.rvs(a=skew, size=size)
    r = r - min(r)
    r = r / max(r)
    r = r * (vmax - vmin)
    r = r + vmin
    r = r.astype(np.float64)
    r = list(r)
    return r

def random_ints(vmin, vmax, vavg, size):
    skew = (vmax - vmin) / 2 - vavg + vmin
    r = skewnorm.rvs(a=skew, size=size)
    r = r - min(r)
    r = r / max(r)
    r = r * (vmax - vmin)
    r = r + vmin
    r = r.astype(np.int64)
    r = list(r)
    return r

def main():
    parse_args()

if __name__ == "__main__":
    main()
