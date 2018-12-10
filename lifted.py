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


def lifted_inference(cnf):
    if (cnf.isClause()):
        clause = cnf.clauses[0]
        if len(clause.atoms) == 1:
            if (len(clause.variables)) == 0:
                prob = clause.atoms[0].get_value()
                return prob
    ucnf = ConverttoUCNF(cnf)
    if (len(ucnf.cnfs) == 2):
        if (ucnf.cnfs[0].is_independent(ucnf.cnfs[1])):
            cnf1 = ucnf.cnfs[0].deep_cooy()
            cnf2 = ucnf.cnfs[1].deep_cooy()
            prob1 = lifted_inference(cnf1)
            prob2 = lifted_inference(cnf2)
            return 1 - (1 - prob1) * (1 - prob2)
        else:
            cnf1 = ucnf.cnfs[0].deep_cooy()
            cnf2 = ucnf.cnfs[1].deep_cooy()
            cnf12 = cnf1.mergeCNF(cnf2)

            return lifted_inference(cnf1) + lifted_inference(cnf2) - lifted_inference(cnf12)
    if (len(cnf.clauses) == 2):
        if (cnf.clauses[0].is_independent(cnf.clauses[1])):
            cnf1 = cnf()
            cnf2 = cnf()
            cnf1.addClause(cnf.clauses[0])
            cnf2.addClause(cnf.clauses[1])
            return lifted_inference(cnf1)*lifted_inference(cnf2)
    var = cnf.get_separator()
    if (var == "None"):
        return 0
    else:
        val_domain = get_val_domain(var, cnf.clauses[0].atoms[0])
        prob = 1

        for i in val_domain:
            cnf1 = cnf.deep_cooy()
            grounding(var, str(i), cnf1)
            prob = prob * lifted_inference(cnf1)
        return prob
