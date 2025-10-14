import numpy as np
from vtk_reader import vtk_reader

def conbine_models(cells1, nodes1, model2):
    cells2, nodes2, _, _ = vtk_reader(model2)
    cells2 += len(nodes1)
    cells_ = np.vstack([cells1, cells2])
    nodes_ = np.vstack([nodes1, nodes2])
    return cells_, nodes_
