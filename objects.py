# Example R(x1)
# Input: ['R', ['x1']]
import parser
import copy


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
        new_clause = clause.deep_copy()
        self.clauses.append(new_clause)
        #self.clauses.append(clause)

    def isClause(self):
        return len(self.clauses) == 1

    def mergeCNF(self, CNF2):
        res = CNF()
        cnf1 = self.deep_copy()
        cnf2 = CNF2.deep_copy()
        for clause in cnf1.clauses: #self.clauses:
            res.addClause(clause)
        for clause in cnf2.clauses: #CNF2.clauses:
            res.addClause(clause)

        return res

    def rewrite(self):
        if len(self.clauses) == 0:
            return
        clause = self.clauses[0]
        big_var = None
        not_found = False
        for clause in self.clauses:
            for variable in clause.variables:
                if variable.isnumeric():
                    continue
                if big_var == None:
                    big_var = variable[0]
                if big_var != variable[0]:
                    not_found = True
                    break
            if not_found:
                break
        if not not_found:
            for clause in self.clauses:
                temp = set([elem for elem in clause.variables if elem[0] != big_var])
                if temp != clause.variables:
                    clause.variables = temp
                    clause.variables.add(big_var)
                for atom in clause.atoms:
                    for i in range(len(atom.variables)):
                        if atom.variables[i][0] == big_var:
                            atom.variables[i] = big_var
        new_list = []

        for i in range(len(self.clauses)):
            found = False
            if len(new_list) == 0:
                new_list.append(self.clauses[i])
            for j in range(len(new_list)):
                if new_list[j].is_equal(self.clauses[i]):
                    found = True
                    break
            if not found:
                new_list.append(self.clauses[i])

        self.clauses = new_list

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

    def deep_copy(self):
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

    def is_equal(self, atom2):
        if self.name != atom2.name:
            return False
        if self.negation != atom2.negation:
            return False
        if len(self.variables) != len(atom2.variables):
            return False

        for i in range(len(self.variables)):
            if self.variables[i] != atom2.variables[i]:
                return False
        return True

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

        if self.name == atom2.name:
            return False
        if self.name != atom2.name:
            if atom1_var == atom2_var and len(atom1_var) != 0:
                return False
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

    def is_equal(self, clause2):
        if self.variables != clause2.variables:
            return False
        if self.relations != clause2.relations:
            return False
        if len(self.atoms) != len(clause2.atoms):
            return False

        self.atoms.sort(key=lambda x: x.name)
        clause2.atoms.sort(key=lambda x: x.name)
        for i in range(len(self.atoms)):
            if not self.atoms[i].is_equal(clause2.atoms[i]):
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

    def deep_copy(self):
        new_clause = Clause()
        new_clause.relations = copy.deepcopy(self.relations)
        new_clause.variables = copy.deepcopy(self.variables)
        for atom in self.atoms:
            new_atom = Atom()
            new_atom.table_dict = atom.table_dict
            new_atom.variables = copy.deepcopy(atom.variables)
            new_atom.negation = atom.negation
            new_atom.name = atom.name
            new_clause.addAtom(new_atom)
        return new_clause

def dfs(node, newClause, visited):
    if node in visited:
        return
    visited.add(node)
    newClause.addAtom(node.atom)
    for neighbor in node.neighbors:
        dfs(neighbor, newClause, visited)



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
    cnf1 = CNF()
    cnf1.addClause(Clause(parsed_query[0], table_dict))

    # print(cnf1.clauses[0].is_independent(cnf1.clauses[1]))
    # var = cnf1.clauses[0].getUCNF()
    cnf2 = CNF()
    #cnf1.addClause(Clause(parsed_query[1], table_dict))

    clause1 = Clause()
    clause2 = Clause()

    clause1.addAtom(cnf1.clauses[0].atoms[0])
    clause2.addAtom(cnf1.clauses[0].atoms[1])

    clause1.variables = set()
    clause2.variables = set()

    if (clause1.is_independent(clause2)):
        print("independent")
    #print(cnf1.is_independent(cnf2))


if __name__ == "__main__":
    main()
