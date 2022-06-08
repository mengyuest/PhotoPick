import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QDockWidget, \
    QPushButton, QDesktopWidget, QFileDialog, QSlider, QGridLayout, QTableView, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QPixmap
from PyQt5.QtCore import Qt

class Windows(QWidget):
    def __init__(self):
        super().__init__()

        self.reset_vars()

        self.init_ui()

    def init_ui(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # self.dock = True
        self.dock = False

        # buttons
        self.btn_load = self.create_load_button()
        self.btn_prev = self.create_prev_button()
        self.btn_next = self.create_next_button()
        self.btn_save = self.create_save_button()

        # add the score slider
        self.slider = self.create_slider()
        self.textEdit = self.create_listview()
        self.image_viewer = self.create_image_viewer()

        self.resize(600, 800)
        self.center()
        self.setWindowTitle('Photo Data Collector')
        self.setWindowIcon(QIcon('samples/cam1.png'))
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def create_load_button(self):
        self.label_input_path = QLabel()
        self.label_input_path.setText("Image directory: %s" % (self.dir_name))
        self.grid.addWidget(self.label_input_path, 0, 0, 1, 16, alignment=Qt.AlignLeft)

        btn0 = QPushButton('Load', self)
        btn0.setToolTip('Open the image directory')
        btn0.resize(btn0.sizeHint())
        self.grid.addWidget(btn0, 1, 0, 3, 4)
        btn0.clicked.connect(self.load_path)
        return btn0

    def create_prev_button(self):
        btn1 = QPushButton('Prev', self)
        btn1.setToolTip('Choose the previous image')
        btn1.resize(btn1.sizeHint())
        self.grid.addWidget(btn1, 1, 4, 3, 4)
        btn1.clicked.connect(self.prev_image)
        btn1.setEnabled(False)
        return btn1

    def create_next_button(self):
        btn2 = QPushButton('Next', self)
        btn2.setToolTip('Choose the next image')
        btn2.resize(btn2.sizeHint())
        self.grid.addWidget(btn2, 1, 8, 3, 4)
        btn2.clicked.connect(self.next_image)
        btn2.setEnabled(False)
        return btn2

    def create_save_button(self):
        btn3 = QPushButton('Save', self)
        btn3.setToolTip('Save the scoring data')
        btn3.resize(btn3.sizeHint())
        self.grid.addWidget(btn3, 1, 12, 3, 4)
        btn3.clicked.connect(self.save_data)
        btn3.setEnabled(False)
        return btn3

    def create_slider(self):
        slider = QSlider(Qt.Horizontal, self)
        slider.setRange(0, 100)
        slider.setTickInterval(10)
        slider.setSingleStep(100)
        slider.setTickPosition(QSlider.TicksAbove)

        self.label_score = QLabel()
        self.label_score.setText("Score: %d" % (slider.value()))
        self.grid.addWidget(self.label_score, 4, 0, 1, 1, alignment=Qt.AlignLeft)

        label_minimum = QLabel()
        label_minimum.setText("%d (Bad)" % slider.minimum())
        self.grid.addWidget(label_minimum, 5, 0, 3, 1, alignment=Qt.AlignLeft)  #, alignment=Qt.AlignLeft | Qt.AlignBottom)

        label_maximum = QLabel()
        label_maximum.setText("%d (Good)" % slider.maximum())
        self.grid.addWidget(label_maximum, 5, 15, 3, 1, alignment=Qt.AlignLeft)  #, alignment=Qt.AlignRight | Qt.AlignBottom)

        slider.setFocusPolicy(Qt.NoFocus)
        self.grid.addWidget(slider, 5, 1, 3, 14)
        slider.valueChanged[int].connect(self.change_score)
        slider.setEnabled(False)
        return slider

    def create_listview(self):
        self.tableview = QTableView()
        if self.dock:
            self.items = QDockWidget("Dockable")
            self.items.setWidget(self.tableview)
            self.items.setFloating(False)
            # self.setCentralWidget(QTextEdit())
            self.addDockWidget(Qt.RightDockWidgetArea, self.items)
        else:
            self.grid.addWidget(self.tableview, 8, 0, 4, 16)

    def create_image_viewer(self):
        image_viewer = QLabel(alignment=Qt.AlignCenter)
        self.grid.addWidget(image_viewer, 12, 0, 24, 16, alignment=Qt.AlignCenter)
        image_viewer.setFixedSize(400, 400)
        return image_viewer

    # EVENTS
    def reset_vars(self):
        self.dir_name = None
        self.img_names = []
        self.curr_idx = None
        self.save_name = None
        self.model = None
        self.pixmap = None
        self.lbl = None

    def load_path(self):
        self.dir_name = QFileDialog.getExistingDirectory(self, 'Choose image directory', './')
        if self.dir_name:
            self.label_input_path.setText("Image directory: %s" % (self.dir_name))
            self.img_names = [x for x in os.listdir(self.dir_name) if x.split(".")[-1].lower() in ["png", "jpg", "jpeg"]]
            self.btn_next.setEnabled(True)
            self.btn_prev.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.slider.setEnabled(True)
            if len(self.img_names) > 0:
                self.curr_idx = 0
                self.model = QStandardItemModel(len(self.img_names), 3)
                self.model.setHorizontalHeaderLabels(['Photo name', "Capture time", 'Score'])
                self.tableview.setModel(self.model)
                self.tableview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.tableview.selectionModel().selectionChanged.connect(self.after_select_row)
                self.tableview.setSelectionBehavior(QAbstractItemView.SelectRows)
                sort_tuple = []
                for i in range(len(self.img_names)):
                    mtime = os.path.getmtime(os.path.join(self.dir_name, self.img_names[i]))
                    sort_tuple.append((self.img_names[i], mtime))
                sort_tuple = sorted(sort_tuple, key=lambda x:x[1])
                for i, (img_name, mtime) in enumerate(sort_tuple):
                    self.model.setItem(i, 0, QStandardItem(img_name))
                    print(os.path.join(self.dir_name, img_name))
                    dtime = datetime.fromtimestamp(mtime).strftime('%Y/%m/%d %H:%M:%S')
                    self.model.setItem(i, 1, QStandardItem(dtime))
                    self.model.setItem(i, 2, QStandardItem("0"))


    def after_select_row(self, clickedIndex):
        self.curr_idx = self.tableview.selectionModel().currentIndex().row()  #clickedIndex.row()
        self.change_row_idx()

    def change_row_idx(self):
        fname = self.model.index(self.curr_idx, 0).data()
        print("Col:", self.curr_idx, fname)
        self.show_image()
        self.slider.setValue(int(self.model.index(self.curr_idx, 2).data()))

    def show_image(self):
        img_full_path = os.path.join(self.dir_name, self.img_names[self.curr_idx])
        pixmap = QPixmap(img_full_path)
        if pixmap.width() > 360:
            pixmap = pixmap.scaled(360, 360, Qt.KeepAspectRatio)
        self.image_viewer.setPixmap(pixmap)

    def prev_image(self):
        if self.curr_idx is not None:
            self.curr_idx -= 1
            if self.curr_idx < 0:
                self.curr_idx += len(self.img_names)
            self.tableview.setCurrentIndex(self.tableview.model().index(self.curr_idx, 0))

    def next_image(self):
        if self.curr_idx is not None:
            self.curr_idx += 1
            if self.curr_idx >= len(self.img_names):
                self.curr_idx -= len(self.img_names)
            self.tableview.setCurrentIndex(self.tableview.model().index(self.curr_idx, 0))

    def save_data(self):
        self.save_name = QFileDialog.getSaveFileName(self, 'Save data file', './')
        if self.save_name[0]:
            print(self.save_name)
            with open(self.save_name[0], "w") as f:
                for i in range(len(self.img_names)):
                    f.write("%s; %s; %s\n"%(
                        self.model.index(i, 0).data(),
                        self.model.index(i, 1).data(),
                        self.model.index(i, 2).data()
                    ))

    def change_score(self):
        self.label_score.setText("Score: %d" % (self.slider.value()))
        self.model.setItem(self.curr_idx, 2, QStandardItem("%d" % self.slider.value()))


if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = Windows()
    sys.exit(app.exec_())