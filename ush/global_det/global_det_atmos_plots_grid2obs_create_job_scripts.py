'''
Program Name: global_det_atmos_plots_grid2obs_create_job_scripts.py
Contact(s): Mallory Row
Abstract: This creates multiple independent job scripts. These
          jobs contain all the necessary environment variables
          and commands to needed to run the specific
          use case.
'''

import sys
import os
import glob
import datetime
import itertools
import numpy as np
import subprocess
import copy
import global_det_atmos_util as gda_util

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
COMOUT = os.environ['COMOUT']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
VERIF_CASE = os.environ['VERIF_CASE']
STEP = os.environ['STEP']
COMPONENT = os.environ['COMPONENT']
JOB_GROUP = os.environ['JOB_GROUP']
evs_run_mode = os.environ['evs_run_mode']
machine = os.environ['machine']
USE_CFP = os.environ['USE_CFP']
nproc = os.environ['nproc']
start_date = os.environ['start_date']
end_date = os.environ['end_date']
NDAYS = str(os.environ['NDAYS'])
VERIF_CASE_STEP_abbrev = os.environ['VERIF_CASE_STEP_abbrev']
VERIF_CASE_STEP_type_list = (os.environ[VERIF_CASE_STEP_abbrev+'_type_list'] \
                             .split(' '))
PBS_NODEFILE = os.environ['PBS_NODEFILE']
VERIF_CASE_STEP = VERIF_CASE+'_'+STEP

njobs = 0
JOB_GROUP_jobs_dir = os.path.join(DATA, VERIF_CASE_STEP,
                                  'plot_job_scripts', JOB_GROUP)
if not os.path.exists(JOB_GROUP_jobs_dir):
    os.makedirs(JOB_GROUP_jobs_dir)

################################################
#### Base/Common Plotting Information
################################################
base_plot_jobs_info_dict = {
    'pres_levs': {
        'GeoHeight': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                   'CONUS'],
                      'fcst_var_dict': {'name': 'HGT',
                                        'levels': ['P1000', 'P925', 'P850',
                                                   'P700', 'P500', 'P300',
                                                   'P250', 'P200', 'P100',
                                                   'P50', 'P20', 'P10', 'P5']},
                      'obs_var_dict': {'name': 'HGT',
                                       'levels': ['P1000', 'P925', 'P850',
                                                  'P700', 'P500', 'P300',
                                                  'P250', 'P200', 'P100',
                                                  'P50', 'P20', 'P10', 'P5']},
                     'obs_name': 'ADPUPA'},
        'RelHum': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                   'fcst_var_dict': {'name': 'RH',
                                     'levels': ['P1000', 'P925', 'P850',
                                                'P700', 'P500', 'P300', 'P250',
                                                'P200', 'P100', 'P50', 'P20',
                                                'P10', 'P5']},
                   'obs_var_dict': {'name': 'RH',
                                    'levels': ['P1000', 'P925', 'P850',
                                               'P700', 'P500', 'P300', 'P250',
                                               'P200', 'P100', 'P50', 'P20',
                                               'P10', 'P5']},
                   'obs_name': 'ADPUPA'},
        'SpefHum': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                    'fcst_var_dict': {'name': 'SPFH',
                                      'levels': ['P1000', 'P925', 'P850',
                                                 'P700', 'P500', 'P300',
                                                 'P250', 'P200', 'P100',
                                                 'P50', 'P20', 'P10', 'P5']},
                    'obs_var_dict': {'name': 'SPFH',
                                     'levels': ['P1000', 'P925', 'P850',
                                                'P700', 'P500', 'P300',
                                                'P250', 'P200', 'P100',
                                                'P50', 'P20', 'P10', 'P5']},
                    'obs_name': 'ADPUPA'},
        'Temp': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                 'fcst_var_dict': {'name': 'TMP',
                                   'levels': ['P1000', 'P925', 'P850', 'P700',
                                              'P500', 'P300', 'P250', 'P200',
                                              'P100', 'P50', 'P20', 'P10',
                                              'P5']},
                 'obs_var_dict': {'name': 'TMP',
                                  'levels': ['P1000', 'P925', 'P850', 'P700',
                                             'P500', 'P300', 'P250', 'P200',
                                             'P100', 'P50', 'P20', 'P10',
                                             'P5']},
                 'obs_name': 'ADPUPA'},
        'UWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                  'fcst_var_dict': {'name': 'UGRD',
                                    'levels': ['P1000', 'P925', 'P850', 'P700',
                                               'P500', 'P300', 'P250', 'P200',
                                               'P100', 'P50', 'P20', 'P10', 
                                               'P5']},
                  'obs_var_dict': {'name': 'UGRD',
                                   'levels': ['P1000', 'P925', 'P850', 'P700',
                                              'P500', 'P300', 'P250', 'P200',
                                              'P100', 'P50', 'P20', 'P10',
                                              'P5']},
                  'obs_name': 'ADPUPA'},
        'VWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS', 'CONUS'],
                  'fcst_var_dict': {'name': 'VGRD',
                                    'levels': ['P1000', 'P925', 'P850', 'P700',
                                               'P500', 'P300', 'P250', 'P200',
                                               'P100', 'P50', 'P20', 'P10',
                                               'P5']},
                  'obs_var_dict': {'name': 'VGRD',
                                   'levels': ['P1000', 'P925', 'P850', 'P700',
                                              'P500', 'P300', 'P250', 'P200',
                                              'P100', 'P50', 'P20', 'P10',
                                              'P5']},
                  'obs_name': 'ADPUPA'},
        'VectorWind': {'vx_masks': ['GLOBAL', 'NHEM', 'SHEM', 'TROPICS',
                                    'CONUS'],
                       'fcst_var_dict': {'name': 'UGRD_VGRD',
                                         'levels': ['P1000', 'P925', 'P850',
                                                    'P700', 'P500', 'P300',
                                                    'P250', 'P200', 'P100',
                                                    'P50', 'P20', 'P10',
                                                    'P5']},
                       'obs_var_dict': {'name': 'UGRD_VGRD',
                                        'levels': ['P1000', 'P925', 'P850',
                                                   'P700', 'P500', 'P300',
                                                   'P250', 'P200', 'P100',
                                                   'P50', 'P20', 'P10', 'P5']},
                       'obs_name': 'ADPUPA'}
    },
    'ptype': {
        'Rain': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                              'CONUS_South', 'CONUS_West', 'Alaska'],
                 'fcst_var_dict': {'name': 'CRAIN',
                                   'levels': ['L0']},
                 'obs_var_dict': {'name': 'PRWE',
                                  'levels':['Z0']},
                 'obs_name': 'ADPSFC'},
        'Snow': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                              'CONUS_South', 'CONUS_West', 'Alaska'],
                 'fcst_var_dict': {'name': 'CSNOW',
                                   'levels': ['L0']},
                 'obs_var_dict': {'name': 'PRWE',
                                  'levels':['Z0']},
                 'obs_name': 'ADPSFC'},
        'FrzRain': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                 'CONUS_South', 'CONUS_West', 'Alaska'],
                    'fcst_var_dict': {'name': 'CFRZR',
                                      'levels': ['L0']},
                    'obs_var_dict': {'name': 'PRWE',
                                     'levels':['Z0']},
                    'obs_name': 'ADPSFC'},
        'IcePel': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                'CONUS_South', 'CONUS_West', 'Alaska'],
                   'fcst_var_dict': {'name': 'CICEP',
                                     'levels': ['L0']},
                   'obs_var_dict': {'name': 'PRWE',
                                    'levels':['Z0']},
                   'obs_name': 'ADPSFC'},
    },
    'sfc': {
        'CAPEMixedLayer': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                        'CONUS_South', 'CONUS_West',
                                        'Appalachia', 'CPlains', 'DeepSouth',
                                        'GreatBasin', 'GreatLakes',
                                        'Mezqutial', 'MidAtlantic',
                                        'NorthAtlantic', 'NPlains', 'NRockies',
                                        'PacificNW', 'PacificSW', 'Prairie',
                                        'Southeast', 'Southwest', 'SPlains',
                                        'SRockies'],
                           'fcst_var_dict': {'name': 'CAPE',
                                             'levels': ['P90-0']},
                           'obs_var_dict': {'name': 'MLCAPE',
                                            'levels': ['L90000-0']},
                           'obs_name': 'ADPUPA'},
        'CAPESfcBased': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                      'CONUS_South', 'CONUS_West',
                                      'Appalachia', 'CPlains', 'DeepSouth',
                                      'GreatBasin', 'GreatLakes', 'Mezqutial',
                                      'MidAtlantic', 'NorthAtlantic',
                                      'NPlains', 'NRockies', 'PacificNW',
                                      'PacificSW', 'Prairie', 'Southeast',
                                      'Southwest', 'SPlains', 'SRockies'], 
                         'fcst_var_dict': {'name': 'CAPE',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'CAPE',
                                          'levels': ['L100000-0']},
                         'obs_name': 'ADPUPA'},
        'Ceiling': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East'
                                 'CONUS_South', 'CONUS_West', 'Appalachia',
                                 'CPlains', 'DeepSouth', 'GreatBasin',
                                 'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                 'NorthAtlantic', 'NPlains', 'NRockies',
                                 'PacificNW', 'PacificSW', 'Prairie',
                                 'Southeast', 'Southwest', 'SPlains',
                                 'SRockies'],
                    'fcst_var_dict': {'name': 'HGT',
                                      'levels': ['CEILING']},
                    'obs_var_dict': {'name': 'CEILING',
                                     'levels': ['L0']},
                    'obs_name': 'ADPSFC'},
        'DailyAvg_TempAnom2m': {'vx_masks': ['CONUS', 'CONUS_Central',
                                             'CONUS_East', 'CONUS_South',
                                             'CONUS_West', 'Appalachia',
                                             'CPlains', 'DeepSouth',
                                             'GreatBasin', 'GreatLakes',
                                             'Mezqutial', 'MidAtlantic',
                                             'NorthAtlantic', 'NPlains',
                                             'NRockies', 'PacificNW',
                                             'PacificSW', 'Prairie',
                                             'Southeast', 'Southwest',
                                             'SPlains', 'SRockies'],
                                'fcst_var_dict': {'name': 'TMP_ANOM_DAILYAVG',
                                                  'levels': ['Z2']},
                                'obs_var_dict': {'name': 'TMP_ANOM_DAILYAVG',
                                                 'levels': ['Z2']},
                                'obs_name': 'ADPSFC'},
        'Dewpoint2m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                    'CONUS_South', 'CONUS_West', 'Appalachia',
                                    'CPlains', 'DeepSouth', 'GreatBasin',
                                    'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                    'NorthAtlantic', 'NPlains', 'NRockies',
                                    'PacificNW', 'PacificSW', 'Prairie',
                                    'Southeast', 'Southwest', 'SPlains',
                                    'SRockies'],
                       'fcst_var_dict': {'name': 'DPT',
                                         'levels': ['Z2']},
                       'obs_var_dict': {'name': 'DPT',
                                        'levels': ['Z2']},
                       'obs_name': 'ADPSFC'},
        'PBLHeight': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                   'CONUS_South', 'CONUS_West', 'Appalachia',
                                   'CPlains', 'DeepSouth', 'GreatBasin',
                                   'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                   'NorthAtlantic', 'NPlains', 'NRockies',
                                   'PacificNW', 'PacificSW', 'Prairie',
                                   'Southeast', 'Southwest', 'SPlains',
                                   'SRockies'],
                      'fcst_var_dict': {'name': 'HPBL',
                                        'levels': ['L0']},
                      'obs_var_dict': {'name': 'HPBL',
                                       'levels': ['L0']},
                      'obs_name': 'ADPUPA'},
        'RelHum2m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                  'CONUS_South', 'CONUS_West', 'Appalachia',
                                  'CPlains', 'DeepSouth', 'GreatBasin',
                                  'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                  'NorthAtlantic', 'NPlains', 'NRockies',
                                  'PacificNW', 'PacificSW', 'Prairie',
                                  'Southeast', 'Southwest', 'SPlains',
                                  'SRockies'],
                     'fcst_var_dict': {'name': 'RH',
                                       'levels': ['Z2']},
                     'obs_var_dict': {'name': 'RH',
                                      'levels': ['Z2']},
                     'obs_name': 'ADPSFC'},
        'SeaLevelPres': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                      'CONUS_South', 'CONUS_West',
                                      'Appalachia', 'CPlains', 'DeepSouth',
                                      'GreatBasin', 'GreatLakes', 'Mezqutial',
                                      'MidAtlantic', 'NorthAtlantic',
                                      'NPlains', 'NRockies', 'PacificNW',
                                      'PacificSW', 'Prairie', 'Southeast',
                                      'Southwest', 'SPlains', 'SRockies'],
                         'fcst_var_dict': {'name': 'PRMSL',
                                           'levels': ['Z0']},
                         'obs_var_dict': {'name': 'PRMSL',
                                          'levels': ['Z0']},
                         'obs_name': 'ADPSFC'},
        'Temp2m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                'CONUS_South', 'CONUS_West', 'Appalachia',
                                'CPlains', 'DeepSouth', 'GreatBasin',
                                'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                'NorthAtlantic', 'NPlains', 'NRockies',
                                'PacificNW', 'PacificSW', 'Prairie',
                                'Southeast', 'Southwest', 'SPlains',
                                'SRockies'],
                   'fcst_var_dict': {'name': 'TMP',
                                     'levels': ['Z2']},
                   'obs_var_dict': {'name': 'TMP',
                                    'levels': ['Z2']},
                   'obs_name': 'ADPSFC'},
        'TotCloudCover': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                       'CONUS_South', 'CONUS_West',
                                       'Appalachia', 'CPlains', 'DeepSouth',
                                       'GreatBasin', 'GreatLakes', 'Mezqutial',
                                       'MidAtlantic', 'NorthAtlantic',
                                       'NPlains', 'NRockies', 'PacificNW',
                                       'PacificSW', 'Prairie', 'Southeast',
                                       'Southwest', 'SPlains', 'SRockies'],
                          'fcst_var_dict': {'name': 'TCDC',
                                            'levels': ['TOTAL']},
                          'obs_var_dict': {'name': 'TCDC',
                                           'levels': ['L0']},
                          'obs_name': 'ADPSFC'},
        'UWind10m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                  'CONUS_South', 'CONUS_West', 'Appalachia',
                                  'CPlains', 'DeepSouth', 'GreatBasin',
                                  'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                  'NorthAtlantic', 'NPlains', 'NRockies',
                                  'PacificNW', 'PacificSW', 'Prairie',
                                  'Southeast', 'Southwest', 'SPlains',
                                  'SRockies'],
                     'fcst_var_dict': {'name': 'UGRD',
                                       'levels': ['Z10']},
                     'obs_var_dict': {'name': 'UGRD',
                                      'levels': ['Z10']},
                     'obs_name': 'ADPSFC'},
        'Visibility': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                    'CONUS_South', 'CONUS_West', 'Appalachia',
                                    'CPlains', 'DeepSouth', 'GreatBasin',
                                    'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                    'NorthAtlantic', 'NPlains', 'NRockies',
                                    'PacificNW', 'PacificSW', 'Prairie',
                                    'Southeast', 'Southwest', 'SPlains',
                                    'SRockies'],
                       'fcst_var_dict': {'name': 'VIS',
                                         'levels': ['Z0']},
                       'obs_var_dict': {'name': 'VIS',
                                        'levels': ['Z0']},
                       'obs_name': 'ADPSFC'},
        'VWind10m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                  'CONUS_South', 'CONUS_West', 'Appalachia',
                                  'CPlains', 'DeepSouth', 'GreatBasin',
                                  'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                  'NorthAtlantic', 'NPlains', 'NRockies',
                                  'PacificNW', 'PacificSW', 'Prairie',
                                  'Southeast', 'Southwest', 'SPlains',
                                  'SRockies'],
                     'fcst_var_dict': {'name': 'VGRD',
                                       'levels': ['Z10']},
                     'obs_var_dict': {'name': 'VGRD',
                                      'levels': ['Z10']},
                     'obs_name': 'ADPSFC'},
        'WindGust': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                  'CONUS_South', 'CONUS_West', 'Appalachia',
                                  'CPlains', 'DeepSouth', 'GreatBasin',
                                  'GreatLakes', 'Mezqutial', 'MidAtlantic',
                                  'NorthAtlantic', 'NPlains', 'NRockies',
                                  'PacificNW', 'PacificSW', 'Prairie',
                                  'Southeast', 'Southwest', 'SPlains',
                                  'SRockies'],
                     'fcst_var_dict': {'name': 'GUST',
                                       'levels': ['Z0']},
                     'obs_var_dict': {'name': 'GUST',
                                      'levels': ['Z0']},
                     'obs_name': 'ADPSFC'},
        'VectorWind10m': {'vx_masks': ['CONUS', 'CONUS_Central', 'CONUS_East',
                                       'CONUS_South', 'CONUS_West',
                                       'Appalachia', 'CPlains', 'DeepSouth',
                                       'GreatBasin', 'GreatLakes', 'Mezqutial',
                                       'MidAtlantic', 'NorthAtlantic',
                                       'NPlains', 'NRockies', 'PacificNW',
                                       'PacificSW', 'Prairie', 'Southeast',
                                       'Southwest', 'SPlains', 'SRockies'],
                          'fcst_var_dict': {'name': 'UGRD_VGRD',
                                            'levels': ['Z10']},
                          'obs_var_dict': {'name': 'UGRD_VGRD',
                                           'levels': ['Z10']},
                          'obs_name': 'ADPSFC'}
    }
}

################################################
#### condense_stats jobs
################################################
condense_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
#### pres_levs
for pres_levs_job in list(condense_stats_jobs_dict['pres_levs'].keys()):
    if pres_levs_job == 'VectorWind':
        (condense_stats_jobs_dict['pres_levs'][pres_levs_job]\
         ['line_types']) = ['VL1L2']
    else:
        (condense_stats_jobs_dict['pres_levs'][pres_levs_job]\
         ['line_types']) = ['SL1L2']
#### sfc
for sfc_job in list(condense_stats_jobs_dict['sfc'].keys()):
    if sfc_job == 'VectorWind10m':
        condense_stats_jobs_dict['sfc'][sfc_job]['line_types'] = (
            ['VL1L2']
        )
    elif sfc_job in ['Dewpoint2m', 'CAPESfcBased', 'CAPEMixedLayer']:
        condense_stats_jobs_dict['sfc'][sfc_job]['line_types'] = (
            ['SL1L2', 'CTC']
        )
    elif sfc_job in ['Visibility', 'Ceiling']:
        condense_stats_jobs_dict['sfc'][sfc_job]['line_types'] = (
            ['CTC']
        )
    else:
        condense_stats_jobs_dict['sfc'][sfc_job]['line_types'] = (
            ['SL1L2']
        )
#### ptype
for ptype_job in list(condense_stats_jobs_dict['ptype'].keys()):
    condense_stats_jobs_dict['ptype'][ptype_job]['line_types'] = (
        ['CTC']
    )
if JOB_GROUP == 'condense_stats':
    JOB_GROUP_dict = condense_stats_jobs_dict

################################################
#### filter_stats jobs
################################################
filter_stats_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
if JOB_GROUP == 'filter_stats':
    JOB_GROUP_dict = filter_stats_jobs_dict

################################################
#### make_plots jobs
################################################
make_plots_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
if JOB_GROUP == 'make_plots':
    JOB_GROUP_dict = make_plots_jobs_dict

################################################
#### tar_images jobs
################################################
tar_images_jobs_dict = copy.deepcopy(base_plot_jobs_info_dict)
if JOB_GROUP == 'tar_images':
    JOB_GROUP_dict = tar_images_jobs_dict

model_list = os.environ['model_list'].split(' ')
for verif_type in VERIF_CASE_STEP_type_list:
    print("----> Making job scripts for "+VERIF_CASE_STEP+" "
          +verif_type+" for job group "+JOB_GROUP)
    VERIF_CASE_STEP_abbrev_type = (VERIF_CASE_STEP_abbrev+'_'
                                   +verif_type)
    model_plot_name_list = (
        os.environ[VERIF_CASE_STEP_abbrev+'_model_plot_name_list'].split(' ')
    )
    verif_type_plot_jobs_dict = JOB_GROUP_dict[verif_type]
    for verif_type_job in list(verif_type_plot_jobs_dict.keys()):
        obs_list = [
            verif_type_plot_jobs_dict[verif_type_job]['obs_name']
            for m in model_list
        ]
        # Initialize job environment dictionary
        job_env_dict = gda_util.initalize_job_env_dict(
            verif_type, JOB_GROUP,
            VERIF_CASE_STEP_abbrev_type, verif_type_job
        )
        job_env_dict['start_date'] = start_date
        job_env_dict['end_date'] = end_date
        job_env_dict['date_type'] = 'VALID'
        #valid_hr_start = int(job_env_dict['valid_hr_start'])
        #valid_hr_end = int(job_env_dict['valid_hr_end'])
        #valid_hr_inc = int(job_env_dict['valid_hr_inc'])
        #valid_hrs = list(range(valid_hr_start,
        #                       valid_hr_end+valid_hr_inc,
        #                       valid_hr_inc))
        #if 'Daily' in verif_type_job:
        #    if job_env_dict['fhr_inc'] != '24':
        #        job_env_dict['fhr_inc'] = '24'
        #    if int(job_env_dict['fhr_end'])%24 != 0:
        #        job_env_dict['fhr_end'] = str(
        #            int(job_env_dict['fhr_end'])
        #             -(int(job_env_dict['fhr_end'])%24)
        #        )
        #    if int(job_env_dict['fhr_start'])%24 != 0:
        #        job_env_dict['fhr_start'] = str(
        #            int(job_env_dict['fhr_start'])
        #            -(int(job_env_dict['fhr_start'])%24)
        #        )
        #    if int(job_env_dict['fhr_start']) < 24:
        #        job_env_dict['fhr_start'] = '24'
        for data_name in ['fcst', 'obs']:
            job_env_dict[data_name+'_var_name'] =  (
                verif_type_plot_jobs_dict[verif_type_job]\
                [data_name+'_var_dict']['name']
            )
        if JOB_GROUP == 'condense_stats':
            JOB_GROUP_verif_type_job_product_loops = list(itertools.product(
                verif_type_plot_jobs_dict[verif_type_job]['line_types'],
                verif_type_plot_jobs_dict[verif_type_job]['fcst_var_dict']['levels'],
                verif_type_plot_jobs_dict[verif_type_job]['vx_masks'],
                model_list
            ))
        for loop_info in JOB_GROUP_verif_type_job_product_loops:
            if JOB_GROUP == 'condense_stats':
                job_env_dict['fcst_var_level'] = loop_info[1]
                job_env_dict['obs_var_level'] = (
                    verif_type_plot_jobs_dict[verif_type_job]\
                    ['obs_var_dict']['levels'][
                        verif_type_plot_jobs_dict[verif_type_job]\
                        ['fcst_var_dict']['levels'].index(loop_info[1])
                    ]
                )
                job_env_dict['model_list'] = loop_info[3]
                job_env_dict['model_plot_name_list'] = (
                    model_plot_name_list[model_list.index(loop_info[3])]
                )
                job_env_dict['obs_list'] = (
                    obs_list[model_list.index(loop_info[3])]
                )
                job_env_dict['line_type'] = loop_info[0]
                job_env_dict['vx_mask'] = loop_info[2]
                job_env_dict['DATAjob'] = os.path.join(
                    DATA, f"{VERIF_CASE}_{STEP}", 'plot_output',
                    f"{RUN}.{end_date}", f"{VERIF_CASE}_{verif_type}",
                    f"last{NDAYS}days", job_env_dict['line_type'].lower(),
                    f"{job_env_dict['fcst_var_name'].lower()}_"
                    +(job_env_dict['fcst_var_level'].lower()\
                      .replace('.','p').replace('-', '_')),
                    job_env_dict['vx_mask'].lower()
                )
                job_env_dict['COMOUTjob'] = os.path.join(
                    COMOUT, f"{VERIF_CASE}_{verif_type}",
                    f"last{NDAYS}days", job_env_dict['line_type'].lower(),
                    f"{job_env_dict['fcst_var_name'].lower()}_"
                    +(job_env_dict['fcst_var_level'].lower()\
                      .replace('.','p').replace('-', '_')),
                    job_env_dict['vx_mask'].lower()
                )
                for output_dir in [job_env_dict['DATAjob'],
                                   job_env_dict['COMOUTjob']]:
                    if not os.path.exists(output_dir):
                        print(f"Creating output directory: {output_dir}")
                        os.makedirs(output_dir)
                # Create job file
                njobs+=1
                job_file = os.path.join(JOB_GROUP_jobs_dir,
                                        'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                # Write environment variables
                job_env_dict['job_id'] = 'job'+str(njobs)
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                job.write(
                    gda_util.python_command('global_det_atmos_plots.py',[])
                )
                job.close()
            elif JOB_GROUP == 'filter_stats':
                for JOB_GROUP_loop in list(
                    itertools.product(model_list, fcst_var_levels,
                                      fcst_var_threshs, valid_hrs)
                ):
                    job_env_dict['model_list'] = "'"+f"{JOB_GROUP_loop[0]}"+"'"
                    job_env_dict['model_plot_name_list'] = (
                        "'"+f"{model_plot_name_list[model_list.index(JOB_GROUP_loop[0])]}"+"'"
                    )
                    job_env_dict['obs_list'] = (
                        "'"+f"{obs_list[model_list.index(JOB_GROUP_loop[0])]}"+"'"
                    )
                    job_env_dict['fcst_var_level_list'] = (
                        "'"+f"{JOB_GROUP_loop[1]}"+"'"
                    )
                    job_env_dict['fcst_var_thresh_list'] = (
                        "'"+f"{JOB_GROUP_loop[2]}"+"'"
                    )
                    job_env_dict['obs_var_level_list'] = (
                        "'"+f"{obs_var_levels[fcst_var_levels.index(JOB_GROUP_loop[1])]}"+"'"
                    )
                    job_env_dict['obs_var_thresh_list'] = (
                        "'"+f"{obs_var_threshs[fcst_var_threshs.index(JOB_GROUP_loop[2])]}"+"'"
                    )
                    job_env_dict['valid_hr_start'] = (
                        str(JOB_GROUP_loop[3]).zfill(2)
                    )
                    job_env_dict['valid_hr_end'] = (
                        job_env_dict['valid_hr_start']
                    )
                    job_env_dict['valid_hr_inc'] = '24'
                    # Create job file
                    njobs+=1
                    job_file = os.path.join(JOB_GROUP_jobs_dir,
                                            'job'+str(njobs))
                    print("Creating job script: "+job_file)
                    job = open(job_file, 'w')
                    job.write('#!/bin/bash\n')
                    job.write('set -x\n')
                    job.write('\n')
                    # Set any environment variables for special cases
                    # Write environment variables
                    job_env_dict['job_id'] = 'job'+str(njobs)
                    for name, value in job_env_dict.items():
                        job.write('export '+name+'='+value+'\n')
                    job.write('\n')
                    job.write(
                        gda_util.python_command('global_det_atmos_plots.py',[])
                    )
                    job.close()
            elif JOB_GROUP == 'make_plots':
                job_output_images_dir = os.path.join(
                    DATA, VERIF_CASE+'_'+STEP, 'plot_output',
                    RUN+'.'+end_date, verif_type,
                    job_env_dict['job_name'].replace('/','_'), 'images'
                )
                if not os.path.exists(job_output_images_dir):
                    os.makedirs(job_output_images_dir)
                job_env_dict['model_list'] = "'"+f"{', '.join(model_list)}"+"'"
                job_env_dict['model_plot_name_list'] = (
                    "'"+f"{', '.join(model_plot_name_list)}"+"'"
                )
                job_env_dict['obs_list'] = (
                    "'"+f"{', '.join(obs_list)}"+"'"
                )
                for plot in verif_type_plot_jobs_dict\
                        [verif_type_job]['plots_list'].split(', '):
                    job_env_dict['plot'] = plot
                    if plot == 'valid_hour_average':
                        plot_valid_hrs_loop = [valid_hrs]
                    else:
                        plot_valid_hrs_loop = valid_hrs
                    if plot in ['threshold_average', 'performance_diagram']:
                        plot_fcst_threshs_loop = [fcst_var_threshs]
                    else:
                        plot_fcst_threshs_loop = fcst_var_threshs
                    if plot in ['stat_by_level', 'lead_by_level']:
                        plot_fcst_levels_loop = ['all', 'trop', 'strat',
                                                 'ltrop', 'utrop']
                    else:
                        plot_fcst_levels_loop = fcst_var_levels
                    for JOB_GROUP_loop in list(
                        itertools.product(plot_valid_hrs_loop,
                                          plot_fcst_threshs_loop,
                                          plot_fcst_levels_loop)
                    ): 
                        if plot == 'valid_hour_average':
                            job_env_dict['valid_hr_start'] = str(
                                JOB_GROUP_loop[0][0]
                            ).zfill(2)
                            job_env_dict['valid_hr_end'] = str(
                                JOB_GROUP_loop[0][-1]
                            ).zfill(2)
                            job_env_dict['valid_hr_inc'] = str(valid_hr_inc)
                        else:
                            job_env_dict['valid_hr_start'] = str(
                                JOB_GROUP_loop[0]
                            ).zfill(2)
                            job_env_dict['valid_hr_end'] = str(
                                JOB_GROUP_loop[0]
                            ).zfill(2)
                            job_env_dict['valid_hr_inc'] = '24'
                        if plot in ['threshold_average',
                                    'performance_diagram']:
                            job_env_dict['fcst_var_thresh_list'] = (
                                "'"+f"{', '.join(JOB_GROUP_loop[1])}"+"'"
                            )
                            job_env_dict['obs_var_thresh_list'] = (
                                "'"+f"{', '.join(obs_var_threshs)}"+"'"
                            )
                        else:
                            job_env_dict['fcst_var_thresh_list'] = (
                                "'"+f"{JOB_GROUP_loop[1]}"+"'"
                            )
                            job_env_dict['obs_var_thresh_list'] = (
                                "'"+f"{obs_var_threshs[fcst_var_threshs.index(JOB_GROUP_loop[1])]}"+"'"
                            )
                        if plot in ['stat_by_level', 'lead_by_level']:
                            job_env_dict['vert_profile'] = (
                                "'"+f"{JOB_GROUP_loop[2]}"+"'"
                            )
                            job_env_dict['fcst_var_level_list'] = (
                                "'"+f"{', '.join(fcst_var_levels)}"+"'"
                            )
                            job_env_dict['obs_var_level_list'] = (
                                "'"+f"{', '.join(obs_var_levels)}"+"'"
                            )
                        else:
                            job_env_dict['fcst_var_level_list'] = (
                                "'"+f"{JOB_GROUP_loop[2]}"+"'"
                            )
                            job_env_dict['obs_var_level_list'] = (
                                "'"+f"{obs_var_levels[fcst_var_levels.index(JOB_GROUP_loop[2])]}"+"'"
                            )
                        run_global_det_atmos_plots = ['global_det_atmos_plots.py']
                        if evs_run_mode == 'production' and \
                                verif_type in ['pres_levs', 'sfc'] and \
                                plot in ['lead_average', 'lead_by_level',
                                         'lead_by_date']:
                            run_global_det_atmos_plots.append(
                                'global_det_atmos_plots_production_tof240.py'
                            )
                        for run_global_det_atmos_plot in run_global_det_atmos_plots:
                            # Create job file
                            njobs+=1 
                            job_file = os.path.join(JOB_GROUP_jobs_dir,
                                                    'job'+str(njobs))
                            print("Creating job script: "+job_file)
                            job = open(job_file, 'w')
                            job.write('#!/bin/bash\n')
                            job.write('set -x\n')
                            job.write('\n')
                            # Set any environment variables for special cases
                            # Write environment variables
                            job_env_dict['job_id'] = 'job'+str(njobs)
                            for name, value in job_env_dict.items():
                                job.write('export '+name+'='+value+'\n')
                            job.write('\n')
                            job.write(
                                gda_util.python_command(run_global_det_atmos_plot,
                                                        [])
                            )
                        job.close()
            elif JOB_GROUP == 'tar_images':
                job_env_dict['model_list'] = "'"+f"{', '.join(model_list)}"+"'"
                job_env_dict['model_plot_name_list'] = (
                    "'"+f"{', '.join(model_plot_name_list)}"+"'"
                )
                job_env_dict['obs_list'] = (
                    "'"+f"{', '.join(obs_list)}"+"'"
                )
                job_env_dict['fcst_var_level_list'] = (
                    "'"+f"{', '.join(fcst_var_levels)}"+"'"
                )
                job_env_dict['fcst_var_thresh_list'] = (
                    "'"+f"{', '.join(fcst_var_threshs)}"+"'"
                )
                job_env_dict['obs_var_level_list'] = (
                    "'"+f"{', '.join(obs_var_levels)}"+"'"
                )
                job_env_dict['obs_var_thresh_list'] = (
                    "'"+f"{', '.join(obs_var_threshs)}"+"'"
                )
                # Create job file
                njobs+=1
                job_file = os.path.join(JOB_GROUP_jobs_dir,
                                        'job'+str(njobs))
                print("Creating job script: "+job_file)
                job = open(job_file, 'w')
                job.write('#!/bin/bash\n')
                job.write('set -x\n')
                job.write('\n')
                # Set any environment variables for special cases
                # Write environment variables
                job_env_dict['job_id'] = 'job'+str(njobs)
                for name, value in job_env_dict.items():
                    job.write('export '+name+'='+value+'\n')
                job.write('\n')
                job.write(
                    gda_util.python_command('global_det_atmos_plots.py',[])
                )
                job.close()

# If running USE_CFP, create POE scripts
if USE_CFP == 'YES':
    job_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'job*'))
    njob_files = len(job_files)
    if njob_files == 0:
        print("WARNING: No job files created in "+JOB_GROUP_jobs_dir)
    poe_files = glob.glob(os.path.join(JOB_GROUP_jobs_dir, 'poe*'))
    npoe_files = len(poe_files)
    if npoe_files > 0:
        for poe_file in poe_files:
            os.remove(poe_file)
    njob, iproc, node = 1, 0, 1
    while njob <= njob_files:
        job = 'job'+str(njob)
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            if iproc >= int(nproc):
                poe_file.close()
                iproc = 0
                node+=1
        poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                    'poe_jobs'+str(node))
        poe_file = open(poe_filename, 'a')
        iproc+=1
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
                str(iproc-1)+' '
                +os.path.join(JOB_GROUP_jobs_dir,job)+'\n'
            )
        else:
            poe_file.write(
                os.path.join(JOB_GROUP_jobs_dir, job)+'\n'
            )
        poe_file.close()
        njob+=1
    # If at final record and have not reached the
    # final processor then write echo's to
    # poe script for remaining processors
    poe_filename = os.path.join(JOB_GROUP_jobs_dir,
                                'poe_jobs'+str(node))
    poe_file = open(poe_filename, 'a')
    if machine == 'WCOSS2':
        nselect = subprocess.check_output(
            'cat '+PBS_NODEFILE+'| wc -l', shell=True, encoding='UTF-8'
        ).replace('\n', '')
        nnp = int(nselect) * int(nproc)
    else:
        nnp = nproc
    iproc+=1
    while iproc <= int(nnp):
        if machine in ['HERA', 'ORION', 'S4', 'JET']:
            poe_file.write(
                str(iproc-1)+' /bin/echo '+str(iproc)+'\n'
            )
        else:
            poe_file.write(
                '/bin/echo '+str(iproc)+'\n'
            )
        iproc+=1
    poe_file.close()

print("END: "+os.path.basename(__file__))
