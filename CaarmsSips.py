

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


import pandas as pd
import numpy as np
import openpyxl

pd.options.mode.chained_assignment = None

class CaarmsSips(object):

    labels = ['ID',
              'Surname Name',
              'CAARMS Main Diagnosis',
              'SIPS Main Diagnosis']

    def __init__(self, file_in = ""):
        self.file_in = file_in

    def gaf_drop(self, x):
        return x*1.058-0.436

    def caarms_to_sips(self):

        xl_file = pd.ExcelFile(self.file_in)
        df = xl_file.parse()
        df_caarms = df

        c2s = {
            'P1' : [0.012, 1.092, 2.212, 3.258, 4.180, 5.019, 5.965],
            'P22': [0.026, 1.059, 2.234, 3.216, 4.105, 5.956, 5.961],
            'P23': [0.041, 0.124, 0.178, 0.112, 0.297, 0.464, 2.692],
            'P3' : [0.012, 0.893, 1.891, 2.953, 3.944, 4.861, 5.876],
            'P4' : [0.067, 0.855, 1.981, 3.032, 4.064, 5.158, 6.090]
        }
        
        for i, row in df_caarms.iterrows():
            p1 = int(row['CAARMS 1.1 Severity'])
            df_caarms.loc[i, 'SIPS P.1'] = c2s['P1'][p1]
            p22 = int(row['CAARMS 1.2 Severity'])
            df_caarms.loc[i, 'SIPS P.2'] = c2s['P22'][p22]
            p23 = int(row['CAARMS 1.2 Severity'])
            df_caarms.loc[i, 'SIPS P.3'] = c2s['P23'][p23]
            p3 = int(row['CAARMS 1.3 Severity'])
            df_caarms.loc[i, 'SIPS P.4'] = c2s['P3'][p3]
            p4 = int(row['CAARMS 1.4 Severity'])
            df_caarms.loc[i, 'SIPS P.5'] = c2s['P4'][p4]

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

        df_caarms['GAF drop'] = df_caarms['SOFAS drop_x'].apply(self.gaf_drop)
            
        # Selection Criteria
        crit_hr_minus = df_caarms['CAARMS Main Diagnosis'] == 'HR -'
        crit_p2 = ((df_caarms['CAARMS 1.1 Severity'] > 2) |
                   (df_caarms['CAARMS 1.2 Severity'] > 2) |
                   (df_caarms['CAARMS 1.3 Severity'] > 2) |
                   (df_caarms['CAARMS 1.4 Severity'] > 2))         
        crit_grd = df_caarms['CAARMS Main Diagnosis'] == 'GRD'
        crit_grd_aps = df_caarms['CAARMS Main Diagnosis'] == 'GRD/APS'
        crit_aps = df_caarms['CAARMS Main Diagnosis'] == 'APS'
        crit_com = df_caarms['Symptoms B/E Comorbidities'] == 'yes'
        crit_no_com = df_caarms['Symptoms B/E Comorbidities'] == 'no'
        crit_com_unknown = pd.isnull(df_caarms['Symptoms B/E Comorbidities'])
        crit_psyc = df_caarms['CAARMS Main Diagnosis'] == 'psychosis'
        crit_psyc_p35 = ((df_caarms['CAARMS 1.3 Severity'] == 5) &
                         (df_caarms['CAARMS 1.3 Frequency'] == 5))
        crit_pysc_to_aps = (crit_psyc_p35 &
                            (df_caarms['CAARMS 1.1 Severity'] < 6) &
                            (df_caarms['CAARMS 1.1 Frequency'] < 6) &
                            (df_caarms['CAARMS 1.2 Severity'] < 6) &
                            (df_caarms['CAARMS 1.2 Frequency'] < 6) &
                            (df_caarms['CAARMS 1.4 Severity'] < 6) &
                            (df_caarms['CAARMS 1.4 Frequency'] < 6))
        crit_dd_symp = df_caarms['DD Symptoms'] == 'yes'
        crit_no_dd_symp = df_caarms['DD Symptoms'] == 'no'
        crit_dd_symp_unknown = pd.isnull(df_caarms['DD Symptoms'])
        crit_onset = df_caarms ['Begun/Worsened within 12 months'] == 'yes'
        crit_no_onset = df_caarms ['Begun/Worsened within 12 months'] == 'no'
        crit_blips = df_caarms['CAARMS Main Diagnosis'] == 'BLIPS'
        crit_grd_blips = df_caarms['CAARMS Main Diagnosis'] == 'GRD/BLIPS'
        crit_GAF = df_caarms['GAF drop'] > 30

        # Convert HR - (P1-P4 < 3) to HR - 
        sips_hr_minus = df_caarms[crit_hr_minus & ~crit_p2]
        sips_hr_minus['SIPS Main Diagnosis'] = 'HR -'
        print(sips_hr_minus[self.labels])

        # Convert HR - (any of P1-P4 > 2 but onset > 12mo) to HR -
        sips_tmp = df_caarms[crit_hr_minus & crit_p2 & crit_no_onset]
        sips_tmp['SIPS Main Diagnosis'] = 'HR -'
        sips_hr_minus = sips_hr_minus.append(sips_tmp)

        # Convert HR - (any of P1-P4 > 2 and onset within 12 mo) to APS 
        sips_aps = df_caarms[crit_hr_minus & crit_p2 & crit_onset]
        sips_aps['SIPS Main Diagnosis'] = 'APS'

        # Convert GRD to HR -
        sips_tmp = df_caarms[crit_grd & ~crit_GAF]
        sips_tmp['SIPS Main Diagnosis'] = 'HR -'
        sips_hr_minus = sips_hr_minus.append(sips_tmp)
        print(sips_hr_minus[self.labels])

        # Convert GRD to GRD
        sips_grd = df_caarms[crit_grd & crit_GAF]
        sips_grd['SIPS Main Diagnosis'] = 'GRD'
        
        # Convert APS or GRD/APS (no comorbidities & onset within 12 months ) to APS
        sips_tmp = df_caarms[(crit_aps | crit_grd_aps) & crit_no_com & crit_onset]
        sips_tmp['SIPS Main Diagnosis'] = 'APS'
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
        sips_tmp['SIPS Main Diagnosis'] = 'missing "Symptoms B/E Comorbidities"'
        sips_grd = sips_grd.append(sips_tmp)
        
        # Convert psychosis (P3 = 5 and P1,P2,P4 < 6) to APS
        all_psyc = df_caarms[crit_psyc]
        sips_tmp = all_psyc[crit_pysc_to_aps]
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
        # Convert BLIPS (with DD Symptoms) to BLIPS
        sips_tmp = df_caarms[(crit_blips | crit_grd_blips) & crit_dd_symp]
        sips_tmp['SIPS Main Diagnosis'] = 'psychosis'
        sips_psyc = sips_psyc.append(sips_tmp)
        
        sips_all = sips_hr_minus.append(sips_grd)
        sips_all = sips_all.append(sips_aps)
        sips_all = sips_all.append(sips_psyc)
        sips_all = sips_all.append(sips_blips)
        sips_all_sorted = sips_all.sort()

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
            'P1' : [0.011, 0.916, 1.816, 2.759, 3.799, 4.976, 6.033],
            'P23': [0.007, 0.919, 1.778, 2.735, 3.806, 4.991, 6.025],
            'P4' : [0.013, 1.112, 2.106, 3.045, 4.059, 5.153, 6.099],
            'P5' : [0.079, 1.126, 2.017, 2.968, 3.936, 4.844, 5.889]
        }

        for i, row in df_sips.iterrows():
            p1 = int(row['SIPS P.1'])
            df_sips.loc[i, 'CAARMS 1.1 Severity'] = s2c['P1'][p1]
            p2 = int(row['SIPS P.2'])
            p3 = int(row['SIPS P.3'])
            df_sips.loc[i, 'CAARMS 1.2 Severity'] = \
                                        s2c['P23'][max(p2, p3)]
            p4 = int(row['SIPS P.4'])
            df_sips.loc[i, 'CAARMS 1.3 Severity'] = s2c['P4'][p4]
            p5 = int(row['SIPS P.5'])
            df_sips.loc[i, 'CAARMS 1.4 Severity'] = s2c['P5'][p5]

        sf2cf = {
            'P1f'  : [0.017, 1.690, 3.321, 5.282],
            'P23f' : [0.062, 1.779, 3.541, 5.478],
            'P4f'  : [0.007, 1.984, 3.347, 4.899],
            'P5f'  : [0.095, 1.743, 3.612, 5.234]
        }

        for i, row in df_sips.iterrows():
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

        df_sips['SOFAS drop'] = df_sips['GAF drop_x'].apply(self.sofas_drop)
        df_sips['SOFAS highest 12 mo'] = df_sips['GAF highest past year_x'].apply(self.sofas_12mo)

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
        crit_SOFAS = df_sips['SOFAS drop'] > 30
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
        

        # Convert HR- to HR-
        caarms_hr_minus = df_sips[crit_hr_minus & crit_no_com & crit_onset]
        caarms_hr_minus['CAARMS Main Diagnosis'] = 'HR -'
        #print caarms_hr_minus[self.labels]

        caarms_tmp = df_sips[crit_hr_minus & crit_com_unknown]
        caarms_tmp['CAARMS Main Diagnosis'] = 'missing "Symptoms B/E Comorbidities"'
        caarms_hr_minus = caarms_hr_minus.append(caarms_tmp)

        # Convert HR- (comorbities or onset > 12mo without functional drop) to HR-
        caarms_tmp = df_sips[crit_hr_minus & (crit_com | crit_no_onset) & ~crit_SOFAS & ~crit_SOFAS_chr]
        caarms_tmp['CAARMS Main Diagnosis'] = 'HR -'
        caarms_hr_minus = caarms_hr_minus.append(caarms_tmp)

        # Convert HR- (comorbities or onset > 12mo with functional drop) to APS
        caarms_aps = df_sips[crit_hr_minus & (crit_com | crit_no_onset) & (crit_SOFAS | crit_SOFAS_chr)]
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
