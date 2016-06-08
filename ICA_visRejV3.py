# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:15:38 2016

@author: kousik
"""

import os
import mne
import matplotlib.pyplot as plt
import numpy as np
from subprocess import check_output     # in order to be able to call the bash command 'find' and use the output
from mne.preprocessing import create_ecg_epochs, create_eog_epochs

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
rawRoot = '/projects/MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG/scratch/PD_move_tSSS/'
artRej_root = '/projects/MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG/scratch/'+\
                'PD_move_tSSS_artRej'
resultsRoot= '/projects/MINDLAB2011_39-STN-DBS-Effect-Cortex-MEG/scratch/'+\
                'visArtRej'

try:
    os.stat(resultsRoot)
    print '*** Directory already exists'
except:
    os.mkdir(resultsRoot)       
    print '*** Directory created now'                
                

raw_fileList = [f for f in os.listdir(rawRoot) if f.endswith('tSSS.fif')]
raw_fileList.sort()

ica_fileList = [f for f in os.listdir(artRej_root) if f.endswith('-ica.fif')]
ica_fileList.sort()
artRej_fileList=[]

for f in np.arange(0,np.size(ica_fileList)): 
    artRej_fileList.insert(f,ica_fileList[f][:-8]+'_ica-raw.fif')
#artRej_fileList.sort()
    
for j in ica_fileList:
    
    icacomps = mne.preprocessing.read_ica(artRej_root+'/'+ica_fileList[j])
    if icacomps.exclude:
        print('##################')
        print('Pre-selected comps: '+str(icacomps.exclude))
        print('##################')
        icacomps.excludeold=icacomps.exclude
        icacomps.exclude=[]
        print('Old components copied. Exclude field cleared')    
    
    raw = mne.io.Raw(rawRoot+raw_fileList[j], preload=True)

    # ica topos
    source_idx = range(0, icacomps.n_components_)
    ica_plot = icacomps.plot_components(source_idx, ch_type="mag") 
    
    title = 'Sources related to %s artifacts (red)'
    
    prompt = '> '
    print 'What components should be rejected as ECG comps?'
    print 'If more than one, list them each separated by a comma and a space'
    ecg_source_idx = map(int, raw_input(prompt).split(','))    
    
    
    ecg_picks = mne.pick_types(raw.info, meg=False, eeg=False, eog=False, ecg=True,
                   stim=False, exclude='bads')[0]
    eog_picks = mne.pick_types(raw.info, meg=False, eeg=False, ecg=False, eog=True,
                   stim=False, exclude='bads')[1]
    meg_picks = mne.pick_types(raw.info, meg=True, eeg=False, eog=False, ecg=False,
                       stim=False, exclude='bads')               
                   
    ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5,picks=meg_picks),
#                                   ch_name=raw.ch_names[ecg_picks].encode('UTF8'))
    ecg_evoked = ecg_epochs.average()
    
    
    eog_evoked = create_eog_epochs(raw, tmin=-.5, tmax=.5,picks=meg_picks,
                                   ch_name=raw.ch_names[eog_picks].encode('UTF8')).average()
    
    #ecg_source_idx, ecg_scores = icacomps.find_bads_ecg(ecg_epochs, method='ctps')
    
    if not ecg_source_idx:
        ecg_exclude = [np.absolute(ecg_scores).argmax()]
        print(ecg_exclude)
    else:
        ecg_exclude=ecg_source_idx
    print ecg_exclude
    
    eog_source_idx, eog_scores = icacomps.find_bads_eog(raw),
                                    ch_name=raw.ch_names[eog_picks].encode('UTF8'))
                                    
    eog_exclude=eog_source_idx                                
    
    
    source_plot = icacomps.plot_sources(ecg_evoked, exclude=ecg_exclude)
    source_plot = icacomps.plot_sources(eog_evoked, exclude=eog_exclude)
    
    
    
    score_plot = icacomps.plot_scores(ecg_scores, exclude=ecg_source_idx, title='ArtSource ecg')









                
                


                
                
                