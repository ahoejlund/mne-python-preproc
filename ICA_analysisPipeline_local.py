# -*- coding: utf-8 -*-
"""
Adapted on Feb 2017
Adapted on Aug 2015)
(Orig created on Wed Mar 19 09:34:24 2014)

@orig_author: lau
@author: andreas & niels christian
"""

''' ANALYSIS PIPELINE '''
### see also MNE_script.py for related processing steps

## read in functions from 'analysisPipelineFunctions'
import os
from os.path import join, basename
import mne
import csv
import numpy as np
from sys import argv
import matplotlib
matplotlib.use('Agg')
#matplotlib.interactive(False)
import matplotlib.pyplot as plt

#os.environ['MINDLABPROJ']='MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG'
#os.environ['MINDLABPROJ']='MINDLAB2016_MEG-PD-DBS-LangCog'
execfile('/Volumes/iMac_backup/Data/scripts/PyCodes/ICA_analysisPipelineFunctions_local.py')

plt.close('all')

printStatus = 1
ignoreDepWarnings = 0
if ignoreDepWarnings:
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

proj_name = '/Volumes/iMac_backup/Data/'
scratch_folder = join(proj_name, 'scratch')

## which steps to run
## first steps
read = 1 
Filter = 0
get_bads_csv=0
#get_bads_epochs=0
ICAraw = 1
saveICA = 1

#print argv
cur_sub          = argv[1]
file_name        = argv[2]
rawRoot          = argv[3]
ICA_resultsRoot  = argv[4]

print cur_sub
print file_name
print rawRoot
print ICA_resultsRoot

os.chdir(rawRoot) ## set series directory
# definning output filenames:
#new_name  = file_name[0:-4]

''' READ AND FILTER'''
if read:
    print('Reading file: ' +file_name)
    ## read raws
    raw = readRawList(file_name,preload=True)
if Filter:
    ## filter
    l_freq, h_freq = 1, 40.0
    method='iir'
    save=False
    ffname = join(filter_folder,'{0:.0f}-{1:.0f}Hz'.format(l_freq or 'None',h_freq or None), 
                                   cur_sub,basename(file_name)[:-4] + '_filt_raw.fif')
    filterRaw(raw,l_freq,h_freq, method, save, ffname)
    
if get_bads_csv:
    csvfilename= (cur_sub)[:-4] + '.csv'
    csvfile=join(misc_folder, 'bad_chans',  csvfilename)
    
    tmp = basename(file_name).split('_')
    block_name = '_'.join(tmp[:2])
    #bname=basename(file_name)[:-22]
    #bads= get_bad_chans_from_csv(csvfile, bname)
    raw.info['bads'] = get_bad_chans_from_csv(csvfile, block_name)
#
##if get_bads_epochs:
##    epochs_para()
##    picks = mne.pick_types(raw.info,meg=True, 
##                           eeg=True, eog=False, stim=False)
##    bad_chs= get_bad_chs(raw,tmin,tmax,baseline,reject,event_id,picks)
##    raw.info['bads'] = bad_chs
#    
#    
''' INDEPENDENT COMPONENT ANALYSIS (EYE BLINKS) '''
if ICAraw:
    name = join(basename(file_name)[:-22])
    saveRoot = (ICA_resultsRoot +  '/')
    #saveRoot = join(ICA_resultsRoot, name)
    
    ICAList,ICAcomps = runICA(raw,saveRoot,name)

'''SAVE'T ALL'''
if saveICA:
    #if printStatus:
    name = join(basename(file_name)[:-22])
    print('Saving ICA for file: ' +  name)
#                os.chdir(root + allSeries[i] + '/mne') ## set saving directory
    #saveRoot = (resultsRoot + '/')
    saveRoot = (ICA_resultsRoot +  '/')
    #saveRoot = join(ICA_resultsRoot, name)
    #saveRoot = ICA_resultsRoot
    saveRaw(ICAList,ICAcomps,saveRoot,name)
    #saveRaw(ICAList,ICAcomps,saveRoot,new_name)
#                os.chdir(root + allSeries[i]) ## set back to working directory    

             
