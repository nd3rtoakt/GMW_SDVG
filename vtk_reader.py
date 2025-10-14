import meshio

def vtk_reader(path):
    mesh = meshio.read(path)

    _names = []
    _types = []
    _cells = []

    for name, data_list in mesh.cell_data.items():
        _names.append(name)
        trace_array = mesh.cell_data[name][0]
        _types.append(trace_array.shape[1])

    for name, data_list in mesh.point_data.items():
        _names.append(name)
        trace_array = mesh.point_data[name]
        _types.append(trace_array.shape[1])

    _nodes = mesh.points
    _cell_data = mesh.cell_data
    _point_data = mesh.point_data

    cells = []
    for cell_block in mesh.cells:
        cells.append(cell_block.data)

    for cell in cells:
        if cell.shape[1] == 3: # for triangle
            _cells = cell

    #print(_cell_data,_point_data,_names,_types)

    return _cells, _nodes, _cell_data, _point_data
