from calculate import *
from graphs import plot_bridge

nodes, top_nodes, bottom_nodes = generate_standard_truss(10,3,50)
# print(nodes)
plot_bridge(nodes, y_bounds=[bottom_nodes[0].y,top_nodes[0].y])