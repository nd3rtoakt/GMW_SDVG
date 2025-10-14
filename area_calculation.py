import numpy as np

def interaction_area(nodes, cells):
    all_cells = len(cells)
    Area = 0.0
    for num_trig in range(all_cells):
        Area += np.linalg.norm(np.cross(nodes[cells[num_trig]][1] - nodes[cells[num_trig]][0], nodes[cells[num_trig]][2] - nodes[cells[num_trig]][0]))
    Area *= 0.5
    return Area
