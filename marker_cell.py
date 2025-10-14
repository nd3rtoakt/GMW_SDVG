import numpy as np
def marker_cell(nodes, cells, cell_param, path_save):
    with open(path_save + "\\output_colored.vtk", "w") as f:
        f.write("# vtk DataFile Version 2.0\n")
        f.write("Colored Mesh with Intersections\n")
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n\n")
        f.write(f"POINTS {len(nodes)} float\n")

        for x, y, z in nodes:
            f.write(f"{x} {y} {z}\n")
        f.write("\n")
        f.write(f"CELLS {len(cells)} {len(cells) * 4}\n")
        for cell in cells:
            f.write(f"3 {cell[0]} {cell[1]} {cell[2]}\n")
        f.write("\n")

        # triangle type 5
        f.write(f"CELL_TYPES {len(cells)}\n")
        for _ in cells:
            f.write("5\n")
        f.write("\n")

        # color cells
        f.write(f"CELL_DATA {len(cells)}\n")
        f.write("SCALARS cell_color float 1\n")  # RGB
        f.write("LOOKUP_TABLE custom_colors\n")
        for param in cell_param:
            if param > 0:
                f.write(f"{param}\n")
            else:
                f.write("0\n")
        f.write("\n")

def interaction_area(cell_param, all_cells, nodes, cells):
    Area, Area_marked = 0.0, 0.0
    for num_trig in range(all_cells):
        Area += np.linalg.norm(np.cross(nodes[cells[num_trig]][1] - nodes[cells[num_trig]][0], nodes[cells[num_trig]][2] - nodes[cells[num_trig]][0]))
        if cell_param[num_trig] != 0:
            Area_marked += np.linalg.norm(np.cross(nodes[cells[num_trig]][1] - nodes[cells[num_trig]][0], nodes[cells[num_trig]][2] - nodes[cells[num_trig]][0]))
    Area *= 0.5
    Area_marked *= 0.5
    return Area_marked / Area , Area

