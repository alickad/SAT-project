import subprocess

V = 0
E = 0
adjacencyMatrix = []


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

def inputParser():
    inputString = ""
    while inputString:
        inputString = input()
        inputList = inputString.split()
        if (inputList[0] == "c"): continue
        elif inputList[0] == "p" and (inputList[1] == "edge" or inputList[1] == "col"):
            V = int(inputList[2])
            E = int(inputList[3])
            adjacencyMatrix = [[0] * V] * V
            
        elif inputList[0] == "e":
            v1, v2 = int(inputList[1]), int(inputList[2])
            adjacencyMatrix[v1][v2] = 1
            adjacencyMatrix[v2][v1] = 1
        else: 
            print("WRONG INPUT")
            exit(0)


inputParser()
cnf = []

# add formulas representing edges
for i in range(V):
    for j in range(V):
        if adjacencyMatrix[i][j]: cnf.append(edgeAtomicNumber(i,j))
        else: cnf.append( (- edgeAtomicNumber(i,j)))

# add formulas representing vertices in cliques
# v_1 && v_2 -> e_1,2
# not v_1 or not v_2 or e_1,2
for v1 in range(V):
    for v2 in range(V):
        if v1 == v2: continue
        cnf.append( (-vertexAtomicNumber(v1), -vertexAtomicNumber(v2), edgeAtomicNumber(v1,v2)))

# now lets binary search the solution with most "vertex atomic formulas" getting true
# can we find solution with at least k trues?
# we will use sequential counter for that

# if in first i are at least j true, then in first i+1 are also at least j true
# s_i,j -> s_i+1,j
# not s_i,j or s_i+1,j
for i in range(V - 1):
    for j in range(V):
        cnf.append((-seqCounterNumber(i,j), seqCounterNumber(i+1,j)))

# s_1,1 <-> v
# (s_1,1 or not v) and (x or not s_1,1)
cnf.append((seqCounterNumber(0,0), -vertexAtomicNumber(0)))
cnf.append((-seqCounterNumber(0,0), vertexAtomicNumber(0)))
# if vertex v is in clique, then increment
# (v and s_v-1,j) -> s_v,j+1
# not v or not s_v-1,j or s_v,j+1
for v in range(1, V):
    for j in range(V-1):
        cnf.append(-vertexAtomicNumber(v), -seqCounterNumber(v-1, j), seqCounterNumber(v, j+1))

# now we just binary search the biggest possible amount of verteces in cliques
smallEnd = 0
b = (V + 1) // 2
while b > 0:
    k = smallEnd + b
    


    b //= 2



    







