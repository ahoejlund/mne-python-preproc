# -*- coding: utf-8 -*-
"""
Adapted on Aug 2015)
(Orig created on Wed Mar 19 09:34:24 2014)

@orig_author: lau
@author: andreas & niels christian
"""

''' ANALYSIS PIPELINE '''
### see also MNE_script.py for related processing steps

## read in functions from 'analysisPipelineFunctions'
import os
import matplotlib
matplotlib.use('TkAgg')
print('TkAgg')
import matplotlib.pyplot as plt
execfile('/projects/MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG/scripts/analysisPipelineFunctions_eog-ecg.py')

import mne


import numpy as np
from subprocess import check_output     # in order to be able to call the bash command 'find' and use the output
from sys import argv



matplotlib.interactive(True)

plt.close('all')

printStatus = 1
ignoreDepWarnings = 0
if ignoreDepWarnings:
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

## which steps to run
## first steps
read = 1 ## can't save filtered files, so don't run this time \
                  ## consuming process every time
Filter = 1
## epochs and sensor space processing
epochIca = 0
evokeds = 0
saveICA = 1
ICAraw = 1


## set path and subs

#print argv
file_name        = argv[1]
#subj='017_KBO'
#cond='08'
#cond            = argv[1]
rawRoot          = argv[2]
resultsRoot      = argv[3]
print file_name
print rawRoot
print resultsRoot

#root = '/projects/MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG/scratch/for_tSSS/'
#resultsRoot = '/projects/MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG/scratch/for_tSSS'#+\
#                'control_move_artRej'

#rawRoot = '/projects/MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG/scratch/CMC/PD/tSSS'
#resultsRoot= '/projects/MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG/scratch/CMC/PD/artRej'

os.chdir(rawRoot) ## set series directory
#fileList = [f for f in os.listdir(rawRoot) if f.endswith('tSSS.fif')]

#file_name = fileList[subj]#subj +'Session' +cond +'_tSSS.fif'

new_name = file_name[0:-4]
 
''' READ AND FILTER'''
if read:
    print('Reading subject: ' +file_name)
    ## read raws
    raw = readRawList(file_name,preload=True)
if Filter:
    ## filter
    l_freq, h_freq = 1, 100.0
    filterRaw(raw,l_freq,h_freq)


''' INDEPENDENT COMPONENT ANALYSIS (EYE BLINKS) '''
if ICAraw:
    saveRoot = (resultsRoot +  '/')
    ICAList,ICAcomps = runICA(raw,saveRoot,new_name)

'''SAVE'T ALL'''
if saveICA:
    if printStatus:
        print('Saving Files for subject: ' +  new_name)
#                os.chdir(root + allSeries[i] + '/mne') ## set saving directory
    saveRoot = (resultsRoot + '/')
    saveRaw(ICAList,ICAcomps,saveRoot,new_name)
#                os.chdir(root + allSeries[i]) ## set back to working directory