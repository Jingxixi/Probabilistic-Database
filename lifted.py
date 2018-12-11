# Example R(x1)
# Input: ['R', ['x1']]
import parser
import copy
from objects import CNF, Atom, Clause, UCNF


def ConverttoUCNF(cnf):
    if (cnf.isClause()):
        return cnf.clauses[0].getUCNF()
    alpha = cnf.clauses[0]

    gamma = CNF()
    for i in cnf.clauses[1:]:
        gamma.addClause(i)
    ucnf = UCNF()

    for i in alpha.getUCNF().cnfs:
        for j in ConverttoUCNF(gamma).cnfs:
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

def cnf_independent(clause, clause_list):
    for i in clause_list:
        if (not clause.is_independent(i)):
            return False
    return True






def lifted_inference(cnf):
    cnf.rewrite()
    if (cnf.isClause()):
        clause = cnf.clauses[0]
        if len(clause.atoms) == 1:
            if (len(clause.variables)) == 0:
                prob = clause.atoms[0].get_value()
                return prob

    ucnf = ConverttoUCNF(cnf)
    if (len(ucnf.cnfs) == 2):
        if (ucnf.cnfs[0].is_independent(ucnf.cnfs[1])):
            cnf1 = ucnf.cnfs[0].deep_copy()
            cnf2 = ucnf.cnfs[1].deep_copy()
            prob1 = lifted_inference(cnf1)
            prob2 = lifted_inference(cnf2)
            return 1 - (1 - prob1) * (1 - prob2)
        else:
            cnf1 = ucnf.cnfs[0].deep_copy()
            cnf2 = ucnf.cnfs[1].deep_copy()
            cnf12 = cnf1.mergeCNF(cnf2)
            prob12 = lifted_inference(cnf12)
            prob1 = lifted_inference(cnf1)
            prob2 = lifted_inference(cnf2)

            return prob1 + prob2 - prob12

    if (len(ucnf.cnfs) == 3):
        cnf1 = ucnf.cnfs[0].deep_copy()
        cnf2 = ucnf.cnfs[1].deep_copy()
        cnf3 = ucnf.cnfs[2].deep_copy()
        cnf12 = cnf1.mergeCNF(cnf2)
        cnf13 = cnf1.mergeCNF(cnf3)
        cnf23 = cnf2.mergeCNF(cnf3)
        cnf123 = cnf12.mergeCNF(cnf3)
        prob1 = lifted_inference(cnf1)
        prob2 = lifted_inference(cnf2)
        prob3 = lifted_inference(cnf3)
        prob12 = lifted_inference(cnf12)
        prob13 = lifted_inference(cnf13)
        prob23 = lifted_inference(cnf23)
        prob123 = lifted_inference(cnf123)
        return prob1 + prob2 + prob3 - prob12 - prob13 - prob23 + prob123

    if (len(ucnf.cnfs) == 4):
        cnf1 = ucnf.cnfs[0].deep_copy()
        cnf2 = ucnf.cnfs[1].deep_copy()
        cnf3 = ucnf.cnfs[2].deep_copy()
        cnf4 = ucnf.cnfs[3].deep_copy()
        cnf12 = cnf1.mergeCNF(cnf2)
        cnf13 = cnf1.mergeCNF(cnf3)
        cnf14 = cnf1.mergeCNF(cnf4)
        cnf23 = cnf2.mergeCNF(cnf3)
        cnf24 = cnf2.mergeCNF(cnf4)
        cnf34 = cnf3.mergeCNF(cnf4)
        cnf123 = cnf12.mergeCNF(cnf3)
        cnf124 = cnf12.mergeCNF(cnf4)
        cnf134 = cnf13.mergeCNF(cnf4)
        cnf234 = cnf23.mergeCNF(cnf4)
        cnf1234 = cnf123.mergeCNF(cnf4)
        prob1234 = lifted_inference(cnf1234)
        prob1 = lifted_inference(cnf1)
        prob2 = lifted_inference(cnf2)
        prob3 = lifted_inference(cnf3)
        prob4 = lifted_inference(cnf4)
        prob12 = lifted_inference(cnf12)
        prob13 = lifted_inference(cnf13)
        prob14 = lifted_inference(cnf14)
        prob23 = lifted_inference(cnf23)
        prob24 = lifted_inference(cnf24)
        prob34 = lifted_inference(cnf34)
        prob123 = lifted_inference(cnf123)
        prob124 = lifted_inference(cnf124)
        prob134 = lifted_inference(cnf134)
        prob234 = lifted_inference(cnf234)
        prob_1 = prob1 + prob2 + prob3 + prob4
        prob_2 = prob12 + prob13 + prob14 + prob23 + prob24 + prob34
        prob_3 = prob123 + prob124 + prob134 + prob234
        prob_4 = prob1234
        return prob_1 - prob_2 + prob_3 - prob_4
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
                    prob = prob * lifted_inference(cnf__1)
                return prob

        if (len(cnf.clauses) == 2):
            if (cnf.clauses[0].is_independent(cnf.clauses[1])):
                cnf_1 = CNF()
                cnf_2 = CNF()
                cnf_1.addClause(cnf.clauses[0])
                cnf_2.addClause(cnf.clauses[1])
                return lifted_inference(cnf_1)*lifted_inference(cnf_2)
            var = cnf.get_separator()
            if (var == "None"):
                return 0
            else:
                val_domain = get_val_domain(var, cnf.clauses[0].atoms[0])
                prob = 1
                for i in val_domain:
                    cnf__1 = cnf.deep_copy()
                    grounding(var, str(i), cnf__1)
                    prob = prob * lifted_inference(cnf__1)
                return prob
        else:
            for i in range(len(cnf.clauses)):
                cnf_1 = CNF()
                cnf_2 = CNF()
                cnf.clauses[0], cnf.clauses[i] = cnf.clauses[i], cnf.clauses[0]
                cnf_1.addClause(cnf.clauses[0])
                for i in cnf.clauses[1:]:
                    cnf_2.addClause(i)
                cnf_0 = cnf_1.clauses[0]
                cnf_list = cnf_2.clauses
                if (cnf_independent(cnf_0, cnf_list)):
                    if (cnf_independent(cnf_0, cnf_list)):
                        return lifted_inference(cnf_2) * lifted_inference(cnf_1)
            var = cnf.get_separator()
            if (var == None):
                return 0
            else:
                val_domain = get_val_domain(var, cnf.clauses[0].atoms[0])
                prob = 1
                for i in val_domain:
                    cnf__1 = cnf.deep_copy()
                    grounding(var, str(i), cnf__1)
                    prob = prob * lifted_inference(cnf__1)
                    return prob




def main():
    """
    Read database files and parse into a table dictionary with tableName, table key/value pair
    """
    filenames = ['table_file_3.txt', 'table_file_1.txt', 'table_file_2.txt']
    table_dict = {}
    for dbfile in filenames:
        t = parser.pdbTable('./db/' + dbfile)
        table_dict[t.table_name] = t

    parsed_query = parser.parse_query('./db/query.txt')
    cnf = CNF()
    for q in parsed_query:
        cnf.addClause(Clause(q, table_dict))
    # cnf1 = CNF()

    # cnf1.addClause(Clause(parsed_query[0], table_dict))

    # cnf2 = CNF()
    # cnf2.addClause(Clause(parsed_query[1], table_dict))


    print(1 - lifted_inference(cnf))

if __name__ == "__main__":
    main()
