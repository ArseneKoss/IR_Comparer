""" @-@-@-IR Comparer by Arsène-@-@-@ """

# Importing modules

import matplotlib.pyplot as plt
import numpy as np
import os
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPalette, QColor, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QMainWindow
from PyQt5.QtCore import QTimer, Qt, QProcess
    
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Patch

import tkinter as tk
from tkinter import filedialog
import time

import range_slider # https://github.com/sleepbysleep/range_slider_for_Qt5_and_PyQt5/blob/master/pyqt5_ranger_slider/range_slider.py

import traceback

main_path = "/path/to/Images"
gen_path = "/path/to/ORCA_Extracter.py"

# Plotting an IR spectrum from .frq (with scaling factors)

def the_data(path, scaled=True):
    f = open(path)
    lines=f.readlines()[1:]
    frequencies=[]
    intensities=[]

    for line in lines:
        if scaled:
            frequencies.append(float(line.split()[3]))

        if not scaled:
            frequencies.append(float(line.split()[2]))

        intensities.append(float(line.split()[4]))

    return frequencies,intensities

# Experimental data

def exp_data(path):
    f = open(path,"r")
    lines=f.readlines()
    X,Y=[],[]

    for line in lines:
        X.append(float(line.split()[0]))
        Y.append(float(line.split()[1]))
    return X,Y

# The GUI

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.xlim = [3000,4000]
        self.thick_w=1.5
        self.label_size=14
        self.new_label_size=self.label_size
        self.show_y_bool = False

        self.ax_list=[None,None]
        self.subplot_titles = ['Experimental spectrum', 'Theoretical spectrum']

        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.ax_list[0] = self.fig.add_subplot(2,1,1)
        self.ax_list[0].set_title(self.subplot_titles[0] , fontsize=self.label_size)
        self.ax_list[0].set_xlim(self.xlim)
        self.ax_list[0].get_yaxis().set_visible(self.show_y_bool)

        self.ax_list[1] = self.fig.add_subplot(2,1,2, sharex=self.ax_list[0])
        self.ax_list[1].set_title(self.subplot_titles[1] , fontsize=self.label_size)
        self.ax_list[1].set_xlabel('Wavenumber (cm-1)', fontsize=self.label_size, labelpad=0)
        self.ax_list[1].get_yaxis().set_visible(self.show_y_bool)


        self.grid_bool = False

        for i in [0,1]:

            self.axis_beauty(i)

        self.fig.tight_layout(pad=0)
        super(MplCanvas, self).__init__(self.fig)

    def change_subplots(self, nb_axes, remadd):

        if remadd=="add":
            ratio=nb_axes/(nb_axes+0.5)

        if remadd=="rem":
            ratio=(nb_axes+0.5)/nb_axes

        self.label_size=self.new_label_size
        self.new_label_size=ratio*self.label_size

        self.make_grid(nb_axes)

    def make_grid(self, nb_axes):

        self.ax_list[-1].set_visible(False)


        for i in range(nb_axes-1):

            self.fig.delaxes(self.ax_list[i])

        self.ax_list=nb_axes*[None]
        self.subplot_titles = nb_axes*[None]

        if self.grid_bool:

            self.gs = self.fig.add_gridspec(nb_axes, hspace=0)
            self.ax_list = self.gs.subplots(sharex = True)

            for i in range(nb_axes-1):

                self.ax_list[i].set_title('')
                self.axis_beauty(i)

            self.ax_list[nb_axes-1].set_title('', fontsize=self.new_label_size)
            self.ax_list[nb_axes-1].set_xlabel('', fontsize=self.new_label_size, labelpad=0)

            self.axis_beauty(nb_axes-1)

        if not self.grid_bool:

            for i in range(nb_axes-1):

                self.ax_list[i]=self.fig.add_subplot(nb_axes, 1, i+1, sharex=self.ax_list[0])
                self.ax_list[i].set_title('Experimental spectrum')
                self.axis_beauty(i)

            self.ax_list[nb_axes-1] = self.fig.add_subplot(nb_axes,1,nb_axes, sharex=self.ax_list[0])
            self.ax_list[nb_axes-1].set_title('Theoretical spectrum', fontsize=self.new_label_size)
            self.ax_list[nb_axes-1].set_xlabel('Wavenumber (cm-1)', fontsize=self.new_label_size, labelpad=0)

            self.axis_beauty(nb_axes-1)

    def axis_beauty(self, axis_id):

        i = axis_id

        self.ax_list[i].tick_params(axis='both', labelsize=self.new_label_size)

        for side in ['bottom','left','top','right']:
            self.ax_list[i].spines[side].set_linewidth(self.thick_w)

        self.ax_list[i].xaxis.set_tick_params(which='major', size=10, width=self.thick_w, direction='out', top=False)
        self.ax_list[i].xaxis.set_tick_params(which='minor', size=7, width=self.thick_w, direction='out', top=False)
        self.ax_list[i].yaxis.set_tick_params(which='major', size=10, width=self.thick_w, direction='in', top=False)
        self.ax_list[i].yaxis.set_tick_params(which='minor', size=7, width=self.thick_w, direction='in', top=False)

        dx = self.xlim[1]-self.xlim[0]

        if dx>2000:
            major_loc = 500
            minor_loc_div = 5

        if dx>1000 and dx<=2000:
            major_loc = 250
            minor_loc_div = 5

        if dx>500 and dx<=1000:
            major_loc = 100
            minor_loc_div = 5

        if dx<=500 and dx>300:
            major_loc = 50
            minor_loc_div = 5

        if dx<=300 and dx>100:
            major_loc = 25
            minor_loc_div = 5

        if dx<=100 and dx>10:
            major_loc = 10
            minor_loc_div = 5

        if dx<=10:
            major_loc = 1
            minor_loc_div = 5

        self.ax_list[i].xaxis.set_major_locator(MultipleLocator(major_loc))
        self.ax_list[i].xaxis.set_minor_locator(MultipleLocator(major_loc / minor_loc_div))

        self.ax_list[i].get_yaxis().set_visible(self.show_y_bool)




class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Defining main window properties
        self.path = main_path
        self.setWindowTitle("IR_Comparer")
        self.setWindowIcon(QIcon(self.path + "\\laser-clipart.ico"))
        self.setGeometry(0, 0, 600, 800)

        # Defining instances
        self.p = None

        fontsize = 12
        self.button_next = QtWidgets.QPushButton('Next')
        self.button_previous = QtWidgets.QPushButton('Previous')
        self.button_open = QtWidgets.QPushButton('Open')
        self.box_goto = QtWidgets.QSpinBox()

        self.label_name = QtWidgets.QLabel('Name : ', self)
        self.label_name.setFont(QFont('Arial', fontsize, QFont.Bold))

        self.label_expname = QtWidgets.QLabel('Exp Name : ', self)
        self.label_expname.setFont(QFont('Arial', fontsize, QFont.Bold))

        self.label_list = QtWidgets.QLabel('Selected List : ', self)
        self.label_list.setFont(QFont('Arial', fontsize, QFont.Bold))

        self.label_namelist = QtWidgets.QLabel('', self)

        self.label_E0K = QtWidgets.QLabel('\u0394E+ZPE : ', self)
        self.label_E0K.setFont(QFont('Arial', fontsize, QFont.Bold))

        self.label_E298K = QtWidgets.QLabel('\u0394G_298K : ', self)
        self.label_E298K.setFont(QFont('Arial', fontsize, QFont.Bold))

        self.button_theory_folder = QtWidgets.QPushButton('Select folder for theory spectra')
        self.button_generate_frq = QtWidgets.QPushButton('Select folder to generate frequency files')
        self.button_experiments_folder = QtWidgets.QPushButton('Select experimental spectrum')
        self.button_experiments_folder_add = QtWidgets.QPushButton('Add experimental spectrum')
        self.button_experiments_folder_rm = QtWidgets.QPushButton('Remove last experimental spectrum')
        self.button_add = QtWidgets.QPushButton('Add')
        self.button_remove = QtWidgets.QPushButton('Remove')
        self.button_save_im = QtWidgets.QPushButton('Save Spectra')
        self.button_save_list = QtWidgets.QPushButton('Save List')
                
        self.slider = range_slider.RangeSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimumHeight(30)
        self.slider.setMinimum(0)
        self.slider.setMaximum(4000)
        self.slider.setLow(3000)
        self.slider.setHigh(4000)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)

        self.scaled_check = QtWidgets.QCheckBox("Scaled Frequencies")
        self.scaled_check.setCheckState(True)
        self.scaled_check.setTristate(False)
        self.scaled_check.toggled.connect(self.scale_frequencies)

        self.button_rescale = QtWidgets.QPushButton('Scale on exp')

        self.show_y_check = QtWidgets.QCheckBox('Show y axis')
        self.show_y_check.setCheckState(False)
        self.show_x_bool = self.show_y_check.isChecked()
        self.show_y_check.setTristate(False)

        self.show_x_check = QtWidgets.QCheckBox('Show x axis')
        self.show_x_check.setCheckState(True)
        self.show_x_bool = self.show_x_check.isChecked()
        self.show_x_check.setTristate(False)

        self.show_title_check = QtWidgets.QCheckBox('Show title')
        self.show_title_check.setCheckState(False)
        self.show_title_bool = self.show_title_check.isChecked()
        self.show_title_check.setTristate(False)
        
        self.show_barlbl_check = QtWidgets.QCheckBox('Show main vibrating atom')
        self.show_barlbl_check.setCheckState(False)
        self.show_barlbl_bool = self.show_title_check.isChecked()
        self.show_barlbl_check.setTristate(False)

        self.popup_window = QtWidgets.QMessageBox()
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)

        # Set icons and connections

        self.button_next.setIcon(QIcon(self.path + '\\right-arrow.png'))
        self.button_previous.setIcon(QIcon(self.path + '\\left-arrow.png'))
        self.button_open.setIcon(QIcon(self.path + '\\chemcraft.png'))
        self.button_theory_folder.setIcon(QIcon(self.path + '\\folder.png'))
        self.button_generate_frq.setIcon(QIcon(self.path + '\\folder.png'))
        self.button_experiments_folder.setIcon(QIcon(self.path + '\\bloc-note.png'))
        self.button_experiments_folder_rm.setIcon(QIcon(self.path + '\\minus.png'))
        self.button_experiments_folder_add.setIcon(QIcon(self.path + '\\plus.png'))
        self.button_add.setIcon(QIcon(self.path + '\\plus.png'))
        self.button_remove.setIcon(QIcon(self.path + '\\minus.png'))
        self.button_save_im.setIcon(QIcon(self.path + '\\save.png'))
        self.button_save_list.setIcon(QIcon(self.path + '\\save.png'))
        self.button_rescale.setIcon(QIcon(self.path + '\\regle.png'))
        self.popup_window.setWindowIcon(QIcon(self.path + "\\laser-clipart.ico"))

        self.button_next.clicked.connect(self.update_plot_next)
        self.button_previous.clicked.connect(self.update_plot_previous)
        self.button_open.clicked.connect(self.open_structure)
        self.box_goto.valueChanged.connect(self.update_plot_goto)
        self.button_theory_folder.clicked.connect(self.pick_new_theo)
        self.button_generate_frq.clicked.connect(self.gen_freq)
        self.button_experiments_folder.clicked.connect(self.pick_new_exp)
        self.button_experiments_folder_add.clicked.connect(self.add_new_exp)
        self.button_experiments_folder_rm.clicked.connect(self.remove_exp)
        self.button_add.clicked.connect(self.add_name)
        self.button_remove.clicked.connect(self.remove_name)
        self.button_save_im.clicked.connect(self.save_im)
        self.button_save_list.clicked.connect(self.save_list)
        self.scaled_check.toggled.connect(self.scale_frequencies)
        self.button_rescale.clicked.connect(self.rescale_on_exp)
        self.show_y_check.toggled.connect(self.show_y)
        self.show_x_check.toggled.connect(self.show_x)
        self.show_title_check.toggled.connect(self.show_title)
        self.show_barlbl_check.toggled.connect(self.show_barlbl)
        self.slider.sliderMoved.connect(self.change_frequency_range)

        # Defining layout

        grid_layout = QtWidgets.QGridLayout()

        # Adding widgets to grid layout

        grid_layout.addWidget(self.button_experiments_folder, 0, 0, 1, 4)
        grid_layout.addWidget(self.button_theory_folder, 0, 4, 1, 4)
        grid_layout.addWidget(self.button_experiments_folder_add, 1, 0, 1, 2)
        grid_layout.addWidget(self.button_experiments_folder_rm, 1, 2, 1, 2)
        grid_layout.addWidget(self.button_generate_frq, 1, 4, 1, 4)
        grid_layout.addWidget(toolbar, 2, 0, 1, 3)
        grid_layout.addWidget(self.show_y_check, 2, 2, 1, 1)
        grid_layout.addWidget(self.show_x_check, 2, 3, 1, 1)
        grid_layout.addWidget(self.show_title_check, 2, 4, 1, 1)
        grid_layout.addWidget(self.show_barlbl_check, 2, 5, 1, 1)
        grid_layout.addWidget(self.scaled_check, 2, 6, 1, 2)
        grid_layout.addWidget(self.canvas, 3, 0, 12, 6)
        grid_layout.addWidget(self.label_expname, 5, 6, 1, 2)
        grid_layout.addWidget(self.label_name, 10, 6, 1, 2)
        grid_layout.addWidget(self.label_E0K, 11, 6, 1, 1)
        grid_layout.addWidget(self.label_E298K, 12, 6, 1, 1)
        grid_layout.addWidget(self.label_list, 13, 6, 1, 1)
        grid_layout.addWidget(self.label_namelist, 14, 6, 2, 1)
        i=16
        grid_layout.addWidget(self.slider, i, 0, 1, 6)
        grid_layout.addWidget(self.button_rescale, i, 6, 1, 1)
        grid_layout.addWidget(self.box_goto, i, 7, 1, 1)
        grid_layout.addWidget(self.button_previous, i+1, 0, 1, 3)
        grid_layout.addWidget(self.button_next, i+1, 3, 1, 3)
        grid_layout.addWidget(self.button_add, i+1, 6, 1, 1)
        grid_layout.addWidget(self.button_remove, i+1, 7, 1, 1)
        grid_layout.addWidget(self.button_open, i+2, 0, 1, 6)
        grid_layout.addWidget(self.button_save_im, i+2, 6, 1, 1)
        grid_layout.addWidget(self.button_save_list, i+2, 7, 1, 1)

        
        
        # Setting the layout to the central widget
        main_page_widget = QtWidgets.QWidget()
        main_page_widget.setLayout(grid_layout)
        self.setCentralWidget(main_page_widget)

        #Defining variables
        self.nb_axes=2
        self.name_string=""
        self.saved_name_list=[]
        self.legend_elements=[
        #Patch(color='dimgrey', label='CH'),
        #Patch(color='red', label='OH'),
        #Patch(color='royalblue', label='NH'),
        #Patch(color='green', label='NH2s'),
        #Patch(color='limegreen', label='NH2a')
        ]
        self.exp_list=[None]
        self.exp_name_list=[None]
        self.xlim=[3000,4000]
        self.scaled_bool=True
        self.frq_name=''

        #Display
        self.canvas.draw()
        self.showMaximized()

    def update_plot_next(self):
        try: self.name_list
        except:
            self.popup_window.setWindowTitle("Warning")
            self.popup_window.setText("No theory spectrum has been selected.")
            self.popup_window.setIcon(QtWidgets.QMessageBox.Warning)
            self.popup_window.exec_()
        else:
            if self.index<len(self.name_list)-1:
                self.box_goto.setValue(self.box_goto.value()+1)

    def update_plot_previous(self):
        try: self.name_list
        except:
            self.popup_window.setWindowTitle("Warning")
            self.popup_window.setText("No theory spectrum has been selected.")
            self.popup_window.setIcon(QtWidgets.QMessageBox.Warning)
            self.popup_window.exec_()
        else:
            if self.index>0:
                self.box_goto.setValue(self.box_goto.value()-1)

    def update_plot_goto(self):
        self.index=self.box_goto.value()

        try: self.X2
        except: None
        else: self.plot_theo()

        try: self.X1
        except: None
        else: self.plot_exp()

    def gen_freq(self):

        try: exec(open(gen_path, encoding="utf-8").read())
        except:
            error_message = traceback.format_exc()
            print(f"An error occurred: {error_message}")
        else:
            self.popup_window.setWindowTitle("Information")
            self.popup_window.setText("Files have been generated.")
            self.popup_window.setIcon(QtWidgets.QMessageBox.Information)
            self.popup_window.setGeometry(100, 100, 500, 200)
            self.popup_window.exec_()

    def pick_new_exp(self):
        self.exp_file = QtWidgets.QFileDialog.getOpenFileName(caption='Please select conformer file', filter='*.txt *.dat')[0]

        if self.exp_file == '':
            return None

        self.exp_name=self.exp_file.split('/')[-1]

        self.exp_name_list[-1] = self.exp_name

        self.X1=exp_data(self.exp_file)[0]
        self.Y1=exp_data(self.exp_file)[1]
        self.exp_list[-1]=(self.X1,self.Y1)

        self.plot_exp()

    def add_new_exp(self):

        if self.exp_name_list[0]==None:
            self.popup_window.setWindowTitle("Warning")
            self.popup_window.setText("Please first select an experimental spectrum.")
            self.popup_window.setIcon(QtWidgets.QMessageBox.Warning)
            self.popup_window.exec_()
            return None

        self.exp_file = QtWidgets.QFileDialog.getOpenFileName()[0]

        if self.exp_file == '':
            return None

        self.nb_axes+=1
        self.canvas.change_subplots(self.nb_axes, 'add')

        self.exp_name=self.exp_file.split('/')[-1]
        self.exp_name_list.append(self.exp_name)

        self.X1=exp_data(self.exp_file)[0]
        self.Y1=exp_data(self.exp_file)[1]
        self.exp_list.append((self.X1,self.Y1))

        try: self.name_list
        except: None
        else: self.plot_theo()
        
        self.plot_exp()

    def remove_exp(self):

        if self.nb_axes>2:

            self.nb_axes-=1
            self.exp_list.pop()
            self.exp_name_list.pop()

            self.canvas.ax_list[self.nb_axes-1].cla()
            self.canvas.ax_list[self.nb_axes-1].axis("off")
            self.canvas.ax_list[self.nb_axes].axis("off")
            self.canvas.ax_list[self.nb_axes].set_title('')
            self.canvas.ax_list[self.nb_axes].get_legend().remove()

            self.canvas.change_subplots(self.nb_axes, 'rem')

            self.plot_exp()

            try: self.name_list
            except: None
            else: self.plot_theo()

        else:
            self.popup_window.setWindowTitle("Warning")
            self.popup_window.setText("Cannot remove more spectra")
            self.popup_window.setIcon(QtWidgets.QMessageBox.Warning)
            self.popup_window.exec_()

    def pick_new_theo(self):

        self.index=0

        self.energy_file = QtWidgets.QFileDialog.getOpenFileName(caption='Please select Energy.txt file', filter='*.txt')[0]
        self.frq_dir = '/'.join(self.energy_file.split('/')[:-1])+'/frq_files'
        
        if not os.path.exists(self.frq_dir):
            print('No frq_dir file found')
            return None
        #self.frq_dir = QtWidgets.QFileDialog.getExistingDirectory(caption='Please select frq files folder')

        if self.frq_dir == '' or self.energy_file=='':
            return None

        self.name_list=np.loadtxt(self.energy_file, dtype='str',skiprows=1, usecols=0)
        self.E0K=np.loadtxt(self.energy_file,skiprows=1, usecols=1)
        self.E298K=np.loadtxt(self.energy_file,skiprows=1, usecols=3)

        try: self.name_list[0] # If only one element in the list np.loadtxt will not generate a list
        except: 
            self.name_list = [str(self.name_list)]
            self.E0K = [float(self.E0K)]
            self.E298K = [float(self.E298K)]

        self.box_goto.setMaximum(len(self.name_list)-1)
        self.box_goto.setMinimum(0)

        self.plot_theo()

        if self.exp_name_list[0]!=None:
            self.plot_exp()

    def plot_exp(self):

        expname = ''

        if self.nb_axes>=2:

            for i in range(self.nb_axes-1):
                expname += self.exp_name_list[i]+'\n'
                self.canvas.ax_list[i].cla()
                self.canvas.ax_list[i].plot(self.exp_list[i][0], self.exp_list[i][1], label=self.exp_name_list[i], color = 'black', linewidth = 3)

                subplot_title = 'Experimental spectrum: '+self.exp_name_list[i]
                self.canvas.subplot_titles[i]=subplot_title

                if self.show_title_bool:
                    self.canvas.ax_list[i].set_title(subplot_title, fontsize=self.canvas.new_label_size)
                if not self.show_title_bool:
                    self.canvas.ax_list[i].set_title('')

                if self.show_x_bool:
                    self.canvas.ax_list[i].get_xaxis().set_visible(True)

                if not self.show_x_bool:
                    self.canvas.ax_list[i].get_xaxis().set_visible(False)

                self.canvas.xlim = self.xlim
                self.canvas.axis_beauty(i)
                self.canvas.ax_list[i].set_xlim(self.xlim)

                try: self.X2
                except: None
                else:
                    for x in self.X2:
                        self.canvas.ax_list[i].axvline(x,color=self.bar_colour[self.X2.index(x)],linestyle='dashed',alpha=self.Y2[self.X2.index(x)]/max(self.Y2))

            self.canvas.draw()

        self.label_expname.setText("Exp Name :\n"+expname)

    def plot_theo(self):

        self.canvas.ax_list[-1].cla()

        self.frq_name=self.name_list[self.index]+".frq"
        self.frq_path = self.frq_dir + '/' + self.frq_name

        self.X2=the_data(self.frq_path, self.scaled_bool)[0]
        self.Y2=the_data(self.frq_path, self.scaled_bool)[1]
        self.frq_group=np.loadtxt(self.frq_path,dtype='str',skiprows=1, usecols=0)
        self.bar_colour=[]

        self.legend_elements=[]
        Cleg, Oleg, Nleg, Nsleg, Nasleg, COleg, Fleg = True, True, True, True, True, True, True
        
        for group in self.frq_group:
            
            if group[0]=='C' and group[-1]=='O':
                self.bar_colour.append('darkorange')
                if COleg:
                    self.legend_elements.append(Patch(color='darkorange', label='CO'))
                    COleg = False

            elif 'C' in group:
                self.bar_colour.append('dimgrey')
                if Cleg:
                    Cleg = False
                    self.legend_elements.append(Patch(color='dimgrey', label='CH'))

            elif 'O' in group:
                self.bar_colour.append('red')
                if Oleg:
                    self.legend_elements.append(Patch(color='red', label='OH'))
                    Oleg = False

            elif 'N' in group and '(s)' in group:
                self.bar_colour.append('green')
                if Nsleg:
                    self.legend_elements.append(Patch(color='green', label='NH2s'))
                    Nsleg = False

            elif 'N' in group and '(as)' in group:
                self.bar_colour.append('limegreen')
                if Nasleg:
                    self.legend_elements.append(Patch(color='limegreen', label='NH2as'))
                    Nasleg = False

            elif 'N' in group:
                self.bar_colour.append('royalblue')
                if Nleg:
                    self.legend_elements.append(Patch(color='royalblue', label='NH'))
                    Nleg = False
                    
            elif 'F' in group:
                self.bar_colour.append('orange')
                if Fleg:
                    self.legend_elements.append(Patch(color='orange', label='F'))
                    Fleg = False
                    
        subplot_title = 'Theoretical spectrum: ' + self.name_list[self.index]
        self.canvas.subplot_titles[self.nb_axes-1]=subplot_title
        
        ax = self.canvas.ax_list[self.nb_axes-1]

        if self.show_title_bool:
            ax.set_title(subplot_title, fontsize=self.canvas.new_label_size)
        if not self.show_title_bool:
            ax.set_title('')

        if self.show_x_bool:
            ax.set_xlabel('Wavenumber (cm-1)', fontsize=self.canvas.new_label_size, labelpad=0)
            
        
        bars=ax.bar(self.X2,self.Y2,width=5,color=self.bar_colour)
        
        if self.show_barlbl_bool:
            ax.bar_label(bars, labels=self.frq_group, padding=3)#, color = self.bar_colour)
            
        self.canvas.xlim = self.xlim
        self.canvas.axis_beauty(self.nb_axes-1)

        for x in self.X2:
            ax.axvline(x,color=self.bar_colour[self.X2.index(x)],linestyle='dashed',alpha=self.Y2[self.X2.index(x)]/max(self.Y2))

        self.label_name.setText("Name : "+str(self.name_list[self.index]))
        self.label_E0K.setText("Energy at 0K : "+str(format(self.E0K[self.index],".2f"))+" kJ/mol")
        self.label_E298K.setText("Energy at 298K : "+str(format(self.E298K[self.index],".2f"))+" kJ/mol")

        ax.legend(handles=self.legend_elements, loc='right')
        self.canvas.ax_list[0].set_xlim(self.xlim)
        self.canvas.draw()

    def change_frequency_range(self, low_value, high_value):

        self.xlim = [low_value, high_value]
        self.canvas.xlim = self.xlim

        for i in range(len(self.canvas.ax_list)):
            self.canvas.axis_beauty(i)

        self.canvas.ax_list[0].set_xlim(self.xlim)
        self.canvas.draw()


    def save_im(self):
        self.save_name = QtWidgets.QFileDialog.getSaveFileName(caption='Save image', filter='*.png')[0]

        if self.save_name == '':
            return None

        self.canvas.fig.savefig(self.save_name,dpi=500, format='png')
        self.popup_window.setWindowTitle("Information")
        self.popup_window.setText("The image has been saved!")
        self.popup_window.setIcon(QtWidgets.QMessageBox.Information)
        self.popup_window.setGeometry(100, 100, 500, 200)
        self.popup_window.exec_()

    def save_list(self):
        self.save_name = QtWidgets.QFileDialog.getSaveFileName()[0]

        if self.save_name == '':
            return None

        self.f=open(self.save_name+'.txt','a')

        for name in self.saved_name_list:
            self.f.write(name+'\n')

        self.f.close()
        self.popup_window.setWindowTitle("Information")
        self.popup_window.setText("The list has been saved!")
        self.popup_window.setIcon(QtWidgets.QMessageBox.Information)
        self.popup_window.setGeometry(100, 100, 500, 200)
        self.popup_window.exec_()

    def add_name(self):
        if self.name_list[self.index] not in self.saved_name_list:
            self.saved_name_list.append(self.name_list[self.index])
            self.name_string+=self.name_list[self.index]+"\n"
            self.label_namelist.setText(self.name_string)

        else:
            self.popup_window.setWindowTitle("Information")
            self.popup_window.setText("The name is already in the list.")
            self.popup_window.exec_()

    def remove_name(self):
        if self.name_list[self.index] in self.saved_name_list:
            self.saved_name_list.remove(self.name_list[self.index])
            self.name_string=self.name_string.replace(self.name_list[self.index]+"\n","")
            self.label_namelist.setText(self.name_string)

        else:
            self.popup_window.setWindowTitle("Information")
            self.popup_window.setText("The name is not in the list.")
            self.popup_window.exec_()

    def open_structure(self):
        
        def alert():
            self.popup_window.setWindowTitle("Warning")
            self.popup_window.setText("No .out or .xyz file found to open.")
            self.popup_window.setIcon(QtWidgets.QMessageBox.Warning)
            self.popup_window.exec_()
            
        try:
            self.name_list
        except:
            self.popup_window.setWindowTitle("Warning")
            self.popup_window.setText("No theory spectrum has been selected.")
            self.popup_window.setIcon(QtWidgets.QMessageBox.Warning)
            self.popup_window.exec_()
        else:
            out_path = '/'.join(self.frq_dir.split('/')[:-1])
            xyz_path = '/'.join(self.frq_dir.split('/')[:-1]) + '/xyz_opt/'
            xyz_name = self.name_list[self.index]+'_'+str(self.index+1)+'.xyz'
            
            if self.name_list[self.index]+".out" in os.listdir(out_path):
                
                out_path += '/' + self.name_list[self.index]+".out"
                
                try: os.startfile(out_path)
                except: 
                    alert()
                    
            elif xyz_name in os.listdir(xyz_path):
                
                xyz_path += '/'+xyz_name
                
                try: os.startfile(xyz_path)
                except: alert()
                
            else:
                alert()
                

    def scale_frequencies(self):

        self.scaled_bool = self.scaled_check.isChecked()

        if self.frq_name!='':
            self.plot_theo()

        if self.exp_name_list[0]!=None:
            self.plot_exp()

    def rescale_on_exp(self):

        try:
            self.X1
        except:
            self.popup_window.setWindowTitle("Warning")
            self.popup_window.setText("No experimental spectrum has been selected.")
            self.popup_window.setIcon(QtWidgets.QMessageBox.Warning)
            self.popup_window.exec_()

        else:
            self.xlim = [min(self.X1), max(self.X1)]
            self.canvas.ax_list[0].set_xlim(self.xlim)
            self.canvas.xlim = self.xlim

            for i in range(len(self.canvas.ax_list)):
                self.canvas.axis_beauty(i)

            self.canvas.draw()

            self.slider.setLow(int(min(self.X1)))
            self.slider.setHigh(int(max(self.X1)))

    def show_y(self):

        self.show_y_bool = self.show_y_check.isChecked()
        self.canvas.show_y_bool = self.show_y_bool

        for i in range(len(self.canvas.ax_list)):
            if self.show_y_bool:
                self.canvas.ax_list[i].get_yaxis().set_visible(True)
            else:
                self.canvas.ax_list[i].get_yaxis().set_visible(False)

        self.canvas.draw()

    def show_x(self):

        self.show_x_bool = self.show_x_check.isChecked()

        for i in range(len(self.canvas.ax_list)-1):

            if self.show_x_bool:
                self.canvas.ax_list[i].get_xaxis().set_visible(True)
            else:
                self.canvas.ax_list[i].get_xaxis().set_visible(False)

        self.canvas.draw()
        self.create_grid()

    def show_title(self):

        self.show_title_bool = self.show_title_check.isChecked()

        for i in range(len(self.canvas.ax_list)):
            if self.show_title_bool:
                self.canvas.ax_list[i].set_title(self.canvas.subplot_titles[i], fontsize=self.canvas.new_label_size)
            else:
                self.canvas.ax_list[i].set_title('')

        self.canvas.draw()
        self.create_grid()
        
    def show_barlbl(self):
        
        self.show_barlbl_bool = self.show_barlbl_check.isChecked()
        self.plot_theo()

        self.canvas.draw()
        self.create_grid()

    def create_grid(self):

        if not self.show_title_bool and not self.show_x_bool and not self.canvas.grid_bool:
            self.canvas.grid_bool = True
            self.canvas.make_grid(self.nb_axes)

            if self.exp_name_list[0]!=None:
                self.plot_exp()
            if self.frq_name!='':
                self.plot_theo()

        if (self.show_title_bool or self.show_x_bool) and self.canvas.grid_bool:
            self.canvas.grid_bool = False
            self.canvas.make_grid(self.nb_axes)

            if self.exp_name_list[0]!=None:
                self.plot_exp()
            if self.frq_name!='':
                self.plot_theo()

        self.canvas.draw()

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()