from calculate import *
from graphs import *

nodes, top_nodes, bottom_nodes = generate_standard_truss(7, 3, 24)

bottom_nodes[0].force = (0, 150)
bottom_nodes[1].force = (0, -60)
bottom_nodes[2].force = (0, -60)
bottom_nodes[3].force = (0, -60)
bottom_nodes[4].force = (0, -60)
bottom_nodes[5].force = (0, -60)
bottom_nodes[6].force = (0, 150)


members = connect_nodes_pratt(top_nodes, bottom_nodes)

solve_truss(nodes, members)

print(members)

plot_bridge(nodes, members, y_bounds=[bottom_nodes[0].y, top_nodes[0].y])
