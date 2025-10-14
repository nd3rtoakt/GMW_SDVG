def vtk_point_generator(array_point, path_particles):
    with open(path_particles + "\\particles.vtk", "w") as f:
        f.write("# vtk DataFile Version 2.0\n")
        f.write("vtk_gen, Created by Gmsh 4.14.0\n")
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n\n")
        f.write(f"POINTS {len(array_point)} float\n")

        for x, y, z in array_point:
            f.write(f"{x} {y} {z}\n")
        f.write("\n")

        f.write(f"CELLS {len(array_point)} {len(array_point) * 2}\n")

        for i in range(len(array_point)):
            f.write(f"1 {i}\n")

        f.write("\n")

        f.write(f"CELL_TYPES {len(array_point)}\n")

        for _ in range(len(array_point)):
            f.write("1\n")
