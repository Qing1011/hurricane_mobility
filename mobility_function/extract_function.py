import pandas as pd
import numpy as np
import os
import csv
import ast
# from mobility_matrix_extract import *
import matplotlib.pyplot as plt
from collections import Counter
import geopandas as gpd
import h5py
from datetime import datetime, timedelta

def test():
    print('Hello world')


def remove_CA_non_NY(x,digits):
    """
    digits: int, the number of digits for the category code, when it is tract, should 11, cbg should be 12 
    including the 0 for some states like CA, "06", 
    non_ny means there are visitors come from counties like virginal islan or puerto rico, still us, but we do not look at them, edit the third line
    """
    filtered_no_ca = [item for item in x if 'CA:' not in item]
    filtered_slipt = [cha.split(':') for cha in filtered_no_ca]
    filtered_ca_na = [[c[:digits],int(n)] for c,n in filtered_slipt if n != '']
    return filtered_ca_na


def account_for_loss_visitors(cbg_list_visitor,raw_visitor):
    sum_known_visitors = sum([ x for [_, x] in cbg_list_visitor])
    unknown_visitors = raw_visitor - sum_known_visitors
    assigned_cbg_list_visitor = [[cbg, no+no*unknown_visitors/sum_known_visitors] for [cbg, no] in cbg_list_visitor]
    return assigned_cbg_list_visitor 

def map_visitor_list(cbg_visitor_real, my_map):
    """
    one to one mapping of fips code to fips index
    if some fips code is not in the map, it will be ignored
    """
    # using index location of modzcta is much quicker than search
    vis_fips_list = [(my_map.loc[a, 'county_idx'], b)
                     for (a, b) in cbg_visitor_real if a in my_map.index]  # m_index
    return vis_fips_list

def assign_visits_by_raw_visitors(cbg_list_visitor, multiplier):
    """
    Adjusts and filters visitor data based on a multiplier and exclusion list.

    :param cbg_list_visitor: List of tuples with (fips, visitor count)
    :param multiplier: Value to adjust the visitor count
    :param my_modzcta: List of fips values to be excluded, not been used here, if you have specific fips to exclude, please use this
    :return: Adjusted and filtered list of (fips, visitor count)
    """
    # please check!!!,count errors of their codes')###
    # the sum of visitor num in cbgs > the raw numbers,
    # it suppose to be the noise caused by imposing 4,
    # but there is no cbg has number of people == 4 to adjust
    # therefore, adjust to raw visitors
    # ignore the possible non-ny visitors' weights
    # just rescale to raw visitors not do reassign them!!!!!
    # Filter out entries where the FIPS is in my_modzcta
    # cbg_list_visitor = [(a, b) for (a, b) in cbg_list_visitor if a in my_tract]
    visitor_record_arr = np.array([b for (a, b) in cbg_list_visitor])
    visitor_fips_arr = np.array([a for (a, b) in cbg_list_visitor])
    cbg_list_visitors_real = list(
        zip(visitor_fips_arr, (visitor_record_arr*multiplier)))
    return cbg_list_visitors_real


def find_fips_dayvisits(fips_visitor_list, visits_by_day_list, raw_visits_count):
    # find [fips, the visits by day (a list of j:list of 7 length)]
    vis_daily_matrix = []  # a list of j:list of 7 length,
    for (f, n) in fips_visitor_list:
        vis_daily_j = np.array(visits_by_day_list)/raw_visits_count*n
        # every single visitor number in each cbg distributes to the 7 days
        vis_daily_matrix.append((f, vis_daily_j))
    return vis_daily_matrix


def mobility_extract_per_poi(df_j, M_raw, dates_idx):
    cluster_idx = df_j['cate_idx'].values[0]
    i = df_j['i'].values[0]
    cbg_list_visitors_real = df_j['vis_daily_matrix'].values[0]
    for (j, vis_daily_a) in cbg_list_visitors_real:
        #         if np.sum(np.array(vis_daily_a) < 0):
        #             print(j_data_idx, 'has negative values')
        # else:
        j = int(j)
        M_raw[dates_idx, cluster_idx, i, j] = vis_daily_a + \
            M_raw[dates_idx, cluster_idx, i, j]
    return M_raw

def store_data_to_hdf5(M_raw, dates, start_day, num_cate, num_mod, filepath='../Data/mobility/'):
    """
    Store high dimensional time series data into an HDF5 file.

    Parameters:
    - M_raw: The data to be stored.
    - dates: List of date strings.
    - y: Year as a string.
    - m: Month as a string.
    - num_cate: Number of categories.
    - num_mod: Number of counties.
    - filepath: The path to the HDF5 file, with placeholders for year and month.

    Returns:
    None
    """
    num_days = len(dates)
    y,m,d = start_day.split('-')
    file_name = filepath + 'M_raw_{}{}{}.h5'.format(y, m, d)
    with h5py.File(file_name, 'w') as f:
        for date_idx in range(num_days):
            day_data = M_raw[date_idx, :, :, :]
            date = dates[date_idx]
            dset = f.create_dataset(
                date, (num_cate, num_mod, num_mod), dtype='float64')
            dset[:] = day_data
