import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import time
import threading
import win32gui
import win32process
import win32con

# === Глобальные переменные ===

gmsh_proc = None
paraview_proc = None
gmsh_path = ""
paraview_path = ""
particle_cloud_path = ""
last_cad_file = None

# === Вспомогательные функции ===

def bring_window_to_front(pid):
    def enum_windows(hwnd, _):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid and win32gui.IsWindowVisible(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
    win32gui.EnumWindows(enum_windows, None)

def kill_process(proc):
    try:
        if proc and proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)
    except Exception:
        pass

# === Функции выбора путей и обновления ячеек ===

def select_gmsh_path():
    global gmsh_path
    path = filedialog.askopenfilename(title="Выберите путь до Gmsh.exe", filetypes=[("Executable", "*.exe")])
    if path:
        gmsh_path = path
        gmsh_entry.delete(0, tk.END)
        gmsh_entry.insert(0, gmsh_path)

def select_paraview_path():
    global paraview_path
    path = filedialog.askopenfilename(title="Выберите путь до ParaView.exe", filetypes=[("Executable", "*.exe")])
    if path:
        paraview_path = path
        paraview_entry.delete(0, tk.END)
        paraview_entry.insert(0, paraview_path)

def select_particle_cloud_path():
    global particle_cloud_path
    path = filedialog.askopenfilename(title="Выберите .txt файл с параметрами облака частиц", filetypes=[("Text files", "*.txt")])
    if path:
        particle_cloud_path = path
        particle_cloud_entry.delete(0, tk.END)
        particle_cloud_entry.insert(0, particle_cloud_path)

# === Кнопки с основным функционалом ===

def on_import_click():
    global gmsh_proc, last_cad_file, gmsh_path

    if not gmsh_path:
        messagebox.showerror("Ошибка", "Сначала выберите путь до Gmsh.exe")
        return

    cad_file = filedialog.askopenfilename(
        title="Выберите CAD файл",
        filetypes=[("CAD файлы", "*.step *.stp *.iges *.igs *.x_t *.x_b *.sat *.sab *.vtk *.fbx")]
    )
    if not cad_file:
        return

    last_cad_file = cad_file

    kill_process(gmsh_proc)
    gmsh_proc = subprocess.Popen([gmsh_path, last_cad_file])
    threading.Thread(target=lambda: (time.sleep(2), bring_window_to_front(gmsh_proc.pid)), daemon=True).start()

def on_save_vtk_click():
    global gmsh_proc, last_cad_file, gmsh_path
    if not last_cad_file:
        messagebox.showerror("Ошибка", "Сначала импортируйте модель в Gmsh.")
        return

    if not gmsh_path:
        messagebox.showerror("Ошибка", "Сначала выберите путь до Gmsh.exe")
        return

    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "model.vtk")

    try:
        subprocess.run([
            gmsh_path,
            last_cad_file,
            "-3",
            "-format", "vtk",
            "-o", output_file
        ], check=True)
        messagebox.showinfo("Успех", f"VTK сохранён в: {output_file}")
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", str(e))
        return

    kill_process(gmsh_proc)

def on_visualize_click():
    global paraview_proc, paraview_path

    if not paraview_path:
        messagebox.showerror("Ошибка", "Сначала выберите путь до ParaView.exe")
        return

    vtk_path = os.path.join(os.getcwd(), "output", "model.vtk")
    if not os.path.exists(vtk_path):
        messagebox.showerror("Ошибка", "VTK-файл модели (model.vtk) не найден. Сначала сохраните его.")
        return

    kill_process(paraview_proc)
    paraview_proc = subprocess.Popen([paraview_path, vtk_path])
    threading.Thread(target=lambda: (time.sleep(2), bring_window_to_front(paraview_proc.pid)), daemon=True).start()

# === Интерфейс ===

root = tk.Tk()
root.title("CAD Workflow")
root.state("zoomed")
root.configure(bg="white")

# Левая панель с выбором путей (3 кнопки + 3 поля ввода)
left_panel = tk.Frame(root, bg="white")
left_panel.pack(side="left", fill="y", padx=10, pady=10)

# Gmsh
tk.Button(left_panel, text="Выбрать путь до Gmsh", command=select_gmsh_path, width=25).pack(pady=5)
gmsh_entry = tk.Entry(left_panel, width=50)
gmsh_entry.pack(pady=5)

# ParaView
tk.Button(left_panel, text="Выбрать путь до ParaView", command=select_paraview_path, width=25).pack(pady=5)
paraview_entry = tk.Entry(left_panel, width=50)
paraview_entry.pack(pady=5)

# Облако частиц
tk.Button(left_panel, text="Задать параметры облака", command=select_particle_cloud_path, width=25).pack(pady=5)
particle_cloud_entry = tk.Entry(left_panel, width=50)
particle_cloud_entry.pack(pady=5)

# Справа сверху — панель кнопок Import, Save VTK, Visualize
top_right_frame = tk.Frame(root, bg="white")
top_right_frame.pack(side="top", anchor="ne", padx=10, pady=10)

tk.Button(top_right_frame, text="Import (Gmsh)", command=on_import_click, bg="#C8A2C8" ,font=("Arial", 11)).pack(side="left", padx=5)
tk.Button(top_right_frame, text="Сохранить как VTK", command=on_save_vtk_click, bg="#d0ffd0", font=("Arial", 11)).pack(side="left", padx=5)
tk.Button(top_right_frame, text="Визуализировать", command=on_visualize_click, bg="#ffe0b3", font=("Arial", 11)).pack(side="left", padx=5)

workspace = tk.Frame(root, bg="#f8f8f8")
workspace.pack(fill="both", expand=True)

root.mainloop()
