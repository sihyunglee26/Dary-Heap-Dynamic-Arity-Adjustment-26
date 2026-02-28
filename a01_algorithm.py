'''
Authored by Sihyung Lee
'''
from pathlib import Path    # to access the current directory

class DirectedEdge:
    def __init__(self, v, w, weight): # Create an edge v->w with a double-type weight
        self.v, self.w, self.weight = v, w, weight
    
    def __lt__(self, other): # < operator, used to sort elements (e.g., in a PriorityQueue, sorted() function)
        assert(isinstance(other, DirectedEdge))
        return self.weight < other.weight

    def __gt__(self, other): # > operator, used to sort elements
        assert(isinstance(other, DirectedEdge))
        return self.weight > other.weight

    def __eq__(self, other): # == operator, used to compare edges for grading
        if other == None: return False
        assert(isinstance(other, DirectedEdge))
        return self.v == other.v and self.w == other.w and self.weight == other.weight

    def __str__(self): # Called when an Edge instance is printed (e.g., print(e))
        return f"{self.v}->{self.w} ({self.weight})"

    def __repr__(self): # Called when an Edge instance is printed as an element of a list
        return self.__str__() 
    

class EdgeWeightedDigraph:
    def __init__(self, V): # Constructor
        self.V = V # Number of vertices
        self.E = 0 # Number of edges
        self.adj = [[] for _ in range(V)]   # adj[v] is a list of vertices adjacent to v
        self.edges = []

    def addEdge(self, v, w, weight): # Add edge v->w. Self-loops and parallel edges are allowed
        e = DirectedEdge(v, w, weight) # Create one edge instance and use it for adj[v], adj[w], and edges[]
        self.adj[v].append(e)        
        self.edges.append(e)
        self.E += 1
    
    def outDegree(self, v):
        return len(self.adj[v])

    def __str__(self):
        rtList = [f"{self.V} vertices and {self.E} edges\n"]
        for v in range(self.V):
            for e in self.adj[v]: rtList.append(f"{e}\n")
        return "".join(rtList)

    def negate(self): # return an EdgeWeightedDigraph with all edge weights negated
        g = EdgeWeightedDigraph(self.V)
        for e in self.edges: g.addEdge(e.v, e.w, -e.weight)
        return g

    def reverse(self): # return an EdgeWeightedDigraph with all edges reversed
        g = EdgeWeightedDigraph(self.V)
        for e in self.edges: g.addEdge(e.w, e.v, e.weight)
        return g

    '''
    Create an EdgeWeightedDigraph from a file
        fileName: Name of the file that contains graph information as follows:
            (1) the number of vertices, followed by
            (2) one edge in each line, where an edge v->w with weight is represented by "v w weight"
            e.g., the following file represents a digraph with 3 vertices and 2 edges
            3
            0 1 0.12
            2 0 0.26
        The file needs to be in the same directory as the current .py file
    '''
    @staticmethod
    def fromFile(fileName):
        filePath = Path(__file__).with_name(fileName)   # Use the location of the current .py file   
        with filePath.open('r') as f:
            phase = 0
            line = f.readline().strip() # Read a line, while removing preceding and trailing whitespaces
            while line:                                
                if len(line) > 0:
                    if phase == 0: # Read V, the number of vertices
                        g = EdgeWeightedDigraph(int(line))
                        phase = 1
                    elif phase == 1: # Read edges
                        edge = line.split()
                        if len(edge) != 3: raise Exception(f"Invalid edge format found in {line}")
                        g.addEdge(int(edge[0]), int(edge[1]), float(edge[2]))                        
                line = f.readline().strip()
        return g
    

'''
Class that finds and stores shortest paths from a single source
This calss serves as a parent of DijkstraSP class 
'''
class SP:
    def __init__(self, g, s): # Find shortest paths from s in graph g
        if not isinstance(g, EdgeWeightedDigraph): raise Exception(f"{g} is not an EdgeWeightedDigraph")
        self.g, self.s = g, s
        self.validateVertex(s)        
        self.edgeTo = [None] * g.V # edgeTo[w]: last edge on the shortest known path to w
        self.distTo = [float('inf')] * g.V  # distTo[w]: shortest known distance to w
        self.distTo[s] = 0

    def pathTo(self, v):
        self.validateVertex(v)
        if not self.hasPathTo(v): raise Exception(f"no path exists to vertex {v}")
        path = []
        e = self.edgeTo[v]
        while e != None:
            path.append(e)
            e = self.edgeTo[e.v]
        path.reverse()
        return path

    def hasPathTo(self, v):
        self.validateVertex(v)
        return self.distTo[v] < float('inf')

    # If e=v->w gives a shorter path to w through v
    #   update distTo[w] and edgeTo[w]
    def relax(self, e):
        assert(isinstance(e, DirectedEdge))        
        if self.distTo[e.w] > self.distTo[e.v] +  e.weight:
            self.distTo[e.w] = self.distTo[e.v] +  e.weight
            self.edgeTo[e.w] = e

    def validateVertex(self, v):
        if v<0 or v>=self.g.V: raise Exception(f"vertex {v} is not between 0 and {self.g.V-1}")


class DijkstraSP(SP): # Inherit SP class
    def __init__(self, g, s, pq):
        super().__init__(g, s) # run the constructor of the parent class
        self.pq = pq
        self.pq.insert(s, 0) # insert (source vertex id, distance)
        self.closed = [False] * g.V
        while not self.pq.is_empty():
            # select vertices in order of distance from s
            dist, v = self.pq.delete_min()
            self.closed[v] = True            
            for e in self.g.adj[v]:
                if not self.closed[e.w]: self.relax(e)

    def relax(self, e):
        assert(isinstance(e, DirectedEdge))        
        if self.distTo[e.w] > self.distTo[e.v] +  e.weight:
            self.distTo[e.w] = self.distTo[e.v] +  e.weight
            self.edgeTo[e.w] = e
            if self.pq.contains(e.w): self.pq.decrease_key(e.w, self.distTo[e.w])
            else: self.pq.insert(e.w, self.distTo[e.w])


'''
Class for storing weighted undirected edges
'''
class Edge:
    def __init__(self, v, w, weight): # Create an edge v-w with a double weight
        if v <= w: self.v, self.w = v, w  # Put the lesser number in v for convenience
        else: self.v, self.w = w, v        
        self.weight = weight
    
    def __lt__(self, other): # < operator, used to sort elements (e.g., in a PriorityQueue, sorted() function)
        assert(isinstance(other, Edge))
        return self.weight < other.weight

    def __gt__(self, other): # > operator, used to sort elements
        assert(isinstance(other, Edge))
        return self.weight > other.weight

    def __eq__(self, other): # == operator, used to compare edges for grading
        assert(isinstance(other, Edge))
        return self.v == other.v and self.w == other.w and self.weight == other.weight

    def __str__(self): # Called when an Edge instance is printed (e.g., print(e))
        return f"{self.v}-{self.w} ({self.weight})"

    def __repr__(self): # Called when an Edge instance is printed as an element of a list
        return self.__str__()

    def other(self, v): # Return the vertex on the Edge other than v
        if self.v == v: return self.w
        else: return self.v


'''
Class for storing WUGraphs (Weighted Undirected Graphs)
'''
class WUGraph:
    def __init__(self, V): # Constructor
        self.V = V # Number of vertices
        self.E = 0 # Number of edges
        self.adj = [[] for _ in range(V)]   # adj[v] is a list of vertices adjacent to v
        self.edges = []

    def addEdge(self, v, w, weight): # Add edge v-w. Self-loops and parallel edges are allowed
        e = Edge(v, w, weight) # Create one edge instance and use it for adj[v], adj[w], and edges[]
        self.adj[v].append(e)
        self.adj[w].append(e)
        self.edges.append(e)
        self.E += 1

    def degree(self, v):
        return len(self.adj[v])

    def __str__(self):
        rtList = [f"{self.V} vertices and {self.E} edges\n"]
        for v in range(self.V):
            for e in self.adj[v]:
                if v == e.v: rtList.append(f"{e}\n") # Do not print the same edge twice
        return "".join(rtList)

    '''
    Create a WUGraph instance from a file
        fileName: Name of the file that contains graph information as follows:
            (1) the number of vertices, followed by
            (2) one edge in each line, where an edge v-w with weight is represented by "v w weight"
            e.g., the following file represents a digraph with 3 vertices and 2 edges
            3
            0 1 0.12
            2 0 0.26
        The file needs to be in the same directory as the current .py file
    '''
    @staticmethod
    def fromFile(fileName):
        filePath = Path(__file__).with_name(fileName)   # Use the location of the current .py file   
        with filePath.open('r') as f:
            phase = 0
            line = f.readline().strip() # Read a line, while removing preceding and trailing whitespaces
            while line:                                
                if len(line) > 0:
                    if phase == 0: # Read V, the number of vertices
                        g = WUGraph(int(line))
                        phase = 1
                    elif phase == 1: # Read edges
                        edge = line.split()
                        if len(edge) != 3: raise Exception(f"Invalid edge format found in {line}")
                        g.addEdge(int(edge[0]), int(edge[1]), float(edge[2]))                        
                line = f.readline().strip()
        return g


'''
Find an MST (Minimum Spanning Tree) using Prim's algorithm (eager version)
    and return the MST with its weight sum
'''
def mstPrimEager(g, pq):
    def include(v):
        included[v] = True
        for e in g.adj[v]:
            w = e.other(v)
            if not included[w]:
                if not pq.contains(w): pq.insert(w, e)
                elif e < pq.key_of(w): pq.decrease_key(w, e)

    assert(isinstance(g, WUGraph))

    edgesInMST = [] # Stores edges selected as part of the MST
    included = [False] * g.V # included[v] == True if v is in the MST
    weightSum = 0  # Sum of edge weights in the MST        
    include(0)

    while not pq.is_empty() and len(edgesInMST) < g.V-1:
        e, w = pq.delete_min()
        #print("connect to", w, "with edge", e)
        edgesInMST.append(e)
        weightSum += e.weight
        include(w)        

    return edgesInMST, weightSum


class FlowEdge:
    def __init__(self, v, w, capacity): # Create an edge v->w with a double capacity
        assert isinstance(v, int) and isinstance(w, int), f"v({v}) and/or w({w}) are not integers"
        assert v>=0 and w>=0, f"Vertices {v} and/or {w} have negative IDs"
        assert isinstance(capacity, int) or isinstance(capacity, float), f"Capacity {capacity} is neither an integer nor a floating-point number"
        assert capacity>=0, f"Edge capacity {capacity} must be >= 0"
        self.v, self.w, self.capacity = v, w, capacity
        self.flow = 0.0 # Initialize flow to 0
    
    def __lt__(self, other): # < operator, used to sort elements (e.g., in a PriorityQueue, sorted() function)
        self.validateInstance(other)
        return self.capacity < other.capacity

    def __gt__(self, other): # > operator, used to sort elements
        self.validateInstance(other)
        return self.capacity > other.capacity

    def __eq__(self, other): # == operator, used to compare edges for grading
        if other == None: return False
        self.validateInstance(other)
        return self.v == other.v and self.w == other.w and self.capacity == other.capacity

    def __str__(self): # Called when an Edge instance is printed (e.g., print(e))
        return f"{self.v}->{self.w} ({self.flow}/{self.capacity})"

    def __repr__(self): # Called when an Edge instance is printed as an element of a list
        return self.__str__()

    def other(self, vertex): # Return the vertex on the Edge other than vertex        
        if vertex == self.v: return self.w
        elif vertex == self.w: return self.v
        else: self.invalidIndex(vertex)

    def remainingCapacityTo(self, vertex): # Remaining capacity toward vertex
        if vertex == self.v: return self.flow
        elif vertex == self.w: return self.capacity - self.flow
        else: self.invalidIndex(vertex)
    
    def addRemainingFlowTo(self, vertex, delta): # Add delta flow toward vertex     
        assert isinstance(delta, int) or isinstance(delta, float), f"Delta {delta} is neither an integer nor a floating-point number"
        assert delta <= self.remainingCapacityTo(vertex), f"Delta {delta} is greater than the remaining capacity {self.remainingCapacity(vertex)}"        
        if vertex == self.v: self.flow -= delta
        elif vertex == self.w: self.flow += delta
        else: self.invalidIndex(vertex)

    def invalidIndex(self, i):
        assert False, f"Illegal endpoint {i}, which is neither of the two end points {self.v} and {self.w}"

    @staticmethod
    def validateInstance(e):
        assert isinstance(e, FlowEdge), f"e={e} is not an instance of FlowEdge"


'''
Class that represents Digraphs with Flow/Capacity
'''
class FlowNetwork:
    def __init__(self, V): # Constructor
        assert isinstance(V, int) and V >= 0, f"V({V}) is not an integer >= 0"
        self.V = V # Number of vertices
        self.E = 0 # Number of edges
        self.adj = [[] for _ in range(V)]   # adj[v] is a list of vertices adjacent to v
        self.edges = []

    def addEdge(self, e): # Add edge v-w. Self-loops and parallel edges are allowed
        FlowEdge.validateInstance(e)
        assert 0<=e.v and e.v<self.V and 0<=e.w and e.w<self.V, f"Edge endpoints ({e.v},{e.w}) are out of the range 0 to {self.V-1}"
        self.adj[e.v].append(e) # Add forward edge
        self.adj[e.w].append(e) # Add backward edge
        self.edges.append(e)
        self.E += 1

    def __str__(self):
        rtList = [f"{self.V} vertices and {self.E} edges\n"]
        for v in range(self.V):
            for e in self.adj[v]: 
                if e.v == v: rtList.append(f"{e}\n") # Show only forward edges to not show the same edge twice
        return "".join(rtList)

    def copy(self):
        fn = FlowNetwork(self.V)
        for e in self.edges: fn.addEdge(FlowEdge(e.v, e.w, e.capacity))
        return fn

    '''
    Create an FlowNetwork from a file
        fileName: Name of the file that contains graph information as follows:
            (1) the number of vertices, followed by
            (2) one edge in each line, where an edge v->w with capacity is represented by "v w capacity"
            e.g., the following file represents a digraph with 3 vertices and 2 edges
            3
            0 1 0.12
            2 0 0.26
        The file needs to be in the same directory as the current .py file
    '''
    @staticmethod
    def fromFile(fileName):
        filePath = Path(__file__).with_name(fileName)   # Use the location of the current .py file   
        with filePath.open('r') as f:
            phase = 0
            line = f.readline().strip() # Read a line, while removing preceding and trailing whitespaces
            while line:                                
                if len(line) > 0:
                    if phase == 0: # Read V, the number of vertices
                        g = FlowNetwork(int(line))
                        phase = 1
                    elif phase == 1: # Read edges
                        edge = line.split()
                        assert len(edge) == 3, f"Invalid edge format found in {line}"
                        if edge[2] == 'inf': g.addEdge(FlowEdge(int(edge[0]), int(edge[1]), float('inf')))                        
                        else: g.addEdge(FlowEdge(int(edge[0]), int(edge[1]), float(edge[2])))                        
                line = f.readline().strip()
        return g

    @staticmethod
    def validateInstance(g):
        assert isinstance(g, FlowNetwork), f"g={g} is not an instance of FlowNetwork"


def findAugmentingPathDijkstra(g, s, pq):
    def relax(e, v, w):
        newCapacity = min(capacityTo[v], e.remainingCapacityTo(w))
        if capacityTo[w] < newCapacity:
            capacityTo[w] = newCapacity
            edgeTo[w] = e
            if pq.contains(w): pq.decrease_key(w, -capacityTo[w])
            else: pq.insert(w, -capacityTo[w])
            
    FlowNetwork.validateInstance(g)
    g = g.copy() # Make a copy to not mutate original graph        

    # insert (source vertex id, capacity of path to s)
    # we negate capacity, as we use minPQ in place of maxPQ    
    pq.insert(s, float('-inf'))

    visited = [False] * g.V
    edgeTo = [None] * g.V
    capacityTo = [0] * g.V
    capacityTo[0] = float('inf')
    while not pq.is_empty():
        capacity, v = pq.delete_min()
        visited[v] = True
        for e in g.adj[v]:
            w = e.other(v)
            if not visited[w] and e.remainingCapacityTo(w) > 0: relax(e, v, w)

    return visited, edgeTo, capacityTo


if __name__ == "__main__":
    pass