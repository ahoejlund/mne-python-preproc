# -*- coding: utf-8 -*-
"""
Adapted on Feb 2017
Edited on Thu Feb 18 11:34:25 2016

@author: kousik
"""

"""
Doc string here.
@author mje
@email: mads [] cnru.dk
"""
import os
import sys
import subprocess
import socket
#import numpy
import numpy as np
#import warnings                           
import re 
from os.path import join, basename
from mne.io import Raw  
import glob

# SETUP PATHS AND PREPARE RAW DATA
hostname = socket.gethostname()

# definning project's folders
proj_name = '/Volumes/iMac_backup/Data/'
scratch_folder = join(proj_name, 'scratch')
scripts_folder = join(proj_name, 'scripts')
mf_folder = join(scratch_folder, 'maxfilter/tsss_st10_corr90')
ica_folder = join(scratch_folder,'ICA_eog_ecg')


if not(os.path.exists(ica_folder)):
    os.mkdir(ica_folder)
    print '*** Directory created' 
 
script_path = join(scripts_folder, 'PyCodes')

# CHANGE DIR TO SAVE FILES THE RIGTH PLACE
os.chdir(script_path)


# querying all subjects in database
##qr = Query(proj_name)
##subs = qr.get_subjects()             

##cb = ClusterBatch(proj_name)

subs = ['0005_FZU', '0006_VAZ', '0008_ATW', '0009_2QT', '0010_VJD', '0011_1I1']
#looping over all subjects' folders
for sub_ind, sub in enumerate(subs):
    rawRoot = join(mf_folder, sub)
    ICA_resultsRoot= join(ica_folder, sub)
    
    if not(os.path.exists(ICA_resultsRoot)):
        os.mkdir(ICA_resultsRoot)
        print '*** Directory created'
            
    os.chdir(rawRoot) ## set series directory
    fif_files = glob.glob(join(rawRoot, '*fif'))
    os.chdir(script_path)
    
    for j in fif_files:
        print j
        cmd = "python ICA_analysisPipeline.py %s %s %s %s" %(cur_sub, j, rawRoot, ICA_resultsRoot)
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
