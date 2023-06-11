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
import csv
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import QFileDialog, QInputDialog
from qgis.utils import iface
from math import *
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import Qgis, QgsFeature, QgsGeometry, QgsVectorLayer, QgsProject, QgsPointXY
from qgis.core import QgsFields, QgsField, QgsWkbTypes





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
        self.canvas = iface.mapCanvas()

        # Wyczyść zawartość labeli
        self.label_pole.clear()
        self.label_error.clear()
        # Wyczyść inne labele, które mają być wyczyszczone
        
        #ukryj radiobuttony 
        self.radioButton_ary.setVisible(False)
        self.radioButton_hektary.setVisible(False)
        self.radioButton_m2.setVisible(False)
        self.radioButton_kilometry.setVisible(False)
        self.radioButton_metry.setVisible(False)
        self.radioButton_stopnie.setVisible(False)
        self.radioButton_grady.setVisible(False)
        self.radioButton_radiany.setVisible(False)
        self.radioButton_mm.setVisible(False)
        self.radioButton_cm.setVisible(False)
        self.radioButton_m_dh.setVisible(False)
        self.pushButton_az_odw.setVisible(False)
        
        
        self.pushButton_liczelementy.clicked.connect(self.licz_elementy)
        self.pushButton_dH.clicked.connect(self.roznica_wysokosci)
        self.radioButton_ary.clicked.connect(self.zmien_jednostke_pole)
        self.radioButton_hektary.clicked.connect(self.zmien_jednostke_pole)
        self.radioButton_m2.clicked.connect(self.zmien_jednostke_pole)
        self.radioButton_metry.clicked.connect(self.zmien_jednostke_odl)
        self.radioButton_kilometry.clicked.connect(self.zmien_jednostke_odl)
        self.radioButton_radiany.clicked.connect(self.zmien_jednostki)
        self.radioButton_stopnie.clicked.connect(self.zmien_jednostki)
        self.radioButton_grady.clicked.connect(self.zmien_jednostki)
        self.radioButton_cm.clicked.connect(self.zmien_jednostke_dh)
        self.radioButton_mm.clicked.connect(self.zmien_jednostke_dh)
        self.radioButton_m_dh.clicked.connect(self.zmien_jednostke_dh)
        self.pushButton_pole.clicked.connect(self.pole)
        self.pushButton_poligon.clicked.connect(self.poligon)
        self.pushButton_odznacz_wszystko.clicked.connect(self.clear_selection)
        self.pushButton_wyczysc_konsole.clicked.connect(self.clear_console)
        self.pushButton_wczytaj_plik.clicked.connect(self.wczytaj)
        self.pushButton_odleglosc.clicked.connect(self.odleglosc)
        self.pushButton_azymut.clicked.connect(self.azymut)
        self.pushButton_az_odw.clicked.connect(self.az_odw)
        
    def licz_elementy(self):
        liczba_elementów = len(self.mMapLayerComboBox_layers.currentLayer().selectedFeatures())
        self.label_liczbaelementow.setText(str(liczba_elementów))
        return liczba_elementów
    
    
    
    def punkty(self):
        self.label_error.clear()
        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
        pkt = []
        for feature in selected_features:
            feature_geometry = feature.geometry().asPoint()
            x = feature_geometry[0]
            y = feature_geometry[1]
            pkt.append([float(x), float(y)])
        
        pkt = self.sortuj_punkty(pkt)
        return pkt
    
    def roznica_wysokosci(self):
        self.label_error.clear()
        self.radioButton_ary.setVisible(False)
        self.radioButton_hektary.setVisible(False)
        self.radioButton_m2.setVisible(False)
        self.radioButton_kilometry.setVisible(False)
        self.radioButton_metry.setVisible(False)
        self.radioButton_stopnie.setVisible(False)
        self.radioButton_grady.setVisible(False)
        self.radioButton_radiany.setVisible(False)
        # Sprawdzenie, czy w QGIS zaznaczono dokładnie dwa punkty
        if len(iface.activeLayer().selectedFeatures()) != 2:
            self.label_error.setText('Zaznacz dokładnie 2 punkty!')
            return
    
        # Pobranie zaznaczonych punktów
        warstwa = iface.activeLayer()
        zaznaczone_punkty = warstwa.selectedFeatures()
    
        # Sprawdzenie, czy atrybut elevation istnieje dla obu punktów
        if "h" not in zaznaczone_punkty[0].fields().names() or "h" not in zaznaczone_punkty[1].fields().names():
            iface.messageBar().pushWarning("Ostrzeżenie", "Wybrane punkty nie mają atrybutu wysokości.")
            return
    
        # Pobranie wysokości zaznaczonych punktów
        wysokosc_punktu_1 = zaznaczone_punkty[0]["h"]
        wysokosc_punktu_2 = zaznaczone_punkty[1]["h"]
    
        # Obliczenie różnicy wysokości
        dH = wysokosc_punktu_2 - wysokosc_punktu_1
        dH_txt = f'{dH:.3f} [m]'
        
        self.radioButton_mm.setVisible(True)
        self.radioButton_cm.setVisible(True)
        self.radioButton_m_dh.setVisible(True)
        
        # Wyświetlenie wyniku
        self.label_dH.setText(dH_txt)
        iface.messageBar().pushMessage("Wynik", f'Różnica wysokości między wybranymi punktami wynosi: {dH_txt}', level=Qgis.Info)
        return dH
    
    def odleglosc(self):
        self.radioButton_ary.setVisible(False)
        self.radioButton_hektary.setVisible(False)
        self.radioButton_m2.setVisible(False)
        self.radioButton_stopnie.setVisible(False)
        self.radioButton_grady.setVisible(False)
        self.radioButton_radiany.setVisible(False)
        self.radioButton_cm.setVisible(False)
        self.radioButton_m_dh.setVisible(False)
        self.radioButton_mm.setVisible(False)
        self.pushButton_az_odw.setVisible(False)
        
        self.label_error.clear()

        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
    
        if len(selected_features) != 2:
            self.label_error.setText('Zaznacz dokładnie 2 punkty!')
            return
    
        X = []
        Y = []

        for feature in selected_features:
            feature_geometry = feature.geometry().asPoint()
            x = feature_geometry[0]
            y = feature_geometry[1]
            X.append(float(x))
            Y.append(float(y))
    
        dx = X[1] - X[0]
        dy = Y[1] - Y[0]
    
        odl = sqrt(dx**2 + dy**2)
        odl_txt = f'{odl:.3f} [m]'
        
        self.radioButton_kilometry.setVisible(True)
        self.radioButton_metry.setVisible(True)
        self.label_odleglosc.setText(odl_txt)
        wynik_str = f'Odległość odcinka między zaznaczonymi punktami wynosi {odl:.3f} [m]'
        iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)
    
        return odl
    
    def azymut(self):
        self.radioButton_kilometry.setVisible(False)
        self.radioButton_metry.setVisible(False)
        self.radioButton_stopnie.setVisible(False)
        self.radioButton_grady.setVisible(False)
        self.radioButton_radiany.setVisible(False)
        self.radioButton_cm.setVisible(False)
        self.radioButton_m_dh.setVisible(False)
        self.radioButton_mm.setVisible(False)
        self.pushButton_az_odw.setVisible(False)
    
        self.label_error.clear()

        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()

        if len(selected_features) != 2:
            self.label_error.setText('Zaznacz dokładnie 2 punkty!')
            return
    
        X = []
        Y = []

        for feature in selected_features:
            feature_geometry = feature.geometry().asPoint()
            y = feature_geometry[0]
            x = feature_geometry[1]
            X.append(float(x))
            Y.append(float(y))

        dx = X[1] - X[0]
        dy = Y[1] - Y[0]
        
        if dx == 0 and dy == 0:
            self.label_error.setText('Punkty są identyczne!')
            return
    
        azymut_rad = atan2(dy, dx)
        if azymut_rad < 0:
            azymut_rad = azymut_rad + 2 * pi
        elif azymut_rad > (2 * pi):
            azymut_rad = azymut_rad - 2 * pi
    
        self.radioButton_stopnie.setVisible(True)
        self.radioButton_grady.setVisible(True)
        self.radioButton_radiany.setVisible(True)
        if not self.label_az_odw.text():      
            self.pushButton_az_odw.setVisible(True)
        
        self.label_azymut.setText(f'{azymut_rad:.7f} [rad]')
        wynik_str = f'Azymut między zaznaczonymi punktami wynosi {azymut_rad:.7f} [rad]'
        iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)
    
        return azymut_rad
    
            
    def az_odw(self):
        az = self.azymut()
        if az > pi:
            az = az - pi
        elif az < pi:
            az = az + pi
        az_odw = az
        self.pushButton_az_odw.setVisible(False)
        self.label_az_odw.setText(f'{az_odw:.7f} [rad]')
        wynik_str = f'Azymut odwrotny między zaznaczonymi punktami wynosi {az_odw:.7f} [rad]'
        iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)
        return az_odw
        
    
    def pole(self):
        self.radioButton_kilometry.setVisible(False)
        self.radioButton_metry.setVisible(False)
        self.radioButton_stopnie.setVisible(False)
        self.radioButton_grady.setVisible(False)
        self.radioButton_radiany.setVisible(False)
        self.radioButton_cm.setVisible(False)
        self.radioButton_mm.setVisible(False)
        self.radioButton_m_dh.setVisible(False)
        self.pushButton_az_odw.setVisible(False)
        self.label_error.clear()
        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
        
        if len(selected_features) < 3:
            self.label_error.setText('Zaznacz więcej punktów')
            return
        
        str_punkty = len(selected_features)
        pkt = []
        for feature in selected_features:
            feature_geometry = feature.geometry().asPoint()
            X = feature_geometry.x()
            Y = feature_geometry.y()
            pkt.append([X, Y])
        pkt = self.sortuj_punkty(pkt)

        n = len(pkt)
        if n < 3:
            self.label_pole.setText('BŁĄD!')
            self.label_error.setText('Zaznacz więcej punktów!')
            iface.messageBar().pushWarning("Ostrzeżenie", "Zaznaczono zbyt mało punktów.")
            pole = 0
        
        else:
            pole = 0
            for i in range(n):
                P = (pkt[i][0] * pkt[(i+1) % n][1] - pkt[(i-1) % n][1] * pkt[i][0])
                pole += P
            
            pole = 0.5 * abs(pole)
            poletxt = f'{pole:.3f} [m2]'
            
            self.label_pole.setText(str(poletxt))
            self.radioButton_ary.setVisible(True)
            self.radioButton_hektary.setVisible(True)
            self.radioButton_m2.setVisible(True)
            
            wynik_str = f'Pole powierzchni figury o wybranych {str_punkty} wierzchołkach wynosi: {pole:.3f} [m2]'
            iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)
        return pole, str_punkty
            
    def zmien_jednostke_pole(self):
        pole_m, punkty_str = self.pole()
        if self.radioButton_ary.isChecked():
            pole_a = pole_m/100
            self.label_pole.setText(f'{pole_a:.3f} [a]')
            wynik_str = f'Pole powierzchni figury o wybranych {punkty_str} wierzchołkach wynosi: {pole_a:.3f} [a]'
        elif self.radioButton_hektary.isChecked():
            pole_ha = pole_m /10000
            self.label_pole.setText(f'{pole_ha:.3f} [ha]')
            wynik_str = f'Pole powierzchni figury o wybranych {punkty_str} wierzchołkach wynosi: {pole_ha:.3f} [ha]'
        elif self.radioButton_m2 .isChecked():
            self.label_pole.setText(f'{pole_m:.3f} [m2]')
            wynik_str = f'Pole powierzchni figury o wybranych {punkty_str} wierzchołkach wynosi: {pole_m:.3f} [m2]'
        else:
            self.label_pole.setText(f'{pole_m:.3f} [m2]')
            wynik_str = f'Pole powierzchni figury o wybranych {punkty_str} wierzchołkach wynosi: {pole_m:.3f} [m2]'
        iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)

    def zmien_jednostke_odl(self):
        odl_m = self.odleglosc()
        if self.radioButton_metry.isChecked():
            self.label_odleglosc.setText(f'{odl_m:.3f} [m]')
            wynik_str = f'Odległość odcinka między zaznaczonymi punktami wynosi {odl_m:.3f} [m]'
        elif self.radioButton_kilometry.isChecked():
            odl_km = odl_m/1000
            self.label_odleglosc.setText(f'{odl_km:.3f} [km]')
            wynik_str = f'Odległość odcinka między zaznaczonymi punktami wynosi {odl_km:.3f} [km]'
        else:
            self.label_odleglosc.setText(f'{odl_m:.3f} [m]')
            wynik_str = f'Odległość odcinka między zaznaczonymi punktami wynosi {odl_m:.3f} [m]'
        iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)
        
    def zmien_jednostke_dh(self):
        dh_m = self.roznica_wysokosci()
        if self.radioButton_cm.isChecked():
            dh_cm = dh_m * 100
            self.label_dH.setText(f'{dh_cm:.3f} [cm]')
            wynik_str = f'Różnica wysokości między wybranymi punktami wynosi: {dh_cm:.3f} [cm]'
        elif self.radioButton_mm.isChecked():
            dh_mm = dh_m * 1000
            self.label_dH.setText(f'{dh_mm:.3f} [mm]')
            wynik_str = f'Różnica wysokości między wybranymi punktami wynosi: {dh_mm:.3f} [mm]'
        elif self.radioButton_m_dh.isChecked():
            self.label_dH.setText(f'{dh_m:.3f} [m]')
            wynik_str = f'Różnica wysokości między wybranymi punktami wynosi: {dh_m:.3f} [m]'
        else:
            self.label_dH.setText(f'{dh_m:.3f} [m]')
            wynik_str = f'Różnica wysokości między wybranymi punktami wynosi: {dh_m:.3f} [m]'   
        iface.messageBar().pushMessage("Wynik", wynik_str , level=Qgis.Info)
        
    def zmien_jednostke_azymut(self):
        az_rad = self.azymut()
        if az_rad < 0:
            az_rad = az_rad + 2 * pi
        elif az_rad > (2 * pi):
            az_rad = az_rad - 2 * pi
        if self.radioButton_grady.isChecked():
            az_g = az_rad * 200/pi
            if az_g < 0:
                az_g = az_g + 400
            elif az_g > 400:
                az_g = az_g - 400
            self.label_azymut.setText(f'{az_g:.5f} [g]')
            wynik_str = f'Azymut między zaznaczonymi punktami wynosi {az_g:.5f} [g]'
        elif self.radioButton_stopnie.isChecked():
            az_deg = degrees(az_rad)
            if az_deg < 0:
                az_deg = az_deg + 360
            elif az_deg > 360:
                az_deg = az_deg - 360
            self.label_azymut.setText(f'{az_deg:.5f} [deg]')
            wynik_str = f'Azymut między zaznaczonymi punktami wynosi {az_deg:.5f} [deg]' 
        elif self.radioButton_radiany.isChecked():
            self.label_azymut.setText(f'{az_rad:.7f} [rad]')
            wynik_str = f'Azymut między zaznaczonymi punktami wynosi {az_rad:.7f} [rad]'
        else:
            self.label_azymut.setText(f'{az_rad:.7f} [rad]')
            wynik_str = f'Azymut między zaznaczonymi punktami wynosi {az_rad:.7f} [rad]'
        iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)
        
    def zmien_jednostke_az_odw(self):
        if not self.label_az_odw.text():
            return
        
        az_rad = self.az_odw()
        
        if az_rad < 0:
            az_rad = az_rad + 2 * pi
        elif az_rad > (2 * pi):
            az_rad = az_rad - 2 * pi
        if self.radioButton_grady.isChecked():
            az_g = az_rad * 200/pi
            if az_g < 0:
                az_g = az_g + 400
            elif az_g > 400:
                az_g = az_g - 400
            self.label_az_odw.setText(f'{az_g:.5f} [g]')
            wynik_str = f'Azymut odwrotny między zaznaczonymi punktami wynosi {az_g:.5f} [g]'
        elif self.radioButton_stopnie.isChecked():
            az_deg = degrees(az_rad)
            if az_deg < 0:
                az_deg = az_deg + 360
            elif az_deg > 360:
                az_deg = az_deg - 360
            self.label_az_odw.setText(f'{az_deg:.5f} [deg]')
            wynik_str = f'Azymut odwrotny między zaznaczonymi punktami wynosi {az_deg:.5f} [deg]' 
        elif self.radioButton_radiany.isChecked():
            self.label_az_odw.setText(f'{az_rad:.7f} [rad]')
            wynik_str = f'Azymut odwrotny między zaznaczonymi punktami wynosi {az_rad:.7f} [rad]'
        else:
            self.label_az_odw.setText(f'{az_rad:.7f} [rad]')
            wynik_str = f'Azymut odwrotny między zaznaczonymi punktami wynosi {az_rad:.7f} [rad]'
        iface.messageBar().pushMessage("Wynik", wynik_str, level=Qgis.Info)
        
    def zmien_jednostki(self):
        self.zmien_jednostke_az_odw()
        self.zmien_jednostke_azymut()
        
    
    def poligon(self):
        xy = self.punkty()
        if len(xy) < 3:
            self.label_error.setText('Za mało punktów')
            return
        
        #if len(xy) > 3:
         #   self.label_error.setText('Za dużo punktów')
          #  return
        
        #if len(xy) != 3:
         #   iface.messageBar().pushMessage("Ostrzeżenie", "Zaznacz dokładnie 3 punkty.", level=Qgis.Warning)
          #  return
    
        punkty = [QgsPointXY(point[0], point[1]) for point in xy]
        punkty.append(punkty[0])

        pol_geom = QgsGeometry.fromPolygonXY([punkty])
        

        if not pol_geom.isGeosValid():
            self.label_poligon.setText('Nieprawidłowa geometria poligonu')
            return
    
        crs = self.mMapLayerComboBox_layers.currentLayer().crs()
        poligon = QgsVectorLayer("Polygon?crs=" + crs.toWkt(), "poligon", "memory")

        if not poligon.isValid():
            self.label_poligon.setText('Nie udało się utworzyć warstwy poligonowej')
            return

        pol_provider = poligon.dataProvider()

        pol_fields = QgsFields()
        pol_fields.append(QgsField("nazwa", QVariant.String))
    
        pol_provider.addAttributes(pol_fields)
    
        poligon.updateFields()
        
        pol_feature = QgsFeature(pol_fields)
        pol_feature.setGeometry(pol_geom)
    
        if not pol_provider.addFeature(pol_feature):
            self.label_poligon.setText('Nie udało się dodać funkcji do warstwy poligonowej')
    
        QgsProject.instance().addMapLayer(poligon)
    
        #self.canvas.refresh()
        iface.messageBar().pushMessage("Poligon został utworzony", level=Qgis.Info)
        #self.label_poligon.setText('Poligon utworzony')

    def dobierz_kat(self, p, punkt_ref):
        dx = p[0] - punkt_ref[0]
        dy = p[1] - punkt_ref[1]
        kat = atan2(dy,dx)
        return kat

    def sortuj_punkty(self, xy):
        punkt_ref = [sum(p[0] for p in xy) / len(xy), sum(p[1] for p in xy) / len(xy)]
        xy_sort = sorted(xy, key=lambda p: self.dobierz_kat(p, punkt_ref))
        return xy_sort
            
    def closeEvent(self, event):
        super().closeEvent(event)
        self.label_pole.clear()
        self.label_azymut.clear()
        self.label_odleglosc.clear()
        self.label_liczbaelementow.clear()
        self.label_error.clear()
        self.label_az_odw.clear()
        self.label_dH.clear()
        self.radioButton_ary.setChecked(False)
        self.radioButton_hektary.setChecked(False)
        self.radioButton_m2.setChecked(False)
        self.radioButton_grady.setChecked(False)
        self.radioButton_radiany.setChecked(False)
        self.radioButton_stopnie.setChecked(False)
        self.radioButton_metry.setChecked(False)
        self.radioButton_kilometry.setChecked(False)
        
    def clear_console(self):
        iface.messageBar().clearWidgets()
        self.label_pole.clear()
        self.label_azymut.clear()
        self.label_odleglosc.clear()
        self.label_liczbaelementow.clear()
        self.label_error.clear()
        self.label_az_odw.clear()
        self.label_dH.clear()
        self.radioButton_ary.setChecked(False)
        self.radioButton_hektary.setChecked(False)
        self.radioButton_m2.setChecked(False)
        self.radioButton_grady.setChecked(False)
        self.radioButton_radiany.setChecked(False)
        self.radioButton_stopnie.setChecked(False)
        self.radioButton_metry.setChecked(False)
        self.radioButton_kilometry.setChecked(False)
        self.radioButton_m_dh.setChecked(False)
        self.radioButton_cm.setChecked(False)
        self.radioButton_mm.setChecked(False)
        self.radioButton_ary.setVisible(False)
        self.radioButton_hektary.setVisible(False)
        self.radioButton_m2.setVisible(False)
        self.radioButton_grady.setVisible(False)
        self.radioButton_radiany.setVisible(False)
        self.radioButton_stopnie.setVisible(False)
        self.radioButton_metry.setVisible(False)
        self.radioButton_kilometry.setVisible(False)
        self.radioButton_m_dh.setVisible(False)
        self.radioButton_cm.setVisible(False)
        self.radioButton_mm.setVisible(False)
        self.pushButton_az_odw.setVisible(False)
        
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
            layer = QgsVectorLayer(uri, "Nowa warstwa", "memory")
            provider = layer.dataProvider()
        
            for wiersz in wiersze:
                if wiersz[0] and wiersz[1]:  # Sprawdź, czy wartości nie są puste
                    try:
                        y = float(wiersz[0])
                        x = float(wiersz[1])
                        feature = QgsFeature()
                        point = QgsPointXY(x, y)
                        geometry = QgsGeometry.fromPointXY(point)
                        feature.setGeometry(geometry)
                        provider.addFeature(feature)
                    except ValueError:
                        QMessageBox.warning(self, "Błąd konwersji", "Wystąpił błąd podczas konwersji współrzędnych.")
        
            QgsProject.instance().addMapLayer(layer)