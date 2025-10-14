def vtk_writer(path_particles, points, cells=[], cells_data=[], points_data=[]):
    len_c = len(cells)
    len_p = len(points)
    len_cd = len(cells_data)
    len_pd = len(points_data)
    with open(path_particles, "w") as f:
        f.write("# vtk DataFile Version 2.0\n")
        f.write("Created by Gmsh 4.14.0\n")
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n")

        f.write(f"POINTS {len(points)} float\n")
        for x, y, z in points:
            f.write(f"{x} {y} {z}\n")
        f.write("\n")

        if len_c != 0:
            num_verteces = len(cells[0])
            f.write(f"CELLS {len_c} {len_c * (num_verteces + 1)}\n")
            for cell in cells:
                f.write(f"{num_verteces} {cell[0]} {cell[1]} {cell[2]}\n")
            f.write("\n")
            f.write(f"CELL_TYPES {len_c}\n")
            for _ in range(len_c):
                f.write("5\n")


        if len_cd != 0:
            f.write("\n")
            f.write(f"CELL_DATA {len_c}\n")
            for name_cd in cells_data.keys():
                if cells_data[name_cd].shape[0] != len_c:
                    raise ValueError(f"Длина массива параметров ячеек {len(cells_data[name_cd].shape[0])} /= числу ячеек {len_c}")
                if cells_data[name_cd].shape[1] == 1:
                    f.write(f"SCALARS {name_cd} float\n")
                    f.write("LOOKUP_TABLE default\n")
                    for data in cells_data[name_cd]:
                        f.write(f"{data[0]}\n")
                else:
                    f.write(f"VECTORS {name_cd} float\n")
                    for data in cells_data[name_cd]:
                        f.write(f"{data[0]} {data[1]} {data[2]}\n")
                f.write("\n")

        if len_pd != 0:
            f.write("\n")
            f.write(f"POINT_DATA {len_p}\n")
            for name_pd in points_data.keys():
                if points_data[name_pd].shape[0] != len_p:
                    raise ValueError(f"Длина массива параметров ячеек {len(points_data[name_pd].shape[0])} /= числу ячеек {len_p}")
                if points_data[name_pd].shape[1] == 1:
                    f.write(f"SCALARS {name_pd} float\n")
                    f.write("LOOKUP_TABLE default\n")
                    for data in points_data[name_pd]:
                        f.write(f"{data[0]}\n")
                else:
                    f.write(f"VECTORS {name_pd} float\n")
                    for data in points_data[name_pd]:
                        f.write(f"{data[0]} {data[1]} {data[2]}\n")
                f.write("\n")

def dict_param(dict, name, data=[]):
    dict[name] = data
    return dict
