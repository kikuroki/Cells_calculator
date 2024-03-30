import sys
from PyQt5.QtWidgets import QMessageBox,QTableWidget, QTableWidgetItem, QPushButton,QGraphicsView, QApplication, QMainWindow, QAction, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QFileDialog, QGraphicsTextItem, QComboBox, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QFont,QColor
from PyQt5.QtCore import Qt
import numpy as np
import tifffile
from cahnal_setting import DialogWindow
from calculate_functions import metod1, metod2, metod3
class MainWindow(QMainWindow):
    parametrs = {'Option 1': 'Channel 1',
                 'Option 2': 'Channel 2',
                 'Option 3': 'Channel 3'
                 
                 }
    metods = {
        'metod1': metod1,
        'metod2': metod2,
        'metod3': metod3
    }
    lsm_path = None
    
    def __init__(self):
        
        super().__init__()
        
        desktop = QApplication.desktop()
        screen_geometry = desktop.availableGeometry()

        self.setFixedSize(screen_geometry.width(), desktop.availableGeometry().height()-self.menuBar().height())

        
        self.setWindowTitle("Main Window")
        #self.setMinimumSize
        
        self.initUI()

    def initUI(self):
        #self.setGeometry(100, 100, 800, 600)
        
        # Create a menu action to open LSM file
        self.open_lsm_action = QAction("Open LSM File", self)
        self.open_lsm_action.triggered.connect(self.open_lsm)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_dialogWindow)

        # Добавление действия в меню
        
        # Create a menu bar
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        
        file_menu.addAction(self.open_lsm_action)
        settings_menu = menubar.addMenu("Settings")
        settings_menu.addAction(settings_action)
        self.init_mainScen()
    def init_mainView(self):
        # TODO : add 2 button 
        self.main_view.setFixedWidth(int(self.width() * 0.75))
        #self.main_view.setFixedHeight(int(self.height()*0.95))
        #self.main_view.setMaximumHeight(int(self.height()))
        
    
    def init_rightLayout(self):
        self.combo_box = QComboBox()
        label = QLabel("Choose metod:")
        self.right_scene = QGraphicsScene()
      
        self.right_view = QGraphicsView(self.right_scene)
        self.right_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.right_button = QPushButton("Calculate")

        
        self.combo_box.setFont(QFont("Arial", 24)) 
        self.combo_box.addItems([key for key in self.metods])
        self.combo_box.currentTextChanged.connect(self.selection_changed)
        self.combo_box.setCurrentIndex(-1)
        label.setFont(QFont("Arial", 32))
        self.right_button.setFont(QFont("Arial", 32))
        self.right_button.clicked.connect(self.calculate_button)
        
        
        

        self.right_layout.addWidget(label)
        self.right_layout.addSpacing(20)
        self.right_layout.addWidget(self.combo_box)
        self.right_layout.addSpacing(20)
      
        self.right_layout.addWidget(self.right_view)
        self.right_layout.addSpacing(20)
        self.right_layout.addWidget(self.right_button)
        self.right_layout.addSpacing(20)
        
        #max_width = self.right_view.maximumWidth()
        #max_height = self.right_view.maximumHeight()

# Установка размера сцены равным максимальной ширине и высоте
        #self.right_scene.setSceneRect(0, 0, max_width, max_height)
        
    def init_mainScen(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()

        self.main_scen = QGraphicsScene()
        self.main_view = QGraphicsView(self.main_scen)
        self.init_mainView()

        self.right_layout = QVBoxLayout()
        self.init_rightLayout()
        
        self.main_layout.addWidget(self.main_view)
        self.main_layout.addLayout(self.right_layout)
        self.central_widget.setLayout(self.main_layout)
        
       
        
        
        
    def show_warning_dialog(self):
    # Создаем диалоговое окно предупреждения
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("Warning\n\nChoose method and file.")
        #msgBox.setInformativeText("Choose method and file.")
        msgBox.setWindowTitle("Warning")
        msgBox.adjustSize()
        msgBox.exec_()
        
    def calculate_button(self):
        metod = self.combo_box.currentText()
        if metod == "" or self.lsm_path is None:
            self.show_warning_dialog()
            print("choose metod and fille")
            return 0
            #TODO : сделать обработку если не  выбран метод
        
        result = self.metods[metod](lsm_path = self.lsm_path, parametrs = self.parametrs)
        if not result:
            return 0
            
        #self.right_view.setFixedSize(451, 661)
        
        label_aliveCells = QGraphicsTextItem(f'Alive cells: {result["alive"]*100}%')
        label_aliveCells.setFont(QFont('Arial',24))
        label_aliveCells.setPos(0, 0)
        label_deadCells = QGraphicsTextItem(f'Dead cells: {result["dead"]*100}%')
        label_deadCells.setFont(QFont('Arial',24))
        label_deadCells.setPos(0, 100)
        self.right_scene.clear()
        self.right_scene.addItem(label_aliveCells)
        
        self.right_scene.addItem(label_deadCells)
        #self.right_view.fitInView(self.right_scene.sceneRect())#, Qt.KeepAspectRatio)
        #self.right_view.adjustSize()
       
        
        
    def selection_changed(self, text):
        print(text)
        

    def open_lsm(self):
        #запомнить путь последней папки  вместо ""
        self.lsm_path, _ = QFileDialog.getOpenFileName(self, "Open .LSM File", "", "LSM Files (*.lsm)")

        if self.lsm_path:
            with tifffile.TiffFile(self.lsm_path) as tif:
                lsm_file = tif.pages[0].asarray()
            image = QImage(lsm_file[1], lsm_file.shape[1],  lsm_file.shape[2] , QImage.Format_Grayscale8)

            # Создаем QPixmap из QImage
            pixmap = QPixmap.fromImage(image)
            
            pixmap_item = self.main_scen.addPixmap(pixmap)
            self.main_view.fitInView(pixmap_item, Qt.KeepAspectRatio)
            
    def open_dialogWindow(self):
        #запомнить путь последней папки  вместо ""
        #self.lsm_path, _ = QFileDialog.getOpenFileName(self, "Open .LSM File", "", "LSM Files (*.lsm)")

        if self.lsm_path:
            dialog = DialogWindow(parent=self, lsm_path=self.lsm_path, parametrs = self.parametrs)
            dialog.setWindowModality(Qt.ApplicationModal)
            #dialog.setFixedSize(1080, 720)
            #dialog.move(100,100)
            dialog.show()
            dialog.center()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(QApplication.desktop().availableGeometry())
    window = MainWindow()
    window.showMaximized()
    print(window.right_view.size())
    #window.open_lsm_action.trigger()

    sys.exit(app.exec_())
