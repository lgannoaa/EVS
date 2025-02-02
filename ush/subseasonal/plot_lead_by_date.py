'''
Name: plot_lead_by_date.py
Contact(s): Shannon Shields
Abstract: Reads filtered files from stat_analysis_wrapper run_all_times
          to make lead-date plots
History Log: Third version
Usage: Called by make_plots_wrapper.py
Parameters: None
Input Files: Text files
Output Files: .png images
Condition codes: 0 for success, 1 for failure
'''

import os
import numpy as np
import pandas as pd
import itertools
import warnings
import logging
import datetime
import re
import sys
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.gridspec as gridspec

import plot_util as plot_util

# add metplus directory to path so the wrappers and utilities can be found
sys.path.insert(0, os.path.abspath(os.environ['HOMEMETplus']))
from metplus.util import do_string_sub

#### EMC-evs title creation script
import plot_title as plot_title

#### EMC-evs plot settings
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.titlepad'] = 5
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['xtick.major.pad'] = 5
plt.rcParams['ytick.major.pad'] = 5
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.titleweight'] = 'bold'
plt.rcParams['figure.titlesize'] = 16
nticks = 4
title_loc = 'center'
cmap = plt.cm.BuPu_r
cmap_diff = plt.cm.coolwarm_r
noaa_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHevs'], 'subseasonal', 'noaa.png')
)
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(
    os.path.join(os.environ['USHevs'], 'subseasonal', 'nws.png')
)
nws_logo_alpha = 0.5

# Read environment variables set in make_plots_wrapper.py
verif_case = os.environ['VERIF_CASE']
verif_type = os.environ['VERIF_TYPE']
date_type = os.environ['DATE_TYPE']
valid_beg = os.environ['VALID_BEG']
valid_end = os.environ['VALID_END']
init_beg = os.environ['INIT_BEG']
init_end = os.environ['INIT_END']
fcst_valid_hour = os.environ['FCST_VALID_HOUR']
fcst_init_hour = os.environ['FCST_INIT_HOUR']
obs_valid_hour = os.environ['OBS_VALID_HOUR']
obs_init_hour = os.environ['OBS_INIT_HOUR']
fcst_lead_list = [os.environ['FCST_LEAD'].split(', ')]
fcst_var_name = os.environ['FCST_VAR']
fcst_var_units = os.environ['FCST_UNITS']
fcst_var_level_list = os.environ['FCST_LEVEL'].split(', ')
fcst_var_thresh_list = os.environ['FCST_THRESH'].split(', ')
obs_var_name = os.environ['OBS_VAR']
obs_var_units = os.environ['OBS_UNITS']
obs_var_level_list = os.environ['OBS_LEVEL'].split(', ')
obs_var_thresh_list = os.environ['OBS_THRESH'].split(', ')
interp_pnts = os.environ['INTERP_PNTS']
vx_mask = os.environ['VX_MASK']
alpha = os.environ['ALPHA']
desc = os.environ['DESC']
obs_lead = os.environ['OBS_LEAD']
cov_thresh = os.environ['COV_THRESH']
stats_list = os.environ['STATS'].split(', ')
model_list = os.environ['MODEL'].split(', ')
model_obtype_list = os.environ['MODEL_OBTYPE'].split(', ')
model_reference_name_list = os.environ['MODEL_REFERENCE_NAME'].split(', ')
dump_row_filename_template = os.environ['DUMP_ROW_FILENAME']
average_method = os.environ['AVERAGE_METHOD']
ci_method = os.environ['CI_METHOD']
verif_grid = os.environ['VERIF_GRID']
event_equalization = os.environ['EVENT_EQUALIZATION']
met_version = os.environ['MET_VERSION']
input_base_dir = os.environ['INPUT_BASE_DIR']
output_base_dir = os.environ['OUTPUT_BASE_DIR']
log_metplus = os.environ['LOG_METPLUS']
log_level = os.environ['LOG_LEVEL']
#### EMC-evs environment variables
var_name = os.environ['var_name']
fcst_var_extra = (os.environ['fcst_var_options'].replace(' ', '') \
                  .replace('=','').replace(';','').replace('"','') \
                  .replace("'",'').replace(',','-').replace('_',''))
obs_var_extra = (os.environ['obs_var_options'].replace(' ', '') \
                 .replace('=','').replace(';','').replace('"','') \
                 .replace("'",'').replace(',','-').replace('_',''))
interp_mthd = os.environ['interp']

# General set up and settings
# Logging
logger = logging.getLogger(log_metplus)
logger.setLevel(log_level)
formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d) %(levelname)s: '
    +'%(message)s',
    '%m/%d %H:%M:%S'
    )
file_handler = logging.FileHandler(log_metplus, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
output_data_dir = os.path.join(output_base_dir, 'data')
#### EMC-evs image directory
output_imgs_dir = os.path.join(output_base_dir, 'subseasonal',
                               'subseasonal.{valid?fmt=%Y%m%d%H}')
# Model info
model_info_list = list(
    zip(model_list,
        model_reference_name_list,
        model_obtype_list,
    )
)
nmodels = len(model_info_list)
# Plot info
plot_info_list = list(
    itertools.product(*[fcst_lead_list,
                        fcst_var_level_list,
                        fcst_var_thresh_list])
    )
# Date and time infomation and build title for plot
date_beg = os.environ[date_type+'_BEG']
date_end = os.environ[date_type+'_END']
valid_init_dict = {
    'fcst_valid_hour_beg': fcst_valid_hour.split(', ')[0],
    'fcst_valid_hour_end': fcst_valid_hour.split(', ')[-1],
    'fcst_init_hour_beg': fcst_init_hour.split(', ')[0],
    'fcst_init_hour_end': fcst_init_hour.split(', ')[-1],
    'obs_valid_hour_beg': obs_valid_hour.split(', ')[0],
    'obs_valid_hour_end': obs_valid_hour.split(', ')[-1],
    'obs_init_hour_beg': obs_init_hour.split(', ')[0],
    'obs_init_hour_end': obs_init_hour.split(', ')[-1],
    'valid_hour_beg': '',
    'valid_hour_end': '',
    'init_hour_beg': '',
    'init_hour_end': ''
}
valid_init_type_list = [
    'valid_hour_beg', 'valid_hour_end', 'init_hour_beg', 'init_hour_end'
]
for vitype in valid_init_type_list:
    if (valid_init_dict['fcst_'+vitype] != ''
            and valid_init_dict['obs_'+vitype] == ''):
        valid_init_dict[vitype] = valid_init_dict['fcst_'+vitype]
    elif (valid_init_dict['obs_'+vitype] != ''
            and valid_init_dict['fcst_'+vitype] == ''):
        valid_init_dict[vitype] = valid_init_dict['obs_'+vitype]
    if valid_init_dict['fcst_'+vitype] == '':
        if 'beg' in vitype:
            valid_init_dict['fcst_'+vitype] = '000000'
        elif 'end' in vitype:
            valid_init_dict['fcst_'+vitype] = '235959'
    if valid_init_dict['obs_'+vitype] == '':
        if 'beg' in vitype:
            valid_init_dict['obs_'+vitype] = '000000'
        elif 'end' in vitype:
            valid_init_dict['obs_'+vitype] = '235959'
    if valid_init_dict['fcst_'+vitype] == valid_init_dict['obs_'+vitype]:
        valid_init_dict[vitype] = valid_init_dict['fcst_'+vitype]
# MET .stat file formatting
stat_file_base_columns = plot_util.get_stat_file_base_columns(met_version)
nbase_columns = len(stat_file_base_columns)

# Start looping to make plots
for plot_info in plot_info_list:
    fcst_leads = plot_info[0]
    fcst_lead_timedeltas = np.full_like(fcst_leads, np.nan, dtype=float)
    for fcst_lead in fcst_leads:
        fcst_lead_idx = fcst_leads.index(fcst_lead)
        fcst_lead_timedelta = datetime.timedelta(
            hours=int(fcst_lead[:-4]),
            minutes=int(fcst_lead[-4:-2]),
            seconds=int(fcst_lead[-2:])
        ).total_seconds()
        fcst_lead_timedeltas[fcst_lead_idx] = float(fcst_lead_timedelta)
    fcst_lead_timedeltas_str = []
    for tdelta in fcst_lead_timedeltas:
        h = int(tdelta/3600)
        m = int((tdelta-(h*3600))/60)
        s = int(tdelta-(h*3600)-(m*60))
        if h < 10:
            tdelta_str = f"{h:01d}"
        elif h < 100:
            tdelta_str = f"{h:02d}"
        else:
            tdelta_str = f"{h:03d}"
        if m != 0:
            tdelta_str+=f":{m:02d}"
        if s != 0:
            tdelta_str+=f":{s:02d}"
        fcst_lead_timedeltas_str.append(tdelta_str)
    fcst_var_level = plot_info[1]
    obs_var_level = obs_var_level_list[
        fcst_var_level_list.index(fcst_var_level)
    ]
    fcst_var_thresh = plot_info[2]
    obs_var_thresh = obs_var_thresh_list[
        fcst_var_thresh_list.index(fcst_var_thresh)
    ]
    fcst_var_thresh_symbol, fcst_var_thresh_letter = plot_util.format_thresh(
        fcst_var_thresh
    )
    obs_var_thresh_symbol, obs_var_thresh_letter = plot_util.format_thresh(
        obs_var_thresh
    )
    logger.info("Working on forecast lead averages "
                +"for forecast variable "+fcst_var_name+" "
                +fcst_var_thresh)
    # Set up base name for file naming convention for lead average files,
    # and output data and images
    base_name = date_type.lower()+date_beg+'to'+date_end
    if (valid_init_dict['valid_hour_beg'] != ''
            and valid_init_dict['valid_hour_end'] != ''):
        base_name+=(
            '_valid'+valid_init_dict['valid_hour_beg'][0:4]
            +'to'+valid_init_dict['valid_hour_end'][0:4]+'Z'
        )
    else:
        base_name+=(
            '_fcst_valid'+valid_init_dict['fcst_valid_hour_beg'][0:4]
            +'to'+valid_init_dict['fcst_valid_hour_end'][0:4]+'Z'
            +'_obs_valid'+valid_init_dict['obs_valid_hour_beg'][0:4]
            +'to'+valid_init_dict['obs_valid_hour_end'][0:4]+'Z'
        )
    if (valid_init_dict['init_hour_beg'] != ''
            and valid_init_dict['init_hour_end'] != ''):
        base_name+=(
            '_init'+valid_init_dict['init_hour_beg'][0:4]
            +'to'+valid_init_dict['init_hour_end'][0:4]+'Z'
        )
    else:
        base_name+=(
            '_fcst_init'+valid_init_dict['fcst_init_hour_beg'][0:4]
            +'to'+valid_init_dict['fcst_init_hour_end'][0:4]+'Z'
            +'_obs_init'+valid_init_dict['obs_init_hour_beg'][0:4]
            +'to'+valid_init_dict['obs_init_hour_end']+'Z'
        )
    base_name+=(
        '_fcst_leadFCSTLEADHOLDER'
        +'_fcst'+fcst_var_name+fcst_var_level
        +fcst_var_thresh_letter.replace(',', '_')+interp_mthd
        +'_obs'+obs_var_name+obs_var_level
        +obs_var_thresh_letter.replace(',', '_')+interp_mthd
        +'_vxmask'+vx_mask
    )
    if desc != '':
        base_name+='_desc'+desc
    if obs_lead != '':
        base_name+='_obs_lead'+obs_lead
    if interp_pnts != '':
        base_name+='_interp_pnts'+interp_pnts
    if cov_thresh != '':
        cov_thresh_symbol, cov_thresh_letter = plot_util.format_thresh(
            cov_thresh
        )
        base_name+='_cov_thresh'+cov_thresh_letter.replace(',', '_')
    if alpha != '':
        base_name+='_alpha'+alpha
    # Reading in model .stat files from stat_analysis
    logger.info("Reading in model data")
    for model_info in model_info_list:
        model_num = model_info_list.index(model_info) + 1
        model_name = model_info[0]
        model_plot_name = model_info[1]
        model_obtype = model_info[2]
        for fl in range(len(fcst_leads)):
            fcst_lead = fcst_leads[fl]
            # Set up expected date in MET .stat file
            # and date plot information
            plot_time_dates, expected_stat_file_dates = (
                plot_util.get_date_arrays(date_type, date_beg, date_end,
                                          fcst_valid_hour, fcst_init_hour,
                                          obs_valid_hour, obs_init_hour,
                                          fcst_lead)
            )
            total_dates = len(plot_time_dates)
            if len(plot_time_dates) == 0:
                logger.error("Date array constructed information from "
                             +"METplus conf file has length of 0. Not enough "
                             +"information was provided to build date "
                             +"information. Please check provided "
                             +"VALID/INIT_BEG/END and "
                             +"OBS/FCST_INIT/VALID_HOUR_LIST")
                exit(1)
            #### EMC-evs date tick interval
            if len(plot_time_dates) < nticks:
                date_tick_intvl = 1
            else:
                date_tick_intvl = int(len(plot_time_dates)/nticks)
            model_lead_now_data_index = pd.MultiIndex.from_product(
                [[model_plot_name], [fcst_lead], expected_stat_file_dates],
                names=['model_plot_name', 'leads', 'dates']
            )
            model_stat_template = dump_row_filename_template
            string_sub_dict = {
                'model': model_name,
                'model_reference': model_plot_name,
                'obtype': model_obtype,
                'fcst_lead': fcst_lead,
                'obs_lead': obs_lead,
                'fcst_level': fcst_var_level,
                'obs_level': obs_var_level,
                'fcst_thresh': fcst_var_thresh,
                'obs_thresh': obs_var_thresh,
            }
            model_stat_file = do_string_sub(model_stat_template,
                                            **string_sub_dict)
            if os.path.exists(model_stat_file):
                nrow = sum(1 for line in open(model_stat_file))
                if nrow == 0:
                    logger.warning("Model "+str(model_num)+" "+model_name+" "
                                   +"with plot name "+model_plot_name+" "
                                   +"file: "+model_stat_file+" empty")
                    model_lead_now_data = pd.DataFrame(
                        np.nan, index=model_lead_now_data_index,
                        columns=[ 'TOTAL' ]
                    )
                else:
                    logger.debug("Model "+str(model_num)+" "+model_name+" "
                                 +"with plot name "+model_plot_name+" "
                                 +"file: "+model_stat_file+" exists")
                    model_lead_now_stat_file_data = pd.read_csv(
                        model_stat_file, sep=" ", skiprows=1,
                        skipinitialspace=True, header=None
                    )
                    model_lead_now_stat_file_data.rename(
                        columns=dict(zip(
                            model_lead_now_stat_file_data.columns \
                            [:len(stat_file_base_columns)],
                            stat_file_base_columns
                        )), inplace=True
                    )
                    line_type = model_lead_now_stat_file_data['LINE_TYPE'][0]
                    stat_file_line_type_columns = (
                        plot_util.get_stat_file_line_type_columns(logger,
                                                                  met_version,
                                                                  line_type)
                    )
                    model_lead_now_stat_file_data.rename(
                        columns=dict(zip(
                            model_lead_now_stat_file_data.columns \
                            [len(stat_file_base_columns):],
                            stat_file_line_type_columns
                        )), inplace=True
                    )
                    model_lead_now_stat_file_data_fcstvaliddates = (
                        model_lead_now_stat_file_data.loc[:] \
                        ['FCST_VALID_BEG'].values
                    )
                    model_lead_now_data = (
                        pd.DataFrame(np.nan, index=model_lead_now_data_index,
                                     columns=stat_file_line_type_columns)
                        )
                    #model_lead_now_stat_file_data.fillna(
                    #    {'FCST_UNITS':'NA', 'OBS_UNITS':'NA', 'VX_MASK':'NA'},
                    #    inplace=True
                    #)
                    for expected_date in expected_stat_file_dates:
                        if expected_date in \
                                model_lead_now_stat_file_data_fcstvaliddates:
                            matching_date_idx = (
                                model_lead_now_stat_file_data_fcstvaliddates \
                                .tolist().index(expected_date)
                            )
                            model_lead_now_stat_file_data_idx = (
                                model_lead_now_stat_file_data \
                                .loc[matching_date_idx][:]
                            )
                            for col in stat_file_line_type_columns:
                                #### EMC-evs changes for PRMSL,PRES/Z0
                                #### O3MR
                                if fcst_var_name == 'PRMSL' \
                                        or \
                                        (fcst_var_name == 'PRES' \
                                         and fcst_var_level == 'Z0'):
                                    if col in ['FBAR', 'OBAR']:
                                        scale = 1/100.
                                    elif col in ['FFBAR', 'FOBAR', 'OOBAR']:
                                        scale = 1/(100.*100.)
                                    else:
                                        scale = 1
                                elif fcst_var_name == 'O3MR':
                                    if col in ['FBAR', 'OBAR']:
                                        scale = 1e6
                                    elif col in ['FFBAR', 'FOBAR', 'OOBAR']:
                                        scale = 1e6*1e6
                                    else:
                                        scale = 1
                                else:
                                    scale = 1
                                model_lead_now_data.loc[
                                    (model_plot_name,
                                     fcst_lead,
                                     expected_date)
                                ][col] = (
                                    model_lead_now_stat_file_data_idx \
                                    .loc[:][col]
                                ) * scale
            else:
                logger.warning("Model "+str(model_num)+" "+model_name+" "
                               +"with plot name "+model_plot_name+" "
                               +"file: "+model_stat_file+" does not exist")
                model_lead_now_data = pd.DataFrame(
                        np.nan, index=model_lead_now_data_index,
                        columns=[ 'TOTAL' ]
                )
            if fl > 0:
                model_now_data = pd.concat(
                    [model_now_data, model_lead_now_data], sort=True
                )
            else:
                model_now_data = model_lead_now_data
        if model_num > 1:
            model_data = pd.concat([model_data, model_now_data], sort=True)
        else:
            model_data = model_now_data
    # Build lead by date grid for plotting
    ymesh, xmesh = np.meshgrid(plot_time_dates, fcst_lead_timedeltas)
    # Calculate statistics and plots
    logger.info("Calculating and plotting statistics")
    for stat in stats_list:
        logger.debug("Working on "+stat)
        stat_values, stat_values_array, stat_plot_name = (
            plot_util.calculate_stat(logger, model_data, stat)
        )
        if event_equalization == 'True':
            logger.debug("Doing event equalization")
            for l in range(len(stat_values_array[:,0,0,0])):
                for fl in range(len(fcst_leads)):
                    stat_values_array[l,:,fl,:] = (
                        np.ma.mask_cols(stat_values_array[l,:,fl,:])
                    )
        if (stat == 'fbar_obar' or stat == 'orate_frate'
                or stat == 'baser_frate'):
            nsubplots = nmodels + 1
        else:
            nsubplots = nmodels
        if nsubplots == 1:
            x_figsize, y_figsize = 14, 7
            row, col = 1, 1
            hspace, wspace = 0, 0
            bottom, top = 0.175, 0.825
            suptitle_y_loc = 0.92125
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
            cbar_bottom = 0.06
            cbar_height = 0.02
        elif nsubplots == 2:
            x_figsize, y_figsize = 14, 7
            row, col = 1, 2
            hspace, wspace = 0, 0.1
            bottom, top = 0.175, 0.825
            suptitle_y_loc = 0.92125
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
            cbar_bottom = 0.06
            cbar_height = 0.02
        elif nsubplots > 2 and nsubplots <= 4:
            x_figsize, y_figsize = 14, 14
            row, col = 2, 2
            hspace, wspace = 0.15, 0.1
            bottom, top = 0.125, 0.9
            suptitle_y_loc = 0.9605
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
            cbar_bottom = 0.03
            cbar_height = 0.02
        elif nsubplots > 4 and nsubplots <= 6:
            x_figsize, y_figsize = 14, 14
            row, col = 3, 2
            hspace, wspace = 0.15, 0.1
            bottom, top = 0.125, 0.9
            suptitle_y_loc = 0.9605
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
            cbar_bottom = 0.03
            cbar_height = 0.02
        elif nsubplots > 6 and nsubplots <= 8:
            x_figsize, y_figsize = 14, 14
            row, col = 4, 2
            hspace, wspace = 0.175, 0.1
            bottom, top = 0.125, 0.9
            suptitle_y_loc = 0.9605
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
            cbar_bottom = 0.03
            cbar_height = 0.02
        elif nsubplots > 8 and nsubplots <= 10:
            x_figsize, y_figsize = 14, 14
            row, col = 5, 2
            hspace, wspace = 0.225, 0.1
            bottom, top = 0.125, 0.9
            suptitle_y_loc = 0.9605
            noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
            nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
            cbar_bottom = 0.03
            cbar_height = 0.02
        else:
            logger.error("Too many subplots selected, max. is 10")
            exit(1)
        suptitle_x_loc = (plt.rcParams['figure.subplot.left']
                          +plt.rcParams['figure.subplot.right'])/2.
        fig = plt.figure(figsize=(x_figsize, y_figsize))
        gs = gridspec.GridSpec(
            row, col,
            bottom = bottom, top = top,
            hspace = hspace, wspace = wspace,
        )
        noaa_logo_xpixel_loc = (
            x_figsize * plt.rcParams['figure.dpi'] * noaa_logo_x_scale
        )
        noaa_logo_ypixel_loc = (
            y_figsize * plt.rcParams['figure.dpi'] * noaa_logo_y_scale
        )
        nws_logo_xpixel_loc = (
            x_figsize * plt.rcParams['figure.dpi'] * nws_logo_x_scale
        )
        nws_logo_ypixel_loc = (
            y_figsize * plt.rcParams['figure.dpi'] * nws_logo_y_scale
        )
        #### EMC_evs set up subplots
        subplot_num = 0
        while subplot_num < nsubplots:
            ax = plt.subplot(gs[subplot_num])
            ax.grid(True)
            if len(fcst_lead_timedeltas) >= 15:
                ax.set_xticks(fcst_lead_timedeltas[::2])
                ax.set_xticklabels(fcst_lead_timedeltas_str[::2])
            elif len(fcst_lead_timedeltas) >= 25:
                ax.set_xticks(fcst_lead_timedeltas[::4])
                ax.set_xticklabels(fcst_lead_timedeltas_str[::4])
            else:
                ax.set_xticks(fcst_lead_timedeltas)
                ax.set_xticklabels(fcst_lead_timedeltas_str)
            ax.set_xlim([fcst_lead_timedeltas[0],
                         fcst_lead_timedeltas[-1]])
            if ax.is_last_row() \
                    or (nsubplots % 2 != 0 and subplot_num == nsubplots -1):
                ax.set_xlabel('Forecast Hour')
            else:
                plt.setp(ax.get_xticklabels(), visible=False)
            ax.set_ylim([plot_time_dates[0],plot_time_dates[-1]])
            ax.set_yticks(plot_time_dates[::date_tick_intvl])
            ax.yaxis.set_major_formatter(md.DateFormatter('%d%b%Y'))
            if len(plot_time_dates) > 60:
                ax.yaxis.set_minor_locator(md.MonthLocator())
            else:
                ax.yaxis.set_minor_locator(md.DayLocator())
            if ax.is_first_col():
                ax.set_ylabel(date_type.title()+" Date")
            else:
                plt.setp(ax.get_yticklabels(), visible=False)
            subplot_num+=1
        obs_plotted = False
        get_clevels = True
        make_colorbar = False
        for model_info in model_info_list:
            model_num = model_info_list.index(model_info) + 1
            model_idx = model_info_list.index(model_info)
            model_name = model_info[0]
            model_plot_name = model_info[1]
            model_obtype = model_info[2]
            model_stat_values_array = stat_values_array[0,model_idx,:,:]
            if (stat == 'fbar_obar' or stat == 'orate_frate'
                    or stat == 'baser_frate'):
                if not obs_plotted:
                    ax = plt.subplot(gs[0])
                    ax.set_title('obs', loc='left')
                    if not stat_values_array[1,model_idx,:,:].mask.all():
                        logger.debug("Plotting observations from "+model_name)
                        obs_stat_values_array = (
                            stat_values_array[1,model_idx,:,:]
                        )
                        CF1 = ax.contourf(xmesh, ymesh, obs_stat_values_array,
                                          cmap=cmap,
                                          locator=matplotlib \
                                              .ticker.MaxNLocator(
                                          symmetric=True
                                          ), extend='both')
                        C1 = ax.contour(xmesh, ymesh, obs_stat_values_array,
                                        levels=CF1.levels,
                                        colors='k',
                                        linewidths=1.0)
                        ax.clabel(C1, C1.levels,
                                  fmt='%1.2f',
                                  inline=True,
                                  fontsize=12.5)
                        obs_plotted = True
                ax = plt.subplot(gs[model_num])
                ax.set_title(model_plot_name+'-obs', loc='left')
                model_obs_diff = (model_stat_values_array
                                  -stat_values_array[1,model_idx,:,:])
                if not model_obs_diff.mask.all():
                    logger.debug("Plotting model "+str(model_num)+" "
                                 +model_name+" - obs "
                                 +"with name on plot "+model_plot_name
                                 +" - obs")
                    if get_clevels:
                        clevels_diff = plot_util.get_clevels(model_obs_diff)
                        CF2 = ax.contourf(xmesh, ymesh, model_obs_diff,
                                          levels=clevels_diff,
                                          cmap=cmap_diff,
                                          locator=matplotlib \
                                              .ticker.MaxNLocator(
                                              symmetric=True
                                          ),
                                          extend='both')
                        get_clevels = False
                        make_colorbar = True
                        colorbar_CF = CF2
                        colorbar_CF_ticks = CF2.levels
                        colorbar_label = 'Difference'
                    else:
                        CF = ax.contourf(xmesh, ymesh, model_obs_diff,
                                         levels=CF2.levels,
                                         cmap=cmap_diff,
                                         locator=matplotlib.ticker.MaxNLocator(
                                             symmetric=True
                                         ),
                                         extend='both')
            elif stat == 'bias' or stat == 'fbias':
                ax = plt.subplot(gs[model_idx])
                ax.set_title(model_plot_name, loc='left')
                if not model_stat_values_array.mask.all():
                    logger.debug("Plotting model "+str(model_num)+" "
                                 +model_name+" with name on plot "
                                 +model_plot_name)
                    if get_clevels:
                        clevels_bias = plot_util.get_clevels(
                            model_stat_values_array
                         )
                        CF1 = ax.contourf(xmesh, ymesh,
                                          model_stat_values_array,
                                          levels=clevels_bias,
                                          cmap=cmap_bias,
                                          locator=\
                                          matplotlib.ticker.MaxNLocator(
                                              symmetric=True
                                          ), extend='both')
                        C1 = ax.contour(xmesh, ymesh, model_stat_values_array,
                                        levels=CF1.levels,
                                        colors='k',
                                        linewidths=1.0)
                        ax.clabel(C1, C1.levels,
                                  fmt='%1.2f',
                                  inline=True,
                                  fontsize=12.5)
                        get_clevels = False
                        make_colorbar = True
                        colorbar_CF = CF1
                        colorbar_CF_ticks = CF1.levels
                        colorbar_label = 'Bias'
                    else:
                        CF = ax.contourf(xmesh, ymesh,
                                         model_stat_values_array,
                                         levels=CF1.levels,
                                         locator=\
                                         matplotlib.ticker.MaxNLocator(
                                              symmetric=True
                                         ),
                                         cmap=cmap_bias,
                                         extend='both')
                        C = ax.contour(xmesh, ymesh,
                                       model_stat_values_array,
                                       levels=CF1.levels,
                                       colors='k',
                                       linewidths=1.0)
                        ax.clabel(C, C.levels,
                                  fmt='%1.2f',
                                  inline=True,
                                  fontsize=12.5)
            else:
                ax = plt.subplot(gs[model_idx])
                if model_num == 1:
                    ax.set_title(model_plot_name, loc='left')
                    model1_name = model_name
                    model1_plot_name = model_plot_name
                    model1_stat_values_array = model_stat_values_array
                    if not model_stat_values_array.mask.all():
                        logger.debug("Plotting model "+str(model_num)+" "
                                     +model_name+" with name on plot "
                                     +model_plot_name)
                        if stat in ['acc']:
                            levels = np.array(
                                [0.0, 0.1, 0.2, 0.3, 0.4, 0.5,
                                 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1]
                            )
                            CF1 = ax.contourf(xmesh, ymesh,
                                              model_stat_values_array,
                                              levels=levels, cmap=cmap,
                                              extend='both')
                        else:
                            CF1 = ax.contourf(xmesh, ymesh,
                                              model_stat_values_array,
                                              cmap=cmap,
                                              extend='both')
                        C1 = ax.contour(xmesh, ymesh,
                                        model_stat_values_array,
                                        levels=CF1.levels,
                                        colors='k',
                                        linewidths=1.0)
                        ax.clabel(C1, C1.levels,
                                  fmt='%1.2f',
                                  inline=True,
                                  fontsize=12.5)
                else:
                    ax.set_title(model_plot_name+'-'+model1_plot_name,
                                 loc='left')
                    model_model1_diff = (
                        model_stat_values_array - model1_stat_values_array
                    )
                    if not model_model1_diff.mask.all():
                        logger.debug("Plotting model "+str(model_num)+" "
                                     +model_name+" - model 1 "+model1_name+" "
                                     +"with name on plot "+model_plot_name+" "
                                     +"- "+model1_plot_name)
                        if get_clevels:
                            clevels_diff = plot_util.get_clevels(
                                model_model1_diff
                            )
                            CF2 = ax.contourf(xmesh, ymesh, model_model1_diff,
                                              levels=clevels_diff,
                                              cmap=cmap_diff,
                                              locator=\
                                              matplotlib.ticker.MaxNLocator(
                                                  symmetric=True
                                              ),
                                              extend='both')
                            get_clevels = False
                            make_colorbar = True
                            colorbar_CF = CF2
                            colorbar_CF_ticks = CF2.levels
                            colorbar_label = 'Difference'
                        else:
                            CF = ax.contourf(xmesh, ymesh, model_model1_diff,
                                             levels=CF2.levels,
                                             cmap=cmap_diff,
                                             locator=\
                                             matplotlib.ticker.MaxNLocator(
                                                 symmetric=True
                                             ),
                                             extend='both')
        #### EMC-evs build formal plot title
        if verif_grid == vx_mask:
            grid_vx_mask = verif_grid
        else:
            grid_vx_mask = verif_grid+vx_mask
        var_info_title = plot_title.get_var_info_title(
            fcst_var_name, fcst_var_level, fcst_var_extra, fcst_var_thresh
        )
        vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
        date_info_title = plot_title.get_date_info_title(
            date_type, fcst_valid_hour.split(', '),
            fcst_init_hour.split(', '),
            str(datetime.date.fromordinal(int(
                plot_time_dates[0])
            ).strftime('%d%b%Y')),
            str(datetime.date.fromordinal(int(
                plot_time_dates[-1])
            ).strftime('%d%b%Y')),
            verif_case
        )
        full_title = (
            stat_plot_name+'\n'
            +var_info_title+', '+vx_mask_title+'\n'
            +date_info_title
        )
        fig.suptitle(full_title,
                     x = suptitle_x_loc, y = suptitle_y_loc,
                     horizontalalignment = title_loc,
                     verticalalignment = title_loc)
        noaa_img = fig.figimage(noaa_logo_img_array,
                                noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                                zorder=1, alpha=noaa_logo_alpha)
        nws_img = fig.figimage(nws_logo_img_array,
                               nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                               zorder=1, alpha=nws_logo_alpha)
        plt.subplots_adjust(
            left = noaa_img.get_extent()[1] \
                   /(plt.rcParams['figure.dpi']*x_figsize),
            right = nws_img.get_extent()[0] \
                    /(plt.rcParams['figure.dpi']*x_figsize)
        )
        #### EMC-evs add colorbar
        cbar_left =(
            noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize)
        )
        cbar_width = (
            nws_img.get_extent()[0]/(plt.rcParams['figure.dpi']*x_figsize)
            - noaa_img.get_extent()[1]/(plt.rcParams['figure.dpi']*x_figsize)
        )
        if make_colorbar:
            cax = fig.add_axes(
                [cbar_left, cbar_bottom, cbar_width, cbar_height]
            )
            cbar = fig.colorbar(colorbar_CF,
                                cax = cax,
                                orientation = 'horizontal',
                                ticks = colorbar_CF_ticks)
            cbar.ax.set_xlabel(colorbar_label, labelpad = 0)
            cbar.ax.xaxis.set_tick_params(pad=0)
        #### EMC-evs build savefig name
        savefig_name = os.path.join(output_imgs_dir, stat)
        if date_type == 'VALID':
            if verif_case == 'grid2obs':
                savefig_name = (
                    savefig_name+'_init'+fcst_init_hour.split(', ')[0][0:2]+'Z'
                )
            else:
                savefig_name = (
                    savefig_name+'_valid'+fcst_valid_hour.split(', ')[0][0:2]
                    +'Z'
                )
        elif date_type == 'INIT':
            if verif_case == 'grid2obs':
                savefig_name = (
                    savefig_name+'_valid'+fcst_valid_hour.split(', ')[0][0:2]
                    +'Z'
                )
            else:
                savefig_name = (
                    savefig_name+'_init'+fcst_init_hour.split(', ')[0][0:2]+'Z'
                )
        if verif_case == 'grid2grid' and verif_type == 'anom':
            savefig_name = savefig_name+'_'+var_name+'_'+fcst_var_level
        else:
            savefig_name = savefig_name+'_'+fcst_var_name+'_'+fcst_var_level
        if verif_case == 'precip':
            savefig_name = savefig_name+'_'+fcst_var_thresh
        savefig_name = savefig_name+'_leaddate_'+grid_vx_mask+'.png'
        logger.info("Saving image as "+savefig_name)
        plt.savefig(savefig_name)
        plt.clf()
        plt.close('all')
