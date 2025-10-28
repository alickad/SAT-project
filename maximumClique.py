import subprocess
from argparse import ArgumentParser


def vertexAtomicNumber(v):
    # atomic formulas representing "vertex v is a part of chosen clique"
    return v+1
def edgeAtomicNumber(e1, e2):
    # atomic formulas representing "there is an edge between e1 and e2"
    if (e1 > e2):
        e1, e2 = e2, e1
    return (V + 1) + 1 + V*e1 + e2
def seqCounterNumber(i,j):
    # atomic formulas representing "from first i vertices, at least j are in a clique"
    return (V+1) + V*V + 1 + V*i + j

def inputParser(input_file_name):
    with open(input_file_name, "r") as file:
        for line in file:
            lineList = line.split()
            if (lineList[0] == "c"): continue
            elif lineList[0] == "p" and (lineList[1] == "edge" or lineList[1] == "col"):
                V = int(lineList[2])
                E = int(lineList[3])
                adjacencyMatrix = [[0] * V] * V
                #print(V, E)
                
            elif lineList[0] == "e":
                v1, v2 = int(lineList[1]), int(lineList[2])
                v1 -= 1
                v2 -= 1
                adjacencyMatrix[v1][v2] = 1
                adjacencyMatrix[v2][v1] = 1
            else: 
                #print("WRONG INPUT")
                exit(0)
    return V, E, adjacencyMatrix

def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    #print(cnf)
    # print CNF into formula.cnf in DIMACS format
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + '\n') # maybe 0 at the end??

    # call the solver and return the output
    return subprocess.run(['./' + solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)


def graphLogic():
    temp_cnf = []
    # add formulas representing edges
    for i in range(V):
        for j in range(V):
            if adjacencyMatrix[i][j]: temp_cnf.append([edgeAtomicNumber(i,j)])
            else: temp_cnf.append([- edgeAtomicNumber(i,j)])

    # add formulas representing vertices in cliques
    # v_1 && v_2 -> e_1,2
    # not v_1 or not v_2 or e_1,2
    for v1 in range(V):
        for v2 in range(V):
            if v1 == v2: continue
            temp_cnf.append( [-vertexAtomicNumber(v1), -vertexAtomicNumber(v2), edgeAtomicNumber(v1,v2)])
 
    return temp_cnf

# now lets binary search the solution with most "vertex atomic formulas" getting true
# can we find solution with at least k trues?
# we will use sequential counter for that

def counterLogic():
    temp_cnf = []
    # if in first i are at least j true, then in first i+1 are also at least j true
    # s_i,j -> s_i+1,j
    # not s_i,j or s_i+1,j
    for i in range(V - 1):
        for j in range(V):
            temp_cnf.append([-seqCounterNumber(i,j), seqCounterNumber(i+1,j)])

    # s_1,1 <-> v
    # (s_1,1 or not v) and (x or not s_1,1)
    temp_cnf.append([seqCounterNumber(0,0), -vertexAtomicNumber(0)])
    temp_cnf.append([-seqCounterNumber(0,0), vertexAtomicNumber(0)])
    # if vertex v is in clique, then increment
    # (v and s_v-1,j) -> s_v,j+1
    # not v or not s_v-1,j or s_v,j+1
    for v in range(1, V):
        for j in range(V-1):
            temp_cnf.append([-vertexAtomicNumber(v), -seqCounterNumber(v-1, j), seqCounterNumber(v, j+1)])

    return temp_cnf

def getCliqueVertices(result):
    # parse the model from the output of the solver
    # the model starts with 'v'
    model = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if line.startswith("v"):    # there might be more lines of the model, each starting with 'v'
            vars = line.split(" ")
            vars.remove("v")
            model.extend(int(v) for v in vars)      
    model.remove(0) # 0 is the end of the model, just ignore it
    clique = []
    for m in model:
        if (abs(m) <= V and m > 0): clique.append(m)

    return clique


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help=(
            "The instance file."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-4.2.1/sources/simp/glucose",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    args = parser.parse_args()

    # get the input instance
    V, E, adjacencyMatrix = inputParser(args.input)

    nr_vars = V + 2*V*V + 1
    #print(nr_vars)

    cnf = []
    cnf.extend(graphLogic())
    cnf.extend(counterLogic())
    print(cnf)
    exit(0)

    # now we just binary search the biggest possible amount of verteces in cliques
    smallEnd = 0
    b = 1
    while b*2 < V: b *= 2
    while b > 0:
        k = smallEnd + b
        cnf.append([seqCounterNumber(V-1, k)])
        # TODO: solve cnf
        # if solution: smallEnd = k
        result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)
        if result.returncode == 10: smallEnd = k
        cnf.pop()
    b //= 2

    # now we know the max clique has size smallEnd
    # we run the  SAT solver one last time to get the vertices of the clique
    cnf.append(seqCounterNumber(V-1, smallEnd))
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)
    # print results
    print("THE MAXIMUM CLIQUE HAS SIZE ", smallEnd, '\n')
    print("the following vertices form a clique of size ", smallEnd, ":")
    clique = getCliqueVertices(result)
    print(" ".join(clique))
    
    