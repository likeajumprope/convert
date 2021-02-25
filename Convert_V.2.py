#!/usr/bin/python
#
# This file is part of CONVERT
# Copyright (C) 2015  Grazia Rutigliano <grazia.rutigliano.gr@gmail.com>
#                     Juri Lelli <juri.lelli@gmail.com>
#                     Paolo Fusar-Poli <paolo.fusar-poli@kcl.ac.uk>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
from tkinter import Frame, Tk, BOTH, Text, Menu, END, Scrollbar #no need to install extra packages here, as tkinter and openpyxl come with VS code python version
import tkinter.filedialog
import tkinter.messagebox
from CaarmsSips import CaarmsSips
import openpyxl

help = """
CONVERT is a Phyton application which implements the conversions between the psychometric diagnostic instruments\n
used to interview help-seeking subjects for a clinical high risk for psychosis (HR), according to the algorithm\n
and equipercentile linking table proposed by Fusar-Poli et al. in Schizophr Bull 2015 (under review).\n
The software takes as input a *.xlsx file having the same structure as the template provided.\n
Clicking on File menu/Open, the user can browse the directories and open the selected input file.\n
Functions included in the software are:\n
1. CAARMS to SIPS\n
2. SIPS to CAARMS\n
They are accessible via the Run pull-down menu.\n
The software provides the conversion of the diagnostic subgroup across the two instruments, and of the individual scores\n
of each severity or frequency subscale. The latter were provided for analytical purposes only. We do not recommend\n
to use the converted severity or frequency to assign the diagnostic subgroup as a first step.\n
The software requires the following clinical information, which should be part of the routine psychometric assessment:\n
1.  Are the symptoms better explained by comorbidities? Yes/No\n
2.  Are the symptoms disorganising and dangerous? Yes/No\n
3.  GAF drop > 30%? Yes/No\n
When these data are missing, the user will be given warning messages.\n
The user can then decide to interrupt the program, enter the data in the input *.xlsx file and rerun the program,\n
or to proceed and exclude the cases. In both cases the subjects with missing info will be listed in the main screen.\n
The Save as item in the File menu allows to save the output *.xlsx file in the selected directory.\n
The Help pull-down menu displays a basic guide about the software use.\n
When using CONVERT please cite: Fusar-Poli P, Cappucciati M, Beverly Q, Rutigliano G, Bonoldi I, Lelli J, Kaar SJ, Gago E, Rocchetti M, Rashmi P,\n
Bhavsar V, Tognin S, Badger S, Calem M, Perez J, McGuire P. Towards a standard psychometric diagnostic interview for people at high clinical risk\n
for psychosis: CAARMS vs SIPS. Schizophrenia Bulletin 2015 (under review).\n
"""

credits = """
CONVERT\n
Authors:\n
Juri Lelli\n
Grazia Rutigliano\n
Paolo Fusar-Poli\n
"""



class Convert(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent        
        self.initUI()
        self.caarms_sips = None
        self.file_in = '' #input file here?
        self.def_file_out = 'caarms_sips_output.xlsx'
        self.file_out = self.def_file_out
        
    def initUI(self):
      
        self.parent.title("CAARMS/SIPS converter")
        self.pack(fill=BOTH, expand=1)
        
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=self.onOpen)
        fileMenu.add_command(label="Save as", command=self.onSave)
        menubar.add_cascade(label="File", menu=fileMenu)        

        runMenu = Menu(menubar)
        runMenu.add_command(label="CAARMS to SIPS", command=self.onCaarms) #menu option to convert CAARMS to SIPS
        runMenu.add_command(label="SIPS to CAARMS", command=self.onSips) #menu option to convert SIPS to CAARMS
        menubar.add_cascade(label="Run", menu=runMenu)        

        helpMenu = Menu(menubar)
        helpMenu.add_command(label="Help", command=self.onHelp)
        helpMenu.add_command(label="Credits", command=self.onCredits)
        menubar.add_cascade(label="Help", menu=helpMenu)
        
        self.txt = Text(self)
        self.scr = Scrollbar(self)
        self.scr.pack(side="right", fill="y", expand=False)
        self.txt.pack(fill=BOTH, expand=1)
        self.txt.configure(state='normal')
        self.txt.insert(END, help)
        self.txt.configure(state='disabled')


    def onOpen(self): #Open command
      
        ftypes = [('Excel DBs', '*.xlsx')]
        dlg = tkinter.filedialog.Open(self, filetypes = ftypes)
        self.file_in = dlg.show()

        if self.file_in != '':
            self.txt.configure(state='normal')
            self.txt.delete(1.0, END)
            self.txt.insert(END, "input DB: {}\n\n".format(self.file_in))
            self.txt.configure(state='disabled')

    def onSave(self):
        ftypes = [('Excel DBs', '*.xlsx')]
        self.file_out = tkinter.filedialog.asksaveasfilename(defaultextension='.xlsx',
                                                       filetypes=ftypes)
        if self.file_out == '':
            self.file_out = self.def_file_out

        self.txt.configure(state='normal')
        self.txt.delete(1.0, END)
        self.txt.insert(END, "output DB: {}\n\n".format(self.file_out))
        self.txt.configure(state='disabled')

    def onCaarms(self):     # on choosing conversion CAARMS to SIPS
        self.caarms_sips = CaarmsSips(file_in = self.file_in) #runs the CaarmsSips.py code, using the input file defined at the start

        df = self.caarms_sips.caarms_to_sips()
        self.txt.configure(state='normal')
        self.txt.insert(END, "converted: {}\n\n".format(self.file_in))
        self.txt.configure(state='disabled')

        df = self.remove_missing_data(df, 'SIPS') #run remove missing data function for CAARMS

        text = df[CaarmsSips.labels].to_string()
        self.txt.configure(state='normal')
        self.txt.insert(END, "\n\nResult (showing {} patients):\n".format(len(df))) #tells you how many participants will be used (from the length of the dataframe, after missing ones removed)
        self.txt.insert(END, text)
        self.txt.configure(state='disabled')

        df.to_excel(self.file_out) #writes dataframe object to excel output sheet

    def onSips(self):   # on choosing conversion SIPS to CAARMS
        self.caarms_sips = CaarmsSips(file_in = self.file_in) #runs the CaarmsSips.py code, using the input file defined at the start

        df = self.caarms_sips.sips_to_caarms() 
        self.txt.configure(state='normal')
        self.txt.insert(END, "converted: {}\n\n".format(self.file_in))
        self.txt.configure(state='disabled')

        df = self.remove_missing_data(df, 'CAARMS') #run remove missing data function for SIPS

        text = df[CaarmsSips.labels].to_string()
        self.txt.configure(state='normal')
        self.txt.insert(END, "\n\nResult (showing {} patients):\n".format(len(df))) #tells you how many participants will be used (from the length of the dataframe, after missing ones removed)
        self.txt.insert(END, text)
        self.txt.configure(state='disabled')

        df.to_excel(self.file_out)  #writes dataframe object to excel output sheet


    def remove_missing_data(self, df, which): 
        lbl = which + ' Main Diagnosis' #this is the column name where the final (converted = SIPS/CAARMS) diagnosis is found. The goal here is to identify the cases where there was missing data. 

        crit_miss_dd = df[lbl] == 'missing "DD Symptoms"' #if Dangerous/Disorganising symptoms is the output, crit_miss_dd is true. 
        crit_miss_sbe = df[lbl] == 'missing "Symptoms B/E Comorbidities"' #if B/E comborbidities is the output, crit_miss_sbe is true. 
        crit_miss_gaf = df[lbl] == 'missing "GAF drop"' #if GAF drop is the output, crit_miss_gaf is true. 
        missing_dd = df[crit_miss_dd] #index dataframe by variable crit_miss_dd (0/1)
        missing_sbe = df[crit_miss_sbe]
        missing_gaf = df[crit_miss_gaf]
        if len(missing_dd) + len(missing_sbe) + len(missing_gaf) > 0: #if there is any missing data out of the three
            msg = ''
            if len(missing_dd) > 0:
                msg += 'Missing data in the column "DD Symptoms" '\
                       '({} cases).\n'.format(len(missing_dd))  #missing data is due to DD symptoms
            if len(missing_sbe) > 0:
                msg += '\nMissing data in the column "Symptoms Better Explained '\
                       'by Comorbidities" ({} cases).\n'.format(len(missing_sbe))   #missing data is due to comorbidities
            if len(missing_gaf) > 0:
                msg += 'Missing data in the column "GAF drop > 30%" '\
                       '({} cases).\n'.format(len(missing_gaf))     #missing data is due to GAF drop
            msg += '\nPress OK if you want to proceed and exclude the cases,'\
                   ' or CANCEL to enter them and rerun the program (they will '\
                   'be listed in any case).'
            convert_missing = tkinter.messagebox.askokcancel(
                              'WARNING',
                              msg,
                              default=tkinter.messagebox.CANCEL,
                              icon=tkinter.messagebox.WARNING)
            self.txt.configure(state='normal')
            if len(missing_sbe) > 0:
                self.txt.insert(END, 'Patients with missing "Symptoms B/E '
                                     'by Comorbidities" ({}):\n'.format(
                                     len(missing_sbe))) #informs you how many patients are missing due to comorbidities
                text = missing_sbe[CaarmsSips.labels].to_string()
                self.txt.insert(END, text)
                self.txt.insert(END, '\n\n') 
            if len(missing_dd) > 0:
                self.txt.insert(END, 'Patients with missing "DD Symptoms"'
                                     ' ({}):\n'.format(
                                     len(missing_dd))) #informs you how mnay patients are missing due to DD symptoms
                text = missing_dd[CaarmsSips.labels].to_string()
                self.txt.insert(END, text)
                self.txt.insert(END, '\n\n')
            if len(missing_gaf) > 0:
                self.txt.insert(END, 'Patients with missing "GAF drop > 30%"'
                                     ' ({}):\n'.format(
                                     len(missing_gaf))) #informs you how mnay patients are missing due to GAF drop
                text = missing_gaf[CaarmsSips.labels].to_string()
                self.txt.insert(END, text)
            self.txt.configure(state='disabled')

            if (convert_missing == False):
                return

        return df[~crit_miss_dd & ~crit_miss_sbe & ~crit_miss_gaf] #returns the cases where there was NO missing data 

    def onHelp(self):
       self.txt.configure(state='normal')
       self.txt.delete(1.0, END)
       self.txt.insert(END, help)
       self.txt.configure(state='disabled')

    def onCredits(self):
       tkinter.messagebox.showinfo('CREDITS:', credits)

def main(): 
  
    root = Tk()
    ex = Convert(root)
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    root.mainloop()  


if __name__ == '__main__':
    main()

