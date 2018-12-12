# Example R(x1)
# Input: ['R', ['x1']]
import argparse
import parser
from objects import UCNF
from objects import CNF
from objects import Clause
from db import SQL_DB 

def CNFConverttoUCNF(cnf):
    if (cnf.isClause()):
        return cnf.clauses[0].getUCNF()
    alpha = cnf.clauses[0]

    gamma = CNF()
    for i in cnf.clauses[1:]:
        gamma.addClause(i)
    ucnf = UCNF()

    for i in alpha.getUCNF().cnfs:
        for j in CNFConverttoUCNF(gamma).cnfs:
            ucnf.add_cnf(i.mergeCNF(j))
    return ucnf


def get_val_domain(var, atom):
    if (var == None): return []
    for i in range(len(atom.variables)):
        if (var in atom.variables[i]):
            break
    t = atom.table_dict[atom.name]
    val_domain = list()
    for j in t.vals:
        val_domain.append(int(j[i]))
    return list(set(val_domain))


def grounding(var, val, cnf):
    for clause in cnf.clauses:
        for atom in clause.atoms:
            for i in range(len(atom.variables)):
                if (var in atom.variables[i]):
                    atom.variables[i] = val
    return


def ucnf_independent(cnf, ucnf):
    for i in ucnf.cnfs:
        if cnf.is_independent(i):
            continue
        else:
            return False
    return True


def lifted_inference_UCNF(ucnf):
    if (len(ucnf.cnfs) == 1):
        cnf = ucnf.cnfs[0].deep_copy()
        return lifted_inference(cnf)
    else:
        cnf1 = ucnf.cnfs[0].deep_copy()
        ucnf1 = UCNF()
        for i in ucnf.cnfs[1:]:
            ucnf1.add_cnf(i.deep_copy())
        if (ucnf_independent(cnf1, ucnf1)):
            prob1 = lifted_inference(cnf1)
            prob2 = lifted_inference_UCNF(ucnf1)
            return 1 - (1 - prob1)(1 - prob2)
        else:
            prob1 = lifted_inference(cnf1)
            prob2 = lifted_inference_UCNF(ucnf1)
            ucnf12 = get_UCNF(cnf1, ucnf1)
            prob12 = lifted_inference_UCNF(ucnf12)
            return prob1 + prob2 - prob12


def get_UCNF(initial_cnf, initial_ucnf):
    ucnf = UCNF()
    for i in initial_ucnf.cnfs:
        ucnf.add_cnf(initial_cnf.mergeCNF(i.deep_copy()))
    return ucnf

def cnf_independent(clause, clause_list):
    for i in clause_list:
        if (not clause.is_independent(i)):
            return False
    return True

def lifted_inference(cnf, db=None):
    cnf.rewrite()
    if (cnf.isClause()):
        clause = cnf.clauses[0]
        if len(clause.atoms) == 1:
            if (len(clause.variables)) == 0:
                atom = clause.atoms[0] 
                if db == None: 
                    prob = atom.get_value() 
                else: 
                    if atom.negation: 
                        prob = db.get_prob(atom.name, atom.variables) 
                    else: 
                        prob = 1.0 - db.get_prob(atom.name, atom.variables) 
                return prob

    ucnf = CNFConverttoUCNF(cnf)
    if (len(ucnf.cnfs) == 2):
        cnf1 = ucnf.cnfs[0].deep_copy()
        cnf2 = ucnf.cnfs[1].deep_copy()
        if (cnf1.is_independent(cnf2)):
            prob1 = lifted_inference(cnf1,db)
            prob2 = lifted_inference(cnf2,db)
            return 1 - (1 - prob1) * (1 - prob2)
        else:
            prob1 = lifted_inference(cnf1,db)
            prob2 = lifted_inference(cnf2,db)
            cnf12 = cnf1.mergeCNF(cnf2)
            prob12 = lifted_inference(cnf12,db)
            return prob1 + prob2 - prob12


    if (len(ucnf.cnfs) > 2):
        cnf1 = ucnf.cnfs[0].deep_copy()
        ucnf1 = UCNF()
        for i in ucnf.cnfs:
            ucnf1.add_cnf(i.deep_copy())
        if ucnf_independent(cnf1, ucnf1):
            prob1 = lifted_inference(cnf1,db)
            prob2 = lifted_inference_UCNF(ucnf1)
            return 1 - (1 - prob1) * (1 - prob2)
        else:
            prob1 = lifted_inference(cnf1,db)
            prob2 = lifted_inference_UCNF(ucnf1)
            ucnf12 = get_UCNF(cnf1, ucnf1)
            prob12 = lifted_inference_UCNF(ucnf12)
            return prob1 + prob2 - prob12

    if (len(ucnf.cnfs) == 1):
        if (len(cnf.clauses) == 1):
            var = cnf.get_separator()
            if (var == None):
                return 0
            else:
                val_domain = get_val_domain(var, cnf.clauses[0].atoms[0])
                prob = 1
                for i in val_domain:
                    cnf__1 = cnf.deep_copy()
                    grounding(var, str(i), cnf__1)
                    prob = prob * lifted_inference(cnf__1,db)
                return prob

        if (len(cnf.clauses) == 2):
            if (cnf.clauses[0].is_independent(cnf.clauses[1])):
                cnf_1 = CNF()
                cnf_2 = CNF()
                cnf_1.addClause(cnf.clauses[0].deep_copy())
                cnf_2.addClause(cnf.clauses[1].deep_copy())
                return lifted_inference(cnf_1,db)*lifted_inference(cnf_2,db)
            var = cnf.get_separator()
            if (var == "None"):
                return 0
            else:
                val_domain = get_val_domain(var, cnf.clauses[0].atoms[0])
                prob = 1
                for i in val_domain:
                    cnf__1 = cnf.deep_copy()
                    grounding(var, str(i), cnf__1)
                    prob = prob * lifted_inference(cnf__1,db)
                return prob
        else:
            for i in range(len(cnf.clauses)):
                cnf_1 = CNF()
                cnf_2 = CNF()

                cnf.clauses[0], cnf.clauses[i] = cnf.clauses[i], cnf.clauses[0]
                cnf_1.addClause(cnf.clauses[0].deep_copy())
                for i in cnf.clauses[1:]:
                    cnf_2.addClause(i.deep_copy())
                cnf_0 = cnf_1.clauses[0]
                cnf_list = cnf_2.clauses
                if (cnf_independent(cnf_0, cnf_list)):
                    return lifted_inference(cnf_2,db) * lifted_inference(cnf_1,db)

            var = cnf.get_separator()
            if (var == None):
                return 0
            else:
                val_domain = get_val_domain(var, cnf.clauses[0].atoms[0])
                prob = 1
                for i in val_domain:
                    cnf__1 = cnf.deep_copy()
                    grounding(var, str(i), cnf__1)
                    prob = prob * lifted_inference(cnf__1,db)
                    return prob

def main():
    """
    Read database files and parse into a table dictionary with tableName, table key/value pair
    """

    argparser = argparse.ArgumentParser()

    argparser.add_argument("--table", nargs=3, help="input the file name of table")
    argparser.add_argument("--query", help="input the file name of query")
    argparser.add_argument("-d", help="database mode", action='store_true')
    args = argparser.parse_args()
    query_name = args.query
    #table_name = args.table


    filenames = args.table
    table_dict = {}
    for dbfile in filenames:
        t = parser.pdbTable('./db/' + dbfile)
        table_dict[t.table_name] = t

    parsed_query = parser.parse_query('./db/' + query_name)
    db = None
    if args.d:
        db_file = 'prob.db' 
        db = SQL_DB(filenames, db_file) 
    cnf = CNF()
    for q in parsed_query:
        cnf.addClause(Clause(q, table_dict))

    print(1 - lifted_inference(cnf,db))

if __name__ == "__main__":
    main()
