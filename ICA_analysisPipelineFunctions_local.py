# -*- coding: utf-8 -*-
"""
Adapted on Aug 2015)
(Orig created on Wed Mar 19 09:34:24 2014)

@orig_author: lau
@author: andreas & niels christian
"""

'''ANALYSIS PIPELINE FUNCTIONS'''
' Many of these are NOT used!!! '

## import libraries
import mne
import csv
#import os
import numpy as np
#import scipy as sci
#==============================================================================
# import sklearn
# import sklearn.svm
# import sklearn.pipeline
# import sklearn.feature_selection
# import sklearn.cross_validation
# import sklearn.preprocessing
# import sklearn.linear_model
#==============================================================================
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mne.io import Raw
from mne.preprocessing import ICA
from mne.preprocessing import create_ecg_epochs, create_eog_epochs
from mne.viz import plot_evoked_topomap
from collections import Counter


''' PREPROCESSING PART '''
          
def readRawList(fileList,preload=False):
    '''Read in fileList, and choose whether to preload. Returns "raw"'''
    raw = Raw(fileList,preload=preload) ## read in files
    return raw
 
def filterRaw(raw,l_freq,h_freq,method,save,ffname):
    '''Filter raw file at the given frequencies and with the given method'''
    raw.filter(l_freq=l_freq,h_freq=h_freq,method=method)
    if save:
        raw.save(ffname)
        #raw.save('filt' + str(l_freq) + '_' + str(h_freq) +\'raw_tsss_at_mc.fif')
                
def get_bad_chans_from_csv(csvfile, block_name):
    #print('Input CSV: {}, bname: {}'.format(csvfile, block_name))
    with open(csvfile) as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            # filter out empty strings
            badchans = filter(len, row[1:])
            if row[0] == block_name:
                print('Block {0}: {1}.'.format(row[0], badchans))  # DEBUG
                # strip white space before/after
                badchans = [c.strip() for c in badchans]
                return(badchans)

    print('WARNING! No bad channels found for block {0}, '
          'returning an empty list (check the CSV?)'.format(block_name))
    return([])

 
''' cf. http://martinos.org/mne/stable/auto_examples/preprocessing/plot_ica_from_raw.html for help on integrating ecg-identification as well '''    
def runICA(raw,saveRoot,name):

    saveRoot = saveRoot    
    icaList = [] 
    ica = []
    n_max_ecg = 3   # max number of ecg components 
#    n_max_eog_1 = 2 # max number of vert eog comps
#    n_max_eog_2 = 2 # max number of horiz eog comps          
    ecg_source_idx, ecg_scores, ecg_exclude = [], [], []
    eog_source_idx, eog_scores, eog_exclude = [], [], []
    #horiz = 1       # will later be modified to horiz = 0 if no horizontal EOG components are identified                   
    ica = ICA(n_components=0.90,n_pca_components=64,max_pca_components=100,noise_cov=None)
    
    fit_picks = mne.pick_types(raw.info, meg=True, eeg=True, eog=False, ecg=False,
                   stim=False, exclude='bads')    
    ica.fit(raw, picks=fit_picks)
    #ica.fit(raw)
    #*************
    eog_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=False, eog=True, ecg=False, emg=False)[0]
    ecg_picks = mne.pick_types(raw.info, meg=False, eeg=False, stim=False, ecg=True, eog=False, emg=False)[0]
    ica_picks = mne.pick_types(raw.info, meg=True, eeg=True, eog=False, ecg=False,
                   stim=False, exclude='bads')
    ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=ica_picks)
    ecg_evoked = ecg_epochs.average()
    eog_evoked = create_eog_epochs(raw, tmin=-.5, tmax=.5, picks=ica_picks).average()

    ecg_source_idx, ecg_scores = ica.find_bads_ecg(ecg_epochs, method='ctps')
    eog_source_idx, eog_scores = ica.find_bads_eog(raw,ch_name=raw.ch_names[eog_picks].encode('ascii', 'ignore'))
    #eog_source_idx_2, eog_scores_2 = ica.find_bads_eog(raw,ch_name='EOG002')
    #if not eog_source_idx_2:
    #    horiz = 0
    
    #show_picks = np.abs(scores).argsort()[::-1][:5]
    #ica.plot_sources(raw, show_picks, exclude=ecg_inds, title=title % 'ecg')
    
        
    # defining a title-frame for later use
    title = 'Sources related to %s artifacts (red)'
  

    # extracting number of ica-components and plotting their topographies
    source_idx = range(0, ica.n_components_)
    #ica_plot = ica.plot_components(source_idx, ch_type="mag")
    ica_plot = ica.plot_components(source_idx)
                                          
    #ica_plot = ica.plot_components(source_idx)

    # select ICA sources and reconstruct MEG signals, compute clean ERFs
    # Add detected artefact sources to exclusion list
    # We now add the eog artefacts to the ica.exclusion list
    if not ecg_source_idx:
        print("No ECG components above threshold were identified for subject " + name +
        " - selecting the component with the highest score under threshold")
        ecg_exclude = [np.absolute(ecg_scores).argmax()]
        ecg_source_idx=[np.absolute(ecg_scores).argmax()]
    elif ecg_source_idx:
        ecg_exclude += ecg_source_idx[:n_max_ecg]
    ica.exclude += ecg_exclude

    if not eog_source_idx:
        if np.absolute(eog_scores).any>0.3:
            eog_exclude=[np.absolute(eog_scores).argmax()]
            eog_source_idx=[np.absolute(eog_scores).argmax()]
            print("No EOG components above threshold were identified " + name +
            " - selecting the component with the highest score under threshold above 0.3")
        elif not np.absolute(eog_scores).any>0.3:
            eog_exclude=[]
            print("No EOG components above threshold were identified" + name)
    elif eog_source_idx:
         eog_exclude += eog_source_idx

    ica.exclude += eog_exclude

    print('########## saving')
    if len(eog_exclude) == 0:
        if len(ecg_exclude) == 0:
            ica_plot.savefig(saveRoot + name + '_comps_eog_none-ecg_none' + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 1:
            ica_plot.savefig(saveRoot + name + '_comps_eog_none-ecg' + map(str, ecg_exclude)[0] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 2:
            ica_plot.savefig(saveRoot + name + '_comps_eog_none-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 3:
            ica_plot.savefig(saveRoot + name + '_comps_eog_none-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '_' + map(str, ecg_exclude)[2] + '.pdf', format = 'pdf')
    elif len(eog_exclude) == 1:
        if len(ecg_exclude) == 0:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] +
            '-ecg_none' + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 1:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] +
            '-ecg' + map(str, ecg_exclude)[0] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 2:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] +
            '-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 3:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] +
            '-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '_' + map(str, ecg_exclude)[2] + '.pdf', format = 'pdf')
    elif len(eog_exclude) == 2:
        if len(ecg_exclude) == 0:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] + '_' + map(str, eog_exclude)[1] +
            '-ecg_none' + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 1:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] + '_' + map(str, eog_exclude)[1] +
            '-ecg' + map(str, ecg_exclude)[0] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 2:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] + '_' + map(str, eog_exclude)[1] +
            '-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '.pdf', format = 'pdf')
        elif len(ecg_exclude) == 3:
            ica_plot.savefig(saveRoot + name + '_comps_eog' + map(str, eog_exclude)[0] + '_' + map(str, eog_exclude)[1] +
            '-ecg' + map(str, ecg_exclude)[0] + '_' + map(str, ecg_exclude)[1] + '_' + map(str, ecg_exclude)[2] + '.pdf', format = 'pdf')
    
    # plot the scores for the different components highlighting in red that/those related to ECG
    #scores_plots=plt.figure()
    #ax = plt.subplot(2,1,1)
    scores_plots_ecg=ica.plot_scores(ecg_scores, exclude=ecg_source_idx, title=title % 'ecg')
    scores_plots_ecg.savefig(saveRoot + name + '_ecg_scores.pdf', format = 'pdf')
    #ax = plt.subplot(2,1,2)
    scores_plots_eog=ica.plot_scores(eog_scores, exclude=eog_source_idx, title=title % 'eog')
    scores_plots_eog.savefig(saveRoot + name + '_eog_scores.pdf', format = 'pdf')
    
    #if len(ecg_exclude) > 0:    
    # estimate average artifact
    #source_clean_ecg=plt.figure()
    #ax = plt.subplot(2,1,1)
    source_source_ecg=ica.plot_sources(ecg_evoked, exclude=ecg_source_idx)
    source_source_ecg.savefig(saveRoot + name + '_ecg_source.pdf', format = 'pdf')
    #ax = plt.subplot(2,1,2)
    source_clean_ecg=ica.plot_overlay(ecg_evoked, exclude=ecg_source_idx)
    source_clean_ecg.savefig(saveRoot + name + '_ecg_clean.pdf', format = 'pdf')
    #clean_plot.savefig(saveRoot + name + '_ecg_clean.pdf', format = 'pdf')
        
    #if len(eog_exclude) > 0:
    source_source_eog=ica.plot_sources(eog_evoked, exclude=eog_source_idx)
    source_source_eog.savefig(saveRoot + name + '_eog_source.pdf', format = 'pdf')
    source_clean_eog=ica.plot_overlay(eog_evoked, exclude=eog_source_idx)
    source_clean_eog.savefig(saveRoot + name + '_eog_clean.pdf', format = 'pdf')
   
    
    overl_plot = ica.plot_overlay(raw)
    overl_plot.savefig(saveRoot + name + '_overl.pdf', format = 'pdf')
                
    plt.close('all')
    ## restore sensor space data
    icaList = ica.apply(raw)
    return(icaList, ica)
    
def saveRaw(raw,ica,saveRoot,name):
    raw.save(saveRoot + name + '_ica-raw.fif', overwrite=False)
    ica.save(saveRoot + name + '-ica.fif')
