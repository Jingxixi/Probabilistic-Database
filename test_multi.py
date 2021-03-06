# Example R(x1)
# Input: ['R', ['x1']]
import parser
import copy
import multiprocessing
import time
import multiprocessing
import time

class Node:
    def __init__(self, atom):
        self.atom = atom
        self.neighbors = []

    def addNeighbor(self, atom2):
        self.neighbors.append(atom2)


class CNF:
    def __init__(self):
        self.clauses = []

    def is_independent(self, cnf2):
        for clause1 in self.clauses:
            for clause2 in cnf2.clauses:
                if not clause1.is_independent(clause2):
                    return False
        return True

    def addClause(self, clause):
        self.clauses.append(clause)

    def isClause(self):
        return len(self.clauses) == 1

    def mergeCNF(self, CNF2):
        res = CNF()
        for clause in self.clauses:
            res.addClause(clause)
        for clause in CNF2.clauses:
            res.addClause(clause)
        return res

    def get_separator(self):
        sep_var = ''
        if self.isClause() and len(self.clauses[0].atoms) == 1:
            atom = self.clauses[0].atoms[0]
            for variable in atom.variables:
                if not variable.isnumeric():
                    sep_var = variable[0]
                    self.clauses[0].variables.remove(variable)
                    break
            return sep_var
        for clause in self.clauses:
            for atom in clause.atoms:
                if len(atom.variables) == 1 and not atom.variables[0].isnumeric():
                    var = atom.variables[0]
                    sep_var = var[0]
                    break
        if sep_var == '':
            return None

        for clause in self.clauses:
            for atom in clause.atoms:
                found = False
                for var in atom.variables:
                    if var[0] == sep_var:
                        found = True
                        break
                if not found:
                    return None
        for clause in self.clauses:
            clause.variables = set(filter(lambda x: x[0] != sep_var, clause.variables))
        return sep_var

    def deep_cooy(self):
        new_copy = CNF()
        for clause in self.clauses:
            new_clause = Clause()
            new_clause.relations = copy.deepcopy(clause.relations)
            new_clause.variables = copy.deepcopy(clause.variables)
            for atom in clause.atoms:
                new_atom = Atom()
                new_atom.table_dict = atom.table_dict
                new_atom.variables = copy.deepcopy(atom.variables)
                new_atom.negation = atom.negation
                new_atom.name = atom.name
                new_clause.addAtom(new_atom)
            new_copy.addClause(new_clause)
        return new_copy


class UCNF:
    def __init__(self):
        self.cnfs = []

    def add_cnf(self, cnf):
        self.cnfs.append(cnf)


class Atom:
    def __init__(self, parsed_atom=[], table_dict=None):
        if len(parsed_atom) == 3:
            self.name = parsed_atom[0]
            self.variables = parsed_atom[1]
            self.negation = parsed_atom[2]
        self.table_dict = table_dict

    def is_connected(self, atom2):
        atom1_set = set()
        for var in self.variables:
            if not var.isnumeric():
                atom1_set.add(var)

        atom2_set = set()
        for var in atom2.variables:
            if not var.isnumeric():
                atom2_set.add(var)

        return len(atom1_set.intersection(atom2_set)) > 0

    def get_value(self):
        t = self.table_dict[self.name]
        query = []
        for num in self.variables:
            if not num.isnumeric():
                return 0
            query.append(int(num))
        if not self.negation:
            return (1.0 - t.getProb(query))
        else:
            return t.getProb(query)

    def is_independent(self, atom2):
        atom1_var = set()
        atom2_var = set()
        for var in self.variables:
            if not var.isnumeric():
                atom1_var.add(var)

        for var in atom2.variables:
            if not var.isnumeric():
                atom2_var.add(var)

        if self.name == atom2.name and atom1_var != atom2_var:
            return False
        if self.name != atom2.name:
            if atom1_var == atom2_var:
                return True
            if len(atom1_var.intersection(atom2_var)) != 0:
                return False
            else:
                return True
        return True


# Example /forall x1 /forall x2 R(x1) conjunnction S(x1,y1)
# Input: [['R', ['x1']], ['S', ['x1', 'y1']]]

class Clause:
    def __init__(self, parsed_clause=[], table_dict={}):
        self.atoms = []
        self.variables = set()
        self.relations = set()
        for i in range(len(parsed_clause)):
            self.atoms.append(Atom(parsed_clause[i], table_dict))
        for a in self.atoms:
            self.variables.update(a.variables)
            self.relations.update(a.name)

    def addAtom(self, atom):
        self.atoms.append(atom)

    def print(self):
        print("This Clause contains the following atoms:")
        for a in self.atoms:
            print("Table name is ", a.name, " and variables contain", a.variables)
        print("This clause has universal quatifier for variable:", self.variables)

    def is_independent(self, clause2):
        for atom1 in self.atoms:
            for atom2 in clause2.atoms:
                if not atom1.is_independent(atom2):
                    return False
        return True

    def getUCNF(self):
        ucnf = UCNF()
        if len(self.atoms) == 1:
            cnf = CNF()
            cnf.addClause(self)
            ucnf.add_cnf(cnf)
            return ucnf

        graph = {}
        for i in range(len(self.atoms)):
            atom1 = self.atoms[i]
            for j in range(i + 1, len(self.atoms)):
                atom2 = self.atoms[j]
                if atom1 not in graph:
                    graph[atom1] = Node(atom1)
                if atom2 not in graph:
                    graph[atom2] = Node(atom2)
                # for atom1 in self.atoms:
                #     for atom2 in self.atoms:
                if not atom1.is_connected(atom2):
                    continue

                graph[atom1].addNeighbor(graph[atom2])
                graph[atom2].addNeighbor(graph[atom1])

        visited = set()
        for key in graph:
            node = graph[key]
            if node in visited:
                continue
            newClause = Clause()
            dfs(node, newClause, visited)
            for atom in newClause.atoms:
                for item in atom.variables:
                    if not item.isnumeric():
                        newClause.variables.add(item)
                newClause.relations.add(atom.name)
            cnf = CNF()
            cnf.addClause(newClause)
            ucnf.add_cnf(cnf)
        return ucnf


def dfs(node, newClause, visited):
    if node in visited:
        return
    visited.add(node)
    newClause.addAtom(node.atom)
    for neighbor in node.neighbors:
        dfs(neighbor, newClause, visited)

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
def lifted_inference_single(cnf):
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
            prob1 = lifted_inference_single(cnf1)
            prob2 = lifted_inference_single(cnf2)
            return 1 - (1 - prob1) * (1 - prob2)
        else:
            cnf1 = ucnf.cnfs[0].deep_cooy()
            cnf2 = ucnf.cnfs[1].deep_cooy()
            cnf12 = cnf1.mergeCNF(cnf2)

            return lifted_inference_single(cnf1) + lifted_inference_single(cnf2) - lifted_inference_single(cnf12)

    

    if (len(cnf.clauses) == 2):
        if (cnf.clauses[0].is_independent(cnf.clauses[1])):
            cnf1 = cnf()
            cnf2 = cnf()
            cnf1.addClause(cnf.clauses[0])
            cnf2.addClause(cnf.clauses[1])
            return lifted_inference_single(cnf1)*lifted_inference_single(cnf2)
    var = cnf.get_separator()
    if (var == "None"):
        return 0
    else:
        val_domain = get_val_domain(var, cnf.clauses[0].atoms[0])
        prob = 1

        for i in val_domain:
            cnf1 = cnf.deep_cooy()
            grounding(var, str(i), cnf1)
            prob = prob * lifted_inference_single(cnf1)
        return prob

def lifted_inference(cnf, level, shared_mem, pNum):
    print('here')
    if (cnf.isClause()):
        clause = cnf.clauses[0]
        if len(clause.atoms) == 1:
            if (len(clause.variables)) == 0:
                prob = clause.atoms[0].get_value()
                shared_mem[str(level)+'/'+str(pNum)] = prob
                return prob
    ucnf = ConverttoUCNF(cnf)
    if (len(ucnf.cnfs) == 2):
        if (ucnf.cnfs[0].is_independent(ucnf.cnfs[1])):
            cnf1 = ucnf.cnfs[0].deep_cooy()
            cnf2 = ucnf.cnfs[1].deep_cooy()
            p1 = multiprocessing.Process(target=lifted_inference, args=(cnf1,level+1, shared_mem, pNum+1))
            p1.start()
            p2 = multiprocessing.Process(target=lifted_inference, args=(cnf2,level+1, shared_mem, pNum+2))
            p2.start()
            p1.join()
            p2.join()
            prob1 = shared_mem[str(level+1)+'/'+str(pNum+1)]
            prob2 = shared_mem[str(level+1)+'/'+str(pNum+2)]
            res = 1 - (1 - prob1) * (1 - prob2)
            shared_mem[str(level)+'/'+str(pNum)] = res
            return res
        else:
            cnf1 = ucnf.cnfs[0].deep_cooy()
            cnf2 = ucnf.cnfs[1].deep_cooy()
            cnf12 = cnf1.mergeCNF(cnf2)
            p1 = multiprocessing.Process(target=lifted_inference, args=(cnf1,level+1, shared_mem, pNum+1))
            p1.start()
            p2 = multiprocessing.Process(target=lifted_inference, args=(cnf2,level+1, shared_mem, pNum+2))
            p2.start()
            p12 = multiprocessing.Process(target=lifted_inference, args=(cnf12,level+1, shared_mem, pNum+3))
            p12.start()
            p1.join()
            p2.join()
            p12.join()
            prob1 = shared_mem[str(level+1)+'/'+str(pNum+1)]
            prob2 = shared_mem[str(level+1)+'/'+str(pNum+2)]
            prob12 = shared_mem[str(level+1)+'/'+str(pNum+3)]
            res = prob1 + prob2 - prob12
            shared_mem[str(level)+'/'+ str(pNum)] = res
            return res

    

    if (len(cnf.clauses) == 2):
        if (cnf.clauses[0].is_independent(cnf.clauses[1])):
            cnf1 = cnf()
            cnf2 = cnf()
            cnf1.addClause(cnf.clauses[0])
            cnf2.addClause(cnf.clauses[1])
            p1 = multiprocessing.Process(target=lifted_inference, args=(cnf1,level+1, shared_mem, pNum+1))
            p1.start()
            p2 = multiprocessing.Process(target=lifted_inference, args=(cnf2,level+1, shared_mem, pNum+2))
            p2.start()
            p1.join()
            p2.join()
            prob1 = shared_mem[str(level+1)+'/'+str(pNum+1)]
            prob2 = shared_mem[str(level+1)+'/'+str(pNum+2)]
            res = prob1*prob2
            shared_mem[str(level)+'/'+ str(pNum)] = res
            return res
    var = cnf.get_separator()
    if (var == "None"):
        return 0
    else:
        val_domain = get_val_domain(var, cnf.clauses[0].atoms[0])
        prob = 1
        num = pNum
        for i in val_domain:
            cnf1 = cnf.deep_cooy()
            grounding(var, str(i), cnf1)
            num +=1
            prob1 = lifted_inference_single(cnf1)
            prob = prob * prob1
        shared_mem[str(level)+'/'+ str(pNum)] = prob
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
    shared_mem = dict()
    start = time.time()
    res = lifted_inference_single(cnf)

    end = time.time()
    print(end - start)

    print("Running multi-processing")
    start = time.time()
    res = lifted_inference(cnf,0,shared_mem , 1)
    end = time.time()
    print(end - start)
if __name__ == "__main__":
    main()
