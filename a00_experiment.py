'''
Authored by Sihyung Lee
'''
from a01_algorithm import EdgeWeightedDigraph, DijkstraSP, WUGraph, mstPrimEager, FlowNetwork, findAugmentingPathDijkstra
from a02_heap_arity_adjustable import DaryHeapBCD as BCD

if __name__ == "__main__":
    print(f"* Run Prim's algorithm for minimum spanning trees:")
    g = WUGraph.fromFile("road_network_seoul_v1356_e3225.txt")
    d_from, d_to, weight_on_current = 4, 2, 0.2

    pq = BCD(g.V, arity_adjustment_policy=-1, d_from=d_from, d_to=d_to, weight_on_current=weight_on_current)
    mstPrimEager(g, pq)
    print(f"Arity changes based on u/d ratio from {d_from} -> {pq.d}, # of comparisons: {pq.num_comparisons}")

    pq = BCD(g.V, arity_adjustment_policy=0, d_from=d_from, d_to=d_to, weight_on_current=weight_on_current)
    mstPrimEager(g, pq)
    print(f"Arity remains fixed, # of comparisons: {pq.num_comparisons}")        
    print()


    print(f"* Run Dijkstra's algorithm for shortest paths:")
    g = EdgeWeightedDigraph.fromFile("road_network_los_angeles_ca_v604_e1487.txt")
    d_from, d_to, weight_on_current = 4, 2, 0.2

    pq = BCD(g.V, arity_adjustment_policy=-1, d_from=d_from, d_to=d_to, weight_on_current=weight_on_current)
    DijkstraSP(g, 0, pq)
    print(f"Arity changes based on u/d ratio from {d_from} -> {pq.d}, # of comparisons: {pq.num_comparisons}")

    pq = BCD(g.V, arity_adjustment_policy=0, d_from=d_from, d_to=d_to, weight_on_current=weight_on_current)
    DijkstraSP(g, 0, pq)
    print(f"Arity remains fixed, # of comparisons: {pq.num_comparisons}")        
    print()
    

    print(f"* Run Ford Fulkerson's algorithm for fattest augmenting paths:")
    g = FlowNetwork.fromFile("computer_vision_super_res_e1_dtu_v10494_e62364.txt")
    d_from, d_to, weight_on_current = 4, 2, 0.2

    pq = BCD(g.V, arity_adjustment_policy=-1, d_from=d_from, d_to=d_to, weight_on_current=weight_on_current)
    findAugmentingPathDijkstra(g, 0, pq)
    print(f"Arity changes based on u/d ratio from {d_from} -> {pq.d}, # of comparisons: {pq.num_comparisons}")

    pq = BCD(g.V, arity_adjustment_policy=0, d_from=d_from, d_to=d_to, weight_on_current=weight_on_current)
    findAugmentingPathDijkstra(g, 0, pq)
    print(f"Arity remains fixed, # of comparisons: {pq.num_comparisons}")        
    print()
