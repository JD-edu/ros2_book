import pyvista as pv

def view_stl_pyvista(file_path):
    # STL 파일 로드
    mesh = pv.read(file_path)
    
    # 플로터 생성 및 설정
    plotter = pv.Plotter(window_size=[1024, 768])
    plotter.add_mesh(mesh, color="lightblue", show_edges=True, edge_color="gray")
    plotter.show_axes()
    plotter.show_grid()
    
    # 뷰어 실행
    plotter.show(title=f"STL Viewer - {file_path}")

if __name__ == "__main__":
    # 본인의 STL 파일 경로 입력
    view_stl_pyvista("./3D_printing_laser_cutting/4axis_robot_arm/base_part_1.stl")