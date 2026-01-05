import sys
import os

# --- 核心修改：使用 PySide6 替代 PyQt6 以解决 Nuitka 打包兼容性问题 ---
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QFrame, QDockWidget)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

# 导入 3D 绘图库
import pyvista as pv
from pyvistaqt import QtInteractor

# ==========================================
# 资源路径辅助函数 (打包的关键)
# ==========================================
def get_resource_path(relative_path):
    """
    获取资源的绝对路径。
    兼容开发环境（直接运行 Python）和打包环境（运行 exe）。
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller/Nuitka 打包后的临时解压目录
        base_path = sys._MEIPASS
    else:
        # 开发模式下，使用当前文件所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# ==========================================
# 主窗口类
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. 基础窗口设置
        self.setWindowTitle("MCM Visualization Tool (Powered by PySide6 & PyVista)")
        self.resize(1200, 800) # 默认宽、高

        # 2. 设置图标
        # 注意：这里假设 resources 文件夹和 main.py 同级
        icon_path = get_resource_path(os.path.join("resources", "icon.ico"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"⚠️ Warning: Icon not found at {icon_path}")

        # 3. 初始化 UI 布局
        self.init_ui()

    def init_ui(self):
        """ 初始化界面布局：左侧控制栏 + 右侧 3D 画布 """
        
        # 创建一个中心部件来容纳主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局：水平排列 (Horizontal)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # ----------------------------------
        # 左侧：控制面板 (Sidebar)
        # ----------------------------------
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        self.sidebar.setFixedWidth(250) # 固定宽度
        
        # 侧边栏内部布局：垂直排列
        sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(sidebar_layout)

        # 添加一些控件到侧边栏
        title_label = QLabel("<h2>工具箱</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)

        # 按钮 1：绘制球体
        btn_sphere = QPushButton("🌍 绘制 3D 球体")
        btn_sphere.setFixedHeight(40)
        btn_sphere.clicked.connect(self.plot_sphere) # 绑定点击事件
        sidebar_layout.addWidget(btn_sphere)

        # 按钮 2：清空画布
        btn_clear = QPushButton("🗑️ 清空画布")
        btn_clear.setFixedHeight(40)
        btn_clear.clicked.connect(self.clear_plot)
        sidebar_layout.addWidget(btn_clear)

        # 弹簧 (Spacer)：把内容顶上去
        sidebar_layout.addStretch()

        # 作者信息
        sidebar_layout.addWidget(QLabel("MCM 2026 Toolbox\nv1.0.0 Build"))

        # 将侧边栏加入主布局
        main_layout.addWidget(self.sidebar)

        # ----------------------------------
        # 右侧：3D 渲染画布 (The Canvas)
        # ----------------------------------
        # 使用 QtInteractor，它是一个嵌入 Qt 的 PyVista 窗口
        self.plotter = QtInteractor(self)
        main_layout.addWidget(self.plotter.interactor)

        # 初始化画布背景
        self.plotter.set_background("white") # 论文风格推荐白色背景
        self.plotter.add_axes() # 显示坐标轴
        self.plotter.add_text("Ready for Data...", position='upper_left', color='black')

    # ==========================================
    # 业务逻辑功能
    # ==========================================
    def plot_sphere(self):
        """ 演示功能：在画布上画一个球 """
        self.plotter.clear() # 先清空
        self.plotter.add_axes()
        
        # 创建一个球体模型
        sphere = pv.Sphere(radius=0.5)
        
        # 添加到场景中
        # show_edges=True 显示网格线，看起来更有“建模感”
        # pbr=True 开启物理渲染 (Physically Based Rendering)，更有质感
        self.plotter.add_mesh(sphere, color="orange", show_edges=True, pbr=False, opacity=0.8)
        
        self.plotter.add_text("Model: 3D Sphere", position='upper_left', color='black')
        self.plotter.reset_camera() # 重置相机视角
        
        print("✅ 成功绘制球体")

    def clear_plot(self):
        """ 清空画布 """
        self.plotter.clear()
        self.plotter.set_background("white")
        self.plotter.add_axes()
        print("🧹 画布已清空")

    def closeEvent(self, event):
        """ 窗口关闭时的清理操作 """
        self.plotter.close()
        event.accept()

# ==========================================
# 程序入口
# ==========================================
if __name__ == "__main__":
    # 创建 Qt 应用实例
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # 使用 Fusion 风格，跨平台且美观

    # 设置应用程序级别的图标（确保任务栏显示图标）
    app_icon_path = get_resource_path(os.path.join("resources", "icon.ico"))
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 进入事件循环
    sys.exit(app.exec())