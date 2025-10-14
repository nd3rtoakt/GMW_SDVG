from numpy import cross, dot, array

def ray_tracing_check(source, part_point, cell):

    E1 = array(cell[1]) - array(cell[0])
    E2 = array(cell[2]) - array(cell[0])
    D = array(part_point) - array(source)
    T = array(source) - array(cell[0])
    total_det = dot(cross(D, E2), E1)

    if total_det == 0:
        return False, 0

    t = dot(cross(T, E1), E2) / total_det
    u = dot(cross(D, E2), T) / total_det
    v = dot(cross(T, E1), D) / total_det
    if u >= 0 and v >= 0 and (u + v) <= 1 and t > 0:
        return True, t
    else:
        return False, 0
