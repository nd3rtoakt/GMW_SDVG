import numpy as np
import logging, argparse, sys, time, os
import ray_tracing
from particle_generator import sphere_cloud, cone_cloud
from vtk_reader import vtk_reader
from vtk_writer import dict_param, vtk_writer
from config_reader import parse_config
from area_calculation import interaction_area
from combiner import conbine_models


VERSION = "betta_0.1.0"
start_time = time.time()

logging.basicConfig(filename='info.log', level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

parser = argparse.ArgumentParser(description="Пример программы с версией")
parser.add_argument(
    "-v", "--version",
    action="store_true",
    help="Показать версию программы"
)

parser.add_argument(
    "-f", "--file",
    type=str,
    help="Путь к файлу конфигурации"
)
parser.add_argument(
    "-d", "--debug",
    type=int,
    choices=[0, 1, 2],
    default=0,
    help="Уровень дебага (0-2)"
)

args = parser.parse_args()

if args.version:
    print(f"Версия программы: {VERSION}")
    sys.exit(0)

if args.file:
    config_path = args.file
    if not os.path.isfile(config_path):
        print(f"Файл конфигурации '{config_path}' не найден!")
        sys.exit(1)
else:
    # Папка, где лежит exe
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_path = os.path.join(exe_dir, "config.txt")
    if not os.path.isfile(config_path):
        print("Файл конфигурации не передан и 'config.txt' не найден в папке с программой!")
        sys.exit(1)

if args.debug > 0:
    print(f"Уровень дебага: {args.debug}")

if args.version:
    print(f"Версия программы: {VERSION}")
    sys.exit(0)

config = parse_config(config_path)

if args.debug == 2:
    print(config)

print(f'Конфигурационный файл успешно загружен')
models_params = config['models']
clouds = config['clouds']
path_dir = config['project_directory'][0]['path']
particles = []
source_points = []

for cloud in clouds:
    if cloud['figure_type'] == 'sphere':
        particles.append(sphere_cloud(cloud['number_of_particles'], cloud['radius'],
                 cloud["source"], cloud['distribution_type'], cloud['sigma_r']))
        source_points.append(cloud["source"])
    elif cloud['figure_type'] == 'cone':
        particles.append(cone_cloud(cloud['number_of_particles'], cloud['radius'],
                 cloud["source"], cloud['distribution_type'], cloud['sigma_r'], cloud['sigma_z'], cloud["height"], cloud['orientation_angle']))
        source_points.append(cloud["source"])
    else:
        raise ValueError("Неизвестная форма облака частиц")

print(f'Облако частиц создано')

cells, nodes, _, _ = vtk_reader(models_params[0]["path"])
orginal_model_p = {}
orginal_model_p[models_params[0]["path"].split('\\')[-1]] = {'num_cell': len(cells), 'num_nodes': len(nodes)}
for i in range(1, len(models_params)):
    path = models_params[i]["path"]
    cells, nodes = conbine_models(cells, nodes, path)
    orginal_model_p[path.split('\\')[-1]] = {'num_cell': len(cells), 'num_nodes': len(nodes)}

num_cloud_particles = int(np.array(particles).size / 3)
point_data_vec_c = np.zeros((num_cloud_particles, 3))
point_data_scal_c = np.zeros((num_cloud_particles, 1))

cell_data = {}
cell_param_all = np.zeros((len(cells), 1))


num_cloud = 0
index_cloud = 0
print(f'Начат процесс пересечения частиц с моделями')
for cloud in particles:
    cell_param = np.zeros((len(cells), 1))
    for part_num in range(len(cloud)):
        length = 0
        answer = 0
        interaction, min_interaction = [], []
        for cell_num in range(len(cells)):
            answer, length = ray_tracing.ray_tracing_check(source_points[num_cloud], cloud[part_num], nodes[cells[cell_num]])
            vector = cloud[part_num] - source_points[num_cloud]
            point_data_vec_c[part_num + index_cloud] = vector / np.linalg.norm(vector)

            if answer == True:
                interaction.append([length, cell_num])
                point_data_scal_c[part_num + index_cloud] = 1

        if len(interaction) != 0:
            min_interaction = min(interaction, key = lambda x: x[0])
            cell_param[min_interaction[1]] += 1
    cell_param_all += cell_param
    num_cloud += 1
    cell_data = dict_param(cell_data, f'cloud_{num_cloud}', cell_param)
    index_cloud += len(cloud)
    # vtk_writer(f'B:\\GMM_2025\\v5\\bmm-math-modeling-MayorIvan1-patch-1\\clouds-{num_cloud}.vtk', cloud)
print('Пересечение частиц с моделями успешно завершено')
point_data = {}
point_data_vec_m = np.zeros((len(nodes), 3))
point_data_vec = np.vstack([point_data_vec_m, point_data_vec_c])
point_data = dict_param(point_data, 'trace_vector', point_data_vec)
point_data_scal_m = np.zeros((len(nodes), 1))
point_data_scal = np.vstack([point_data_scal_m, point_data_scal_c])
point_data = dict_param(point_data, 'interaction', point_data_scal)

cell_data = dict_param(cell_data, f'cloud_all', cell_param_all)

points_cloud = []
points_all = np.vstack([nodes, particles[0]])
for cloud in range(1,len(particles)):
    points_all = np.vstack([points_all, particles[cloud]])

point_data_scal_m = np.zeros((len(nodes), 1))
point_data_scal_c = np.ones((num_cloud_particles, 1))
point_data_scal = np.vstack([point_data_scal_m, point_data_scal_c])
point_data = dict_param(point_data, 'mass_point', point_data_scal)

vtk_writer(path_dir, points_all, cells, cell_data, point_data)

all_area = interaction_area(nodes, cells)

end_time = time.time()
_time = end_time - start_time

print(f'Время выполнения работы программы: {_time:.2f} сек')

logging.info(f"Программа успешно выполнила работу!\n"
             f"Количество частиц попавших на модели: {sum(cell_param_all)} %\n"
             f"Общее количество частиц: {np.array(particles).size / 3}\n"
             f"Вероятность попадания: {sum(cell_param_all) / (np.array(particles).size / 3)}\n"
             f"Время выполнения программы: {_time:.2f} сек\n"
             f"Число ячеек моделей и число частиц: {len(cells)} * {int(np.array(particles).size / 3)} = "
             f"{len(cells) * int(np.array(particles).size / 3)}\n")
