import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph



def request_field_data(ip):
    field = requests.get("http://" + ip + "/io/t1/probe/field/value.json").json()
    return round(field, 3)

def request_temp_data(ip):
    temp = requests.get("http://" + ip + "/io/t1/probe/average_temperature/value.json").json()
    return round(temp, 3)

def request_offset_data(ip):
    offset = requests.get("http://" + ip + "/io/t1/probe/offset/value.json").json()
    return round(offset, 3)


class T1Display(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T1 input")
        self.resize(1000, 500)

        self.verticalLayoutWidget_2 = QWidget(self)
        self.setCentralWidget(self.verticalLayoutWidget_2)

        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(50, 10, 50, 50)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setContentsMargins(20, 20, 10, 10)

        #measurement range
        self.mr_label = QLabel("measurement range", self.verticalLayoutWidget_2)
        
        self.gridLayout_2.addWidget(self.mr_label, 0, 0, 1, 1)
        self.mr_input = QComboBox(self.verticalLayoutWidget_2)
        self.mr_input.addItem("700")
        self.mr_input.addItem("2800")
        self.mr_input.addItem("7000")
        self.mr_input.addItem("28000")
        self.gridLayout_2.addWidget(self.mr_input, 0, 1, 1, 1)

        self.mr_input.currentIndexChanged.connect(self.change_mr)

        #sample rate
        self.sr_label = QLabel("sample rate (Hz)", self.verticalLayoutWidget_2)
        self.gridLayout_2.addWidget(self.sr_label, 1, 0, 1, 1)
        self.sr_input = QComboBox(self.verticalLayoutWidget_2)
        self.sr_input.addItem("10")
        self.sr_input.addItem("50")
        self.sr_input.addItem("100")
        self.sr_input.addItem("500")
        self.sr_input.addItem("1000")
        self.sr_input.addItem("5000")
        self.sr_input.addItem("25000")
        self.gridLayout_2.addWidget(self.sr_input, 1, 1, 1, 1)

        self.sr_input.currentIndexChanged.connect(self.change_sr)

        #layout

        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.horizontalLayout = QHBoxLayout()

        #change to graph
        self.graphWidget = pyqtgraph.PlotWidget(self.verticalLayoutWidget_2)
        self.graphWidget.setBackground("#e1f7c8")
        self.horizontalLayout.addWidget(self.graphWidget)
        


        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setContentsMargins(5, 5, 5, 1500)

        self.timer_button = QPushButton("start", self.verticalLayoutWidget_2)
        self.timer_button.clicked.connect(self.timer_event)
        self.verticalLayout.addWidget(self.timer_button)

        self.clear_button = QPushButton("clear", self.verticalLayoutWidget_2)
        self.clear_button.clicked.connect(self.clear_values)
        self.verticalLayout.addWidget(self.clear_button)


        #perhaps i will add in tesla conversion but is it really necessary
        self.field_label = QLabel("field", self.verticalLayoutWidget_2)
        self.verticalLayout.addWidget(self.field_label)


        #self.field_units = QPushButton(self.verticalLayoutWidget_2)
        #self.field_units.setCheckable(True)
        #self.field_units.setDefault(False)
        #self.field_units.setFlat(False)
        #self.verticalLayout.addWidget(self.field_units)

        self.temperature_label = QLabel("temperature", self.verticalLayoutWidget_2)
        self.verticalLayout.addWidget(self.temperature_label)

        self.offset_label = QLabel("offset", self.verticalLayoutWidget_2)
        self.verticalLayout.addWidget(self.offset_label)

        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.timer = QTimer()
        self.timer.timeout.connect(self.update_values)
        self.interval = 1/int(self.sr_input.currentText()) * 1000
        self.timer.setInterval(self.interval)
        self.time = 0
        self.mr_value = int(self.mr_input.currentText())
        self.time_values = []
        self.field_values = []

    def ipInput(self):
        self.ip_dialog = QDialog()
        self.ip_dialog.setWindowTitle("t1 ip submit")
        self.resize(500, 500)
        self.dialog_layout = QHBoxLayout(self.ip_dialog)
        self.ip_dialog.setModal(True)

        self.ip_label = QLabel("ip of t1")
        self.dialog_layout.addWidget(self.ip_label)

        self.ip_input = QLineEdit("", self)
        self.dialog_layout.addWidget(self.ip_input)

        self.ip_submit = QPushButton("submit", self)
        self.dialog_layout.addWidget(self.ip_submit)

        self.ip_submit.clicked.connect(self.def_ip)

    
    def def_ip(self):
        self.t1_ip = self.ip_input.text()
        try:
            field = requests.get("http://" + self.t1_ip + "/io/t1/probe/offset/value.json", timeout=10).json()
            self.ip_dialog.close()
        except:
            self.error_dialog = QMessageBox.warning(self, "not a valid ip", "please submit a valid ip (etc 192.168.1.1) and check that the ip belongs to the t1 device")

    def update_values(self):
        field = request_field_data(self.t1_ip)
        self.field_label.setText("field: "+'{:.3f}'.format(round(field, 3)) +" G")
        self.field_label.repaint()

        temp = request_temp_data(self.t1_ip)
        self.temperature_label.setText("temperature: "+'{:.3f}'.format(round(temp, 3)) +" C \N{DEGREE SIGN}")
        self.temperature_label.repaint()

        offset = request_offset_data(self.t1_ip)
        self.offset_label.setText("offset: " + '{:.3f}'.format(round(offset, 3)))
        self.offset_label.repaint()

        if not field > self.mr_value:
            self.time_values.append(self.time)
            self.field_values.append(field)

        self.time += self.interval

        pen = pyqtgraph.mkPen(color="#784f59", width=5)
        self.graphWidget.plot(self.time_values, self.field_values, pen=pen)

    def clear_values(self):
        self.field_label.setText("field: ")
        self.temperature_label.setText("temperature: ")
        self.offset_label.setText("offset: ")
        self.graphWidget.clear()
        self.field_values = []
        self.time_values = []

    def timer_event(self):
        if self.timer.isActive():
            self.timer_button.setText("start")
            self.clear_button.setEnabled(True)
            self.timer.stop()
        else:
            self.timer_button.setText("stop")
            self.clear_button.setEnabled(False)
            self.timer.start()

    def change_sr(self):
        self.interval = 1/int(self.sr_input.currentText())*1000

    def change_mr(self):
        self.mr_value = int(self.mr_input.currentText())



    
    

if __name__ == "__main__":
    app = QApplication(sys.argv)

    t1display = T1Display()
    t1display.ipInput()
    t1display.ip_dialog.show()
    t1display.show()

    sys.exit(app.exec_())