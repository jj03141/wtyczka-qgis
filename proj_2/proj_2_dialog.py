# -*- coding: utf-8 -*-
"""
/***************************************************************************
 projekt2Dialog
                                 A QGIS plugin
 Ta wtyczka pozwala obliczyć różnicę wysokości między dwoma punktami oraz pole powierzchni dla obszaru ograniczonego przez minimum 3 punkty
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-06-08
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Jakub Jasiewicz, Patryk Łabędzki
        email                : jakub.jasiewicz3@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import QFileDialog, QInputDialog
from qgis.utils import iface
from math import *
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import Qgis, QgsFeature, QgsGeometry, QgsVectorLayer, QgsProject, QgsPointXY
from qgis.core import QgsMessageLog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'proj_2_dialog_base.ui'))


class projekt2Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(projekt2Dialog, self).__init__(parent)
        self.tableWidget = QtWidgets.QTableWidget()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Wyczyść zawartość labeli
        self.label_pole.clear()
        self.label_poligon.clear()
        # Wyczyść inne labele, które mają być wyczyszczone
        
        self.pushButton_liczelementy.clicked.connect(self.licz_elementy)
        #self.pushButton_dH.clicked.connect(self.roznica_wysokosci)
        self.radioButton_ary.clicked.connect(self.zmien_jednostke)
        self.radioButton_hektary.clicked.connect(self.zmien_jednostke)
        self.radioButton_m2.clicked.connect(self.zmien_jednostke)
        self.pushButton_pole.clicked.connect(self.pole)
        self.pushButton_poligon.clicked.connect(self.poligon)
        self.pushButton_odznacz_wszystko.clicked.connect(self.clear_selection)
        self.pushButton_wyczysc_konsole.clicked.connect(self.clear_console)
        self.pushButton_wczytaj_plik.clicked.connect(self.wczytaj)
        
    def licz_elementy(self):
        liczba_elementów = len(self.mMapLayerComboBox_layers.currentLayer().selectedFeatures())
        self.label_liczbaelementow.setText(str(liczba_elementów))
        
    '''        
    def odleglosci(self):
        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
        X = []
        Y = []
        ODL = []
        for feature in selected_features:
            feature_geometry = feature.geometry().asPoint()
            x = feature_geometry[0]
            y = feature_geometry[1]
            X.append(float(x))
            Y.append(float(y))
        
        t = 0
        for i,j in zip(X,Y):
            #self.textEdit_d.append(f'X = {i:.3f}; Y = {j:.3f}\n')
            if t == len(X) - 1:
                m = 0
            else:
                m = t + 1
            dx = X[m] - X[t]
            dy = Y[m] - Y[t]
            odl = sqrt(dx**2 + dy**2) 
            t += 1
            ODL.append(odl)
            if t == len(X):
                break
            
        for i in ODL:
            self.textEdit_pole.append(f'Odległość: {i:.3f}\n')
        '''
      
    def punkty(self):
        self.label_error.clear()
        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
        pkt = []
        for feature in selected_features:
            feature_geometry = feature.geometry().asPoint()
            x = feature_geometry[0]
            y = feature_geometry[1]
            pkt.append((float(x),float(y)))
        return pkt
    
    def pole(self):
        self.label_error.clear()
        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
        X = []
        Y = []
        for feature in selected_features:
            feature_geometry = feature.geometry().asPoint()
            x = feature_geometry[0]
            y = feature_geometry[1]
            X.append(float(x))
            Y.append(float(y))
        
        n = len(X)
        if n < 3:
            self.label_pole.setText('BŁĄD!')
            self.label_error.setText('Zaznacz więcej punktów!')
            iface.messageBar().pushWarning("Ostrzeżenie", "Zaznaczono zbyt mało punktów.")
            pole_m2 = 0
        
        else:
            pole = 0
            for i in range(n-1):
                x1 = X[i]
                y1 = Y[i]
                x2 = X[i + 1]
                y2 = Y[i + 1]
                pole += x1 * y2 - x2 * y1
            
            pole /= 2
            pole_m2 = abs(pole)
            poletxt = f'Pole: {pole_m2:.3f} [m2]'
            
            self.label_pole.setText(str(poletxt))
            
            punkty_str = ', '.join(f'PKT{i+1}' for i in range(n))
            wynik_str = f'Pole powierzchni figury o wierzchołkach w punktach: {punkty_str} wynosi: {pole_m2:.3f} [m2]'
            iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)
        return pole_m2
            
    def zmien_jednostke(self):
        pole_m = self.pole()
        if self.radioButton_ary.isChecked():
            pole_a = pole_m/100
            self.label_pole.setText(f'Pole: {pole_a:.3f} [a]')
        elif self.radioButton_hektary.isChecked():
            pole_ha = pole_m /10000
            self.label_pole.setText(f'Pole: {pole_ha:.3f} [ha]')
        elif self.radioButton_m2 .isChecked():
            self.label_pole.setText(f'Pole: {pole_m:.3f} [m2]')
        else:
            self.label_pole.setText(f'Pole: {pole_m:.3f} [m2]')
        
    def poligon(self):
        xy = self.punkty()
        punkty = [QgsPointXY(*p) for p in xy]
        pol_geometry = QgsGeometry.fromPolygonXY([punkty])
        if not pol_geometry.isGeosValid():
            self.label_poligon.setText('Nieprawidłowa geometria poligonu')
            return
        pol_feature = QgsFeature()
        pol_feature.setGeometry(pol_geometry)
        
        crs = self.mMapLayerComboBox_layers.currentLayer().crs()
        poligon = QgsVectorLayer("poligon?crs=" + crs.toWkt(), "poligon", "memory")
        poligon.startEditing()
        poligon.addFeature(pol_feature)
        poligon.commitChanges()
        
        QgsProject.instance().addMapLayer(poligon)
        
        area = poligon.getFeature(0).geometry().area()
        if area >= 0:
            self.label_poligon.setText(f'Pole poligonu: {area:.3f}')
        else:
            self.label_poligon.setText('Nie można obliczyć pola poligonu')
            
            
    def closeEvent(self, event):
        super().closeEvent(event)
        self.label_pole.clear()
        self.label_poligon.clear()
        self.radioButton_ary.setChecked(False)
        self.radioButton_hektary.setChecked(False)
        self.radioButton_m2.setChecked(False)
        
    def clear_console(self):
        iface.messageBar().clearWidgets()
        
    def clear_selection(self):
        layer = self.mMapLayerComboBox_layers.currentLayer()
        if layer is not None:
            layer.removeSelection()
            
    def wczytaj(self):
        uklad, ok = QInputDialog.getItem(self, "Wybierz układ współrzędnych", "Wybierz układ:", ["PL-1992", "PL-2000"], 0, False)
        if ok:
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter("Dokumenty tekstowe (*.txt);;Pliki CSV (*.csv)")

            if not dialog.exec_():
                return
            wybrany_plik = dialog.selectedFiles()[0]
            
            if wybrany_plik.endswith(".txt"):
                with open(wybrany_plik, 'r') as plik:
                    lines = plik.readlines()
                    wiersze = [line.strip().split(',') for line in lines]
        
            elif wybrany_plik.endswith(".csv"):
                with open(wybrany_plik, 'r') as plik:
                    csv_reader = csv.reader(plik)
                    wiersze = [row for row in csv_reader]
                
                
            if len(wiersze) == 0 or len(wiersze[0]) < 2:
                QMessageBox.warning(self, "Nieodpowiedni plik", "Wybrany plik ma więcej niż 2 kolumny danych.")
                return
            # Utworzenie tabeli o odpowiedniej liczbie wierszy i kolumn
            self.tableWidget.setRowCount(len(wiersze))
            self.tableWidget.setColumnCount(len(wiersze[0]))
                
                # Wypełnij tabelę danymi
            for i, wiersz in enumerate(wiersze):
                for j, wartosc in enumerate(wiersz):
                    p = QTableWidgetItem(wartosc)
                    self.tableWidget.setItem(i, j, p)
                    
            if uklad == "PL-1992":
                uklad_epsg = "EPSG:2180"
            elif uklad == "PL-2000":
                strefa, ok = QInputDialog.getItem(self, "Wybierz strefę PL-2000", "Wybierz strefę:", ["Strefa 5", "Strefa 6", "Strefa 7", "Strefa 8"], 0, False)
            if not ok:
                return
            if strefa == "Strefa 5":
                uklad_epsg = "EPSG:2176"
            elif strefa == "Strefa 6":
                uklad_epsg = "EPSG:2177"
            elif strefa == "Strefa 7":
                uklad_epsg = "EPSG:2178"
            elif strefa == "Strefa 8":
                uklad_epsg = "EPSG:2179"
                
             # Dodanie warstwy do projektu QGIS
            uri = "Point?crs={}".format(uklad_epsg)
            layer = QgsVectorLayer(uri, "Warstwa", "memory")
            provider = layer.dataProvider()
        
            for wiersz in wiersze:
                if wiersz[0] and wiersz[1]:  # Sprawdź, czy wartości nie są puste
                    try:
                        x = float(wiersz[0])
                        y = float(wiersz[1])
                        feature = QgsFeature()
                        point = QgsPointXY(x, y)
                        geometry = QgsGeometry.fromPointXY(point)
                        feature.setGeometry(geometry)
                        provider.addFeature(feature)
                    except ValueError:
                        QMessageBox.warning(self, "Błąd konwersji", "Wystąpił błąd podczas konwersji współrzędnych.")
        
            QgsProject.instance().addMapLayer(layer)
    