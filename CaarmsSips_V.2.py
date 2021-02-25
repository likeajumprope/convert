
#!/usr/bin/python
#
# This file is part of Convert
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


import pandas as pd #make sure pandas and numpy are correctly installed using pip3 install pandas/numpy/openpyxl
import numpy as np
import openpyxl

pd.options.mode.chained_assignment = None #ignores warning messages

class CaarmsSips(object): #a class for each participant, with their associated ID, CAARMS and SIPS diagnoses

    labels = ['ID',
              'CAARMS Main Diagnosis',
              'SIPS Main Diagnosis']

    def __init__(self, file_in = ""): #input template is defined here, previously chosen from the menu bar
        self.file_in = file_in

    def gaf_drop(self, x): #function to calculate gaf_drop
        return x*0.793+8.163 

    def caarms_to_sips(self): #defining the necessary dataframe, from the input template

        xl_file = pd.ExcelFile(self.file_in)
        df = xl_file.parse() #parse specified sheet into a data-frame
        df_caarms = df.dropna(subset=['SOFAS year','SOFAS current','CAARMS Main Diagnosis','CAARMS 1.1 Severity','CAARMS 1.2 Severity','CAARMS 1.3 Severity','CAARMS 1.4 Severity']) #clean the dataframe so that it drops any row where there are missing values (NaN) in the essential columns needed for SOFAS drop calculation
        

#carms to sips, severity converters taken from equipercentile linking
        c2s = { 
            'P1' : [0.012, 1.092, 2.212, 3.258, 4.180, 5.019, 5.965],
            'P22': [0.026, 1.059, 2.234, 3.216, 4.105, 5.956, 5.961],
            'P23': [0.041, 0.124, 0.178, 0.112, 0.297, 0.464, 2.692],
            'P3' : [0.012, 0.893, 1.891, 2.953, 3.944, 4.861, 5.876],
            'P4' : [0.067, 0.855, 1.981, 3.032, 4.064, 5.158, 6.090] 
        }
        
        for i, row in df_caarms.iterrows(): #this will iterate through each row in the df
            if df_caarms.loc[i,'CAARMS 1.1 Severity'] == 0: #first fill in all the NaN with zeros 
                df_caarms.loc[i,'CAARMS 1.1 Frequency']=0
            if df_caarms.loc[i,'CAARMS 1.2 Severity'] == 0:
                df_caarms.loc[i,'CAARMS 1.2 Frequency']=0
            if df_caarms.loc[i,'CAARMS 1.3 Severity'] == 0:
                df_caarms.loc[i,'CAARMS 1.3 Frequency']=0
            if df_caarms.loc[i,'CAARMS 1.4 Severity'] == 0:
                df_caarms.loc[i,'CAARMS 1.4 Frequency']=0

            p1 = int(row['CAARMS 1.1 Severity']) #define p1 as the severity value in CAARMS question 1.1.
            df_caarms.loc[i, 'SIPS P.1'] = c2s['P1'][p1] #locate the SIPS P.1 column, row i and define it by multiplying by p1 * P1
            p22 = int(row['CAARMS 1.2 Severity']) #define p22 as the severity value in CAARMS question 1.2.
            df_caarms.loc[i, 'SIPS P.2'] = c2s['P22'][p22]
            p23 = int(row['CAARMS 1.2 Severity']) #define p23 as the severity value in CAARMS question 1.2.
            df_caarms.loc[i, 'SIPS P.3'] = c2s['P23'][p23]
            p3 = int(row['CAARMS 1.3 Severity']) #define p3 as the severity value in CAARMS question 1.3.
            df_caarms.loc[i, 'SIPS P.4'] = c2s['P3'][p3]
            p4 = int(row['CAARMS 1.4 Severity']) #define p4 as the severity value in CAARMS question 1.4.
            df_caarms.loc[i, 'SIPS P.5'] = c2s['P4'][p4]

#carms to sips, frequency converters?
        cf2sf = {
            'P1f'  : [0.019, 0.718, 1.163, 1.781, 2.481, 2.899, 3.289],
            'P22f' : [0.028, 0.602, 1.001, 1.669, 2.406, 2.861, 3.271],
            'P23f' : [0.004, 0.027, 0.071, 0.106, 0.237, 0.469, 2.462],
            'P3f'  : [0.007, 0.625, 1.001, 1.701, 2.537, 3.034, 3.530],
            'P4f'  : [0.080, 0.594, 1.133, 1.666, 2.193, 2.798, 3.472]
        }

        for i, row in df_caarms.iterrows():
            p1f = int (row['CAARMS 1.1 Frequency'])
            df_caarms.loc[i, 'SIPS P.1 frequency'] = cf2sf['P1f'][p1f]
            p22f = int(row['CAARMS 1.2 Frequency'])
            df_caarms.loc[i, 'SIPS P.2 frequency'] = cf2sf['P22f'][p22f]
            p23f = int(row['CAARMS 1.2 Frequency'])
            df_caarms.loc[i, 'SIPS P.3 frequency'] = cf2sf['P23f'][p23f]
            p3f = int(row['CAARMS 1.3 Frequency'])
            df_caarms.loc[i, 'SIPS P.4 frequency'] = cf2sf['P3f'][p3f]
            p4f = int(row['CAARMS 1.4 Frequency'])
            df_caarms.loc[i, 'SIPS P.5 frequency'] = cf2sf['P4f'][p4f]

        ##this section just fills in some variables using raw data from the input data, which are important for selection criteria   

        df_caarms['SOFAS drop_x'] = ((df_caarms['SOFAS year']-df_caarms['SOFAS current']) / df_caarms['SOFAS year'])*100 #calculate SOFAS drop % from the current SOFAS relative to the highest overall lifetime SOFAS score

        for i, row in df_caarms.iterrows():
            if (df_caarms.loc[i,'SOFAS drop_x']>30) | (df_caarms.loc[i,'SOFAS year']<50) :#fill in the SOFAS drop variable, with a response 'yes' if the drop is greater than 30, or if the last 12 months have had a SOFAS score < 50
                df_caarms.loc[i,'SOFAS drop']= 'yes'  
            else:
                df_caarms.loc[i,'SOFAS drop']= 'no'
                
            if (df_caarms.loc[i,'1.1 SIPS b1']=='Yes') | (df_caarms.loc[i,'1.2 SIPS b1']=='Yes') | (df_caarms.loc[i,'1.3 SIPS b1']=='Yes') | (df_caarms.loc[i,'1.4 SIPS b1']=='Yes') :
                df_caarms.loc[i,'Begun/Worsened within 12 months'] = 'yes' #if any of the qualifying symptom domains begun/worsened in previous 12 months, fill in 'yes', otherwise 'no'
            else:
                df_caarms.loc[i,'Begun/Worsened within 12 months'] = 'no'


            if (df_caarms.loc[i,'1.1 SIPS a1']=='Yes') | (df_caarms.loc[i,'1.2 SIPS a1']=='Yes') | (df_caarms.loc[i,'1.3 SIPS a1']=='Yes') | (df_caarms.loc[i,'1.4 SIPS a1']=='Yes') :
                df_caarms.loc[i,'DD Symptoms'] = 'yes' #if any of the qualifying symptoms are seriously disorganising or dangerous, fill in 'yes', otherwise 'no'
            else:
                df_caarms.loc[i,'DD Symptoms'] = 'no'

        df_caarms['GAF drop_x'] = df_caarms['SOFAS drop_x'].apply(self.gaf_drop) #then calculate GAD drop_x from the conversion formula SOFAS->GAF
        
        for i, row in df_caarms.iterrows():
            if df_caarms.loc[i,'GAF drop_x']>30 : 
                df_caarms.loc[i,'GAF drop > 30%'] = 'yes'
            else:
                df_caarms.loc[i,'GAF drop > 30%'] = 'no'


        # Selection Criteria
        crit_hr_minus = df_caarms['CAARMS Main Diagnosis'] == 'HR -' #NOT at high risk
        crit_p2 = ((df_caarms['CAARMS 1.1 Severity'] > 2) | 
                   (df_caarms['CAARMS 1.2 Severity'] > 2) |
                   (df_caarms['CAARMS 1.3 Severity'] > 2) |
                   (df_caarms['CAARMS 1.4 Severity'] > 2))   #crit_p2 =1 if at least one of the symptoms severity > 2.
        crit_grd = df_caarms['CAARMS Main Diagnosis'] == 'GRD' #Genetic Risk and Deterioration (GRD) Syndrome
        crit_grd_aps = df_caarms['CAARMS Main Diagnosis'] == 'GRD/APS' #GRD + APS
        crit_aps = df_caarms['CAARMS Main Diagnosis'] == 'APS' #Attenuated Psychotic Symptoms
        crit_com = df_caarms['Symptoms B/E Comorbidities'] == 'yes' #criteria comorbidity
        crit_no_com = df_caarms['Symptoms B/E Comorbidities'] == 'no' #no comborbidity
        crit_com_unknown = pd.isnull(df_caarms['Symptoms B/E Comorbidities']) #don't have comorbidity data
        crit_psyc = df_caarms['CAARMS Main Diagnosis'] == 'psychosis' 
        crit_psyc_p35 = ((df_caarms['CAARMS 1.3 Severity'] == 5) &
                         (df_caarms['CAARMS 1.3 Frequency'] == 5)) #CAARMS P3 (perceptual abnormlaities) scored as intensity=5 and frequency=5
        crit_psyc_to_aps = (crit_psyc_p35 &
                            (df_caarms['CAARMS 1.1 Severity'] < 6) &
                            (df_caarms['CAARMS 1.1 Frequency'] < 6) &
                            (df_caarms['CAARMS 1.2 Severity'] < 6) &
                            (df_caarms['CAARMS 1.2 Frequency'] < 6) &
                            (df_caarms['CAARMS 1.4 Severity'] < 6) &
                            (df_caarms['CAARMS 1.4 Frequency'] < 6)) #criteria psychoses to APS?
        crit_dd_symp = df_caarms['DD Symptoms'] == 'yes'
        crit_no_dd_symp = df_caarms['DD Symptoms'] == 'no' #what are DD symptoms? 
        crit_dd_symp_unknown = pd.isnull(df_caarms['DD Symptoms'])
        crit_onset = df_caarms ['Begun/Worsened within 12 months'] == 'yes'
        crit_no_onset = df_caarms ['Begun/Worsened within 12 months'] == 'no'
        crit_blips = df_caarms['CAARMS Main Diagnosis'] == 'BLIPS' #Brief Limited Intermittent Psychotic Symptoms 
        crit_grd_blips = df_caarms['CAARMS Main Diagnosis'] == 'GRD/BLIPS'
        crit_GAF = df_caarms['GAF drop_x'] > 30 
        crit_last_month = df_caarms['Symptoms present in previous month'] =='yes'
        crit_no_last_month = df_caarms['Symptoms present in previous month'] =='no'

        # Convert HR - (P1-P4 < 3) to HR - 
        sips_hr_minus = df_caarms[crit_hr_minus & ~crit_p2] #sips hr- defined as criteria for caarms hr - AND score less than 3 in any of the P1-P4 in CAARMS
        sips_hr_minus['SIPS Main Diagnosis'] = 'HR -'
        print(sips_hr_minus[self.labels])

        # Convert HR - (any of P1-P4 > 2 but onset > 12mo) to HR -
        sips_tmp = df_caarms[crit_hr_minus & crit_p2 & crit_no_onset] #sips hr- defined as criteria for caarms hr - AND any P1-p4 >2 AND onset > 12 months ago
        sips_tmp['SIPS Main Diagnosis'] = 'HR -'
        sips_hr_minus = sips_hr_minus.append(sips_tmp)

        # Convert HR - (any of P1-P4 > 2 and onset within 12 mo) to APS 
        sips_aps = df_caarms[crit_hr_minus & crit_p2 & crit_onset] #sips APS defined as criteria for caarms hr - AND any P1-p4 >2 AND onset < 12 months ago
        sips_aps['SIPS Main Diagnosis'] = 'APS'

        # Convert GRD to HR -
        sips_tmp = df_caarms[crit_grd & ~crit_GAF] #sips hr- defined as criteria for caarms GRD AND GAF drop < 30
        sips_tmp['SIPS Main Diagnosis'] = 'HR -'
        sips_hr_minus = sips_hr_minus.append(sips_tmp)
        print(sips_hr_minus[self.labels])

        # Convert GRD to GRD
        sips_grd = df_caarms[crit_grd & crit_GAF] #sips GRD defined as criteria for caarms GRD AND GAF drop > 30
        sips_grd['SIPS Main Diagnosis'] = 'GRD'
        
        # Convert APS or GRD/APS (no comorbidities & onset within 12 months & symptoms present in previous month) to APS
        sips_tmp = df_caarms[(crit_aps | crit_grd_aps) & crit_no_com & crit_onset & crit_last_month]
        sips_tmp['SIPS Main Diagnosis'] = 'APS'
        sips_aps = sips_aps.append(sips_tmp)
        
        # Convert APS or GRD/APS (no comorbidities & onset within 12 months & symptoms not present in previous month) to HR-
        sips_tmp = df_caarms[(crit_aps | crit_grd_aps) & crit_no_com & crit_onset & crit_no_last_month]
        sips_tmp['SIPS Main Diagnosis'] = 'HR -'
        sips_aps = sips_aps.append(sips_tmp)
        

        # Convert APS or GRD/APS (no comorbidities & onset > 12 months ) to HR -
        sips_tmp = df_caarms[(crit_aps | crit_grd_aps) & (crit_com | crit_no_onset)]
        sips_tmp['SIPS Main Diagnosis'] = 'HR -'
        sips_hr_minus = sips_hr_minus.append(sips_tmp)
        
        # Convert APS (with comorbidities) to HR-
        sips_tmp = df_caarms[crit_aps & crit_com]
        sips_tmp['SIPS Main Diagnosis'] = 'HR -'
        sips_hr_minus = sips_hr_minus.append(sips_tmp)
        
        # Convert GRD/APS (with comorbidities) to GRD
        sips_tmp = df_caarms[crit_grd_aps & crit_com]
        sips_tmp['SIPS Main Diagnosis'] = 'GRD'
        sips_grd = sips_grd.append(sips_tmp)

        sips_tmp = df_caarms[(crit_grd_aps | crit_aps) & crit_com_unknown]
        sips_tmp['SIPS Main Diagnosis'] = 'missing "Symptoms B/E Comorbidities"' #cannot perform diagnosis without information on comorbidities
        sips_grd = sips_grd.append(sips_tmp)
        
        # Convert psychosis (P3 = 5 and P1,P2,P4 < 6) to APS
        all_psyc = df_caarms[crit_psyc]
        sips_tmp = all_psyc[crit_psyc_to_aps]
        sips_tmp['SIPS Main Diagnosis'] = 'APS'
        sips_aps = sips_aps.append(sips_tmp)
        
        # Convert psychosis (P3 > 5) to psychosis
        sips_psyc = all_psyc[~all_psyc.isin(sips_tmp)].dropna(how='all')
        sips_psyc['SIPS Main Diagnosis'] = 'psychosis' 
        
        # Convert BLIPS <---- ask info!
        sips_blips = df_caarms[(crit_blips | crit_grd_blips) & crit_dd_symp_unknown]
        sips_blips['SIPS Main Diagnosis'] = 'missing "DD Symptoms"'
        # Convert BLIPS (without DD Symptoms) to BLIPS
        sips_tmp = df_caarms[(crit_blips | crit_grd_blips) & crit_no_dd_symp]
        sips_tmp['SIPS Main Diagnosis'] = 'BLIPS'
        sips_blips = sips_blips.append(sips_tmp)
        # Convert BLIPS (with DD Symptoms) to Psychosis
        sips_tmp = df_caarms[(crit_blips | crit_grd_blips) & crit_dd_symp]
        sips_tmp['SIPS Main Diagnosis'] = 'psychosis'
        sips_psyc = sips_psyc.append(sips_tmp)
        
        sips_all = sips_hr_minus.append(sips_grd)
        sips_all = sips_all.append(sips_aps)
        sips_all = sips_all.append(sips_psyc)
        sips_all = sips_all.append(sips_blips)
        sips_all_sorted = sips_all.sort_index()

        return sips_all_sorted


    def sofas_drop(self, x):
        return x*0.945+0.412 

    def sofas_12mo(self, x):
        return x*0.960+2.436

    def sips_to_caarms(self):
        
        xl_file = pd.ExcelFile(self.file_in)
        df = xl_file.parse()
        df_sips = df
        
        s2c = {
            'P1' : [0.011, 0.916, 1.816, 2.759, 3.799, 4.976, 6.033],  #severity conversion scores
            'P23': [0.007, 0.919, 1.778, 2.735, 3.806, 4.991, 6.025],
            'P4' : [0.013, 1.112, 2.106, 3.045, 4.059, 5.153, 6.099],
            'P5' : [0.079, 1.126, 2.017, 2.968, 3.936, 4.844, 5.889]
        }

        for i, row in df_sips.iterrows():
            p1 = int(row['SIPS P.1']) #define p1 as the severity in the SIPS P.1 cell
            df_sips.loc[i, 'CAARMS 1.1 Severity'] = s2c['P1'][p1] #convert to CAARMS 1.1 severity score by multiplying p1 by converter P1 value
            p2 = int(row['SIPS P.2']) #define p2 as the severity in the SIPS P.2 cell
            p3 = int(row['SIPS P.3']) #define p3 as the severity in the SIPS P.3 cell
            df_sips.loc[i, 'CAARMS 1.2 Severity'] = s2c['P23'][max(p2, p3)] #convert to CAARMS 1.2 severity score by multiplying max of p2/p3 by converter P23 value
            p4 = int(row['SIPS P.4']) #define p4 as the severity in the SIPS P.4 cell
            df_sips.loc[i, 'CAARMS 1.3 Severity'] = s2c['P4'][p4] #convert to CAARMS 1.3 severity score by multiplying p4 by converter P4 value
            p5 = int(row['SIPS P.5']) #define p5 as the severity in the SIPS P.5 cell
            df_sips.loc[i, 'CAARMS 1.4 Severity'] = s2c['P5'][p5] #convert to CAARMS 1.4 severity score by multiplying p4 by converter P5 value

        sf2cf = {
            'P1f'  : [0.017, 1.690, 3.321, 5.282],  #frequency conversion scores
            'P23f' : [0.062, 1.779, 3.541, 5.478],
            'P4f'  : [0.007, 1.984, 3.347, 4.899],
            'P5f'  : [0.095, 1.743, 3.612, 5.234]
        }

        for i, row in df_sips.iterrows(): #iterate across rows, similar procedure, locate the SIMS frequency and multilply by conversion score to obtain CAARMS frequency
            p1f = int(row['SIPS P.1 frequency'])
            df_sips.loc[i, 'CAARMS 1.1 Frequency'] = sf2cf['P1f'][p1f]
            p2f = int(row['SIPS P.2 frequency'])
            p3f = int(row['SIPS P.3 frequency'])
            df_sips.loc[i, 'CAARMS 1.2 Frequency'] = \
                                        sf2cf['P23f'][max(p2f, p3f)]
            p4f = int(row['SIPS P.4 frequency'])
            df_sips.loc[i, 'CAARMS 1.3 Frequency'] = sf2cf['P4f'][p4f]
            p5f = int(row['SIPS P.5 frequency'])
            df_sips.loc[i, 'CAARMS 1.4 Frequency'] = sf2cf['P5f'][p5f]

        df_sips['SOFAS drop_x'] = df_sips['GAF drop_x'].apply(self.sofas_drop)
        # def sofas_drop(self, x):
        #return x*0.945+0.412

        df_sips['SOFAS highest 12 mo'] = df_sips['GAF highest past year_x'].apply(self.sofas_12mo)
        # def sofas_12mo(self, x):
        #return x*0.960+2.436   

        # Selection criteria
        crit_com = df_sips['Symptoms B/E Comorbidities'] == 'yes'
        crit_no_com = df_sips['Symptoms B/E Comorbidities'] == 'no'
        crit_com_unknown = pd.isnull(df_sips['Symptoms B/E Comorbidities'])
        crit_hr_minus = df_sips['SIPS Main Diagnosis'] == 'HR -'
        crit_onset = df_sips ['Begun/Worsened within 12 months'] == 'yes'
        crit_no_onset = df_sips ['Begun/Worsened within 12 months'] == 'no'
        crit_grd = df_sips['SIPS Main Diagnosis'] == 'GRD'
        crit_grd_aps = df_sips['SIPS Main Diagnosis'] == 'GRD/APS'
        crit_aps = df_sips['SIPS Main Diagnosis'] == 'APS'
        crit_SOFAS = df_sips['SOFAS drop_x'] > 30
        crit_SOFAS_chr = df_sips['SOFAS highest 12 mo'] < 50
        crit_psyc_p4 = ((df_sips['SIPS P.4'] == 5) &
                        (df_sips['SIPS P.4 frequency'] == 3))
        crit_psyc = df_sips['SIPS Main Diagnosis'] == 'psychosis'
        crit_dd_symp = df_sips['DD Symptoms'] == 'yes'
        crit_no_dd_symp = df_sips['DD Symptoms'] == 'no'
        crit_dd_symp_unknown = pd.isnull(df_sips['DD Symptoms'])
        crit_more_7days = df_sips['Symptoms present for more than one week'] == 'yes' 
        crit_blips = df_sips['SIPS Main Diagnosis'] == 'BLIPS'
        crit_grd_blips = df_sips['SIPS Main Diagnosis'] == 'GRD/BLIPS'
        crit_last_month = df_sips['Symptoms present in previous month'] =='yes'
        crit_no_last_month = df_sips['Symptoms present in previous month'] =='no'
        

        # Convert HR- to HR-
        caarms_hr_minus = df_sips[crit_hr_minus & crit_no_com & crit_onset & crit_last_month]
        caarms_hr_minus['CAARMS Main Diagnosis'] = 'HR -'
        print(caarms_hr_minus[self.labels])

        caarms_tmp = df_sips[crit_hr_minus & crit_com_unknown]
        caarms_tmp['CAARMS Main Diagnosis'] = 'missing "Symptoms B/E Comorbidities"'
        caarms_hr_minus = caarms_hr_minus.append(caarms_tmp)

        # Convert HR- (comorbities or onset > 12mo or symptoms not present in previous month without functional drop) to HR-
        caarms_tmp = df_sips[crit_hr_minus & (crit_com | crit_no_onset | crit_no_last_month) & ~crit_SOFAS & ~crit_SOFAS_chr]
        caarms_tmp['CAARMS Main Diagnosis'] = 'HR -'
        caarms_hr_minus = caarms_hr_minus.append(caarms_tmp)

        # Convert HR- (comorbities or onset > 12mo or symptoms not present in previous month with functional drop) to APS
        caarms_aps = df_sips[crit_hr_minus & (crit_com | crit_no_onset | crit_no_last_month) & (crit_SOFAS | crit_SOFAS_chr)]
        caarms_aps['CAARMS Main Diagnosis'] = 'APS'
        #print caarms_aps

        # Convert GRD to HR -
        caarms_tmp = df_sips[crit_grd & ~crit_SOFAS & ~crit_SOFAS_chr]
        caarms_tmp['CAARMS Main Diagnosis'] = 'HR -'
        caarms_hr_minus = caarms_hr_minus.append(caarms_tmp)
        
        # Convert GRD to GRD
        caarms_grd = df_sips[crit_grd & (crit_SOFAS | crit_SOFAS_chr)]
        caarms_grd['CAARMS Main Diagnosis'] = 'GRD'

        # Convert APS and GRD/APS to HR-
        caarms_tmp = df_sips[(crit_aps | crit_grd_aps) & ~crit_SOFAS & ~crit_SOFAS_chr]
        caarms_tmp['CAARMS Main Diagnosis'] = 'HR -'
        caarms_hr_minus = caarms_hr_minus.append(caarms_tmp)
        
        # Convert APS and GRD/APS(P.4 < 5) to APS
        caarms_tmp = df_sips[(crit_aps | crit_grd_aps) & (crit_SOFAS | crit_SOFAS_chr) & ~crit_psyc_p4]
        caarms_tmp['CAARMS Main Diagnosis'] = 'APS'
        caarms_aps = caarms_aps.append(caarms_tmp)
        
        # Convert APS (P.4 < 5) to APS <--- missing data
        #caarms_tmp = df_sips[(crit_aps | crit_grd_aps) & crit_GAF_unknown]
        #caarms_tmp ['CAARMS Main Diagnosis'] = 'missing "GAF drop"'
        #caarms_aps = caarms_aps.append(caarms_tmp)
        
        # Convert APS and GRD/APS(P.4 = 5) to psychosis <---- something wrong with the algo!
        caarms_psyc = df_sips[(crit_aps | crit_grd_aps) & (crit_SOFAS | crit_SOFAS_chr) & crit_psyc_p4]
        caarms_psyc['CAARMS Main Diagnosis'] = 'psychosis'
        
        # Convert psychosis <---- ask info!
        caarms_tmp = df_sips[crit_psyc & crit_dd_symp_unknown]
        caarms_tmp['CAARMS Main Diagnosis'] = 'missing "DD Symptoms"'
        caarms_psyc = caarms_psyc.append(caarms_tmp)

        # Convert psychosis (no DD symp) to psychosis
        caarms_tmp = df_sips[crit_psyc & crit_no_dd_symp]
        caarms_tmp['CAARMS Main Diagnosis'] = 'psychosis'
        caarms_psyc = caarms_psyc.append(caarms_tmp)
        # Convert psychosis (DD symp & more than 7 days) to psychosis
        caarms_tmp = df_sips[crit_psyc & crit_dd_symp & crit_more_7days]
        caarms_tmp['CAARMS Main Diagnosis'] = 'psychosis'
        caarms_psyc = caarms_psyc.append(caarms_tmp)
        # Convert psychosis (DD symp & less than 7 days) to BLIPS
        caarms_blips = df_sips[crit_psyc & crit_dd_symp & ~crit_more_7days]
        caarms_blips['CAARMS Main Diagnosis'] = 'BLIPS'
        
        # Convert BLIPS (less than 7 days) to BLIPS
        caarms_tmp = df_sips[(crit_blips | crit_grd_blips)  & ~crit_more_7days]
        caarms_tmp ['CAARMS Main Diagnosis'] = 'BLIPS'
        caarms_blips = caarms_blips.append (caarms_tmp)
        
        # Convert BLIPS or GRD/BLIPS (more than 7 days) to psychosis
        caarms_tmp = df_sips[(crit_blips | crit_grd_blips) & crit_more_7days]
        caarms_tmp['CAARMS Main Diagnosis'] = 'psychosis'
        caarms_psyc = caarms_psyc.append(caarms_tmp)
        
        # Put all together
        caarms_all = caarms_hr_minus.append(caarms_aps)
        caarms_all = caarms_all.append(caarms_grd)
        caarms_all = caarms_all.append(caarms_blips)
        caarms_all = caarms_all.append(caarms_psyc)
        caarms_all_sorted = caarms_all.sort()
        
        return caarms_all_sorted
