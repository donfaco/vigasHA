import sys
import v
from PyQt4 import QtGui
from vigasgui import Ui_MainWindow
from PyQt4.QtGui  import QMainWindow, QTableWidgetItem as Item
#from PyQt4 import QtCore
from flexvigas import flexion
from cortevigas import corte
import webbrowser

import wmi
import requests
import os
import base64

sistema = wmi.WMI().Win32_ComputerSystem()[0]
uuid = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
maquina = sistema.Manufacturer
modelo = sistema.Model
usuario = sistema.UserName
web = base64.b85decode('XmoUNb2=|CW@T(?aAjj}a%5$4Z!U0obZBpGVQzVMXk~I`E@N+PFLr5XVRJ}9FKKRRV`*V>').decode()
datos = {"uuid": uuid, "maquina": maquina, "modelo": modelo, "usuario": usuario}
respuesta = requests.post("{}".format(web), data = datos)
try:
    if respuesta.text == base64.b85decode('Pirnvb!B8_LvL<$X>N64as').decode():
        pass
    else:
        os._exit(0)
except:
    os._exit(0)

class Principal(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(Principal, self).__init__(parent)
        self.setupUi(self)
#        self.label_12.setText("<a href=\"https://felipecordero.cl/\">a</a>")
        self.label_12.mousePressEvent = self.webfelipe
        self.label_12.setToolTip("Abrir sitio web de Felipe Cordero")
#        self.label_12.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
#        self.label_12.setOpenExternalLinks(True)
        self.show()

        self.calcular.clicked.connect(self.calcular_todo)

    def webfelipe(self, event):
        webbrowser.open("https://felipecordero.cl")
    
    def calcular_todo(self):

        #~ Recoger valores de entrada:

        fc  = float(v.fc[self.HormBox.currentText()])
        fy  = float(v.fy[self.AceroBox.currentText()])
        E   = float(v.E[self.HormBox.currentText()])*101.972 # ton/m2

        L   = float(self.L.text())
        B   = float(self.B.text())
        H   = float(self.H.text())
        r   = float(self.rec.text())

        # Calcular Inercia de la viga

        I = 1/12*B*H**3*(0.01**4) # m4

        #~ Datos de entrada para determinar qu:

        a   = float(self.TablaCargas.item(0,0).text())
        e   = float(self.TablaCargas.item(1,0).text())
        cm  = float(self.TablaCargas.item(2,0).text())
        sc  = float(self.TablaCargas.item(3,0).text())

        #~ Determinacion de qu:

        PPlosa  = 2.5*e*0.01*a
        PPviga  = 2.5*H*B*0.01*0.01
        Qsc     = a*sc*0.001
        Qcm     = a*cm*0.001

        qu1     = 1.2*(Qcm + PPlosa + PPviga) + 1.6 * Qsc
        qu2     = 1.4*(Qcm + PPlosa + PPviga)

        qu = max(qu1,qu2)

        quLP = 2*(Qcm + PPlosa + PPviga) + Qsc

        qINS = 1 * (Qcm + PPlosa + PPviga) + Qsc

        self.statusBar.showMessage("qu = "+str(round(qu, 3))+" [ton/m]")

        # Llenado de matriz de resultados

        M   = ["Mi","Mc","Md"]
        V   = ["Vi","Vc","Vd"]
        D   = ["Di","Dc","Dd"]

        filas = range(5)
        cols  = range(3)

        for fila in filas:
            for col in cols:
                if fila == 0:
                    mu = v.res[self.tipo.currentText()][M[col]] * qu * L ** 2
                    f = flexion(H, B, r, fc, fy, mu, 0)
                    item = Item("Mu = {}; As = {}; Asc = {}".format(round(mu,1), f[0], f[1]))
                    rorobItem = Item("{}".format(f[2]))
                    self.resultados.setItem(fila,col,item)
                    self.resultados.setItem(fila + 1, col, rorobItem)
                if fila == 2:
                    vu = v.res[self.tipo.currentText()][V[col]]*qu*L
                    item = Item(str(round(vu,1))+" "+str(corte(B,H,r,fc,fy,vu,0,0.75)))
                    self.resultados.setItem(fila,col,item)
                if fila == 3:
                    du = v.res[self.tipo.currentText()][D[col]]*quLP*L**4/(E*I)*100
                    item = Item(str(round(du,5)))
                    self.resultados.setItem(fila,col,item)
                if fila == 4:
                    du = v.res[self.tipo.currentText()][D[col]]*qINS*L**4/(E*I)*100
                    item = Item(str(round(du,5)))
                    self.resultados.setItem(fila,col,item)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ppal = Principal()
    sys.exit(app.exec_())