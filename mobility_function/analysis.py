import pandas as pd
import numpy as np
import h5py
from datetime import timedelta
# from datetime import date
import datetime
from dateutil.relativedelta import relativedelta, MO

def test():
    print('Hello world')

def h5py_to_4d_array(file_path):
    """
    Convert datasets from an h5py file to a 4D numpy array.

    Parameters:
    - file_path: str, path to the h5py file.

    Returns:
    - 4D numpy array with shape (number_of_dates, d1, d2, d3)
    """
    with h5py.File(file_path, 'r') as f:
        # Get all dataset names (dates) in the file
        dataset_names = list(f.keys())
        
        # Load the datasets into a list of arrays
        data_arrays = [f[date][:] for date in dataset_names]
        
        # Stack the datasets along a new axis to form a 4D numpy array
        combined_array = np.stack(data_arrays, axis=0)
    
    return combined_array


def cos_sim(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)


def get_mondays(year, month):
    # Get the first Monday of the given month
    date = datetime.date(year, month, 1)
    if date.weekday() > 0:  # If the 1st is not a Monday
        date = date + relativedelta(weekday=MO(1))  # Get the next Monday

    # Keep getting Mondays until the next month
    mondays = []
    while date.month == month:
        mondays.append(date.strftime('%d'))  # Store date as string ##'%Y-%m-%d' if you need the whole please store it
        date = date + relativedelta(weeks=1)  # Get the next Monday

    return mondays


def get_diagonal_prob(Ms):
    """
    Ms is a 4D array of shape (7,17,3144,3144)
    sum over the first to get the visits to all categories
    get the diagonal of each day of 3144x3144
    """
    M_sum = np.sum(Ms, axis=1)
    Prob_ts = np.zeros((7, 3144))
    for d_i in range(7):
        M_t = M_sum[d_i]  # Shape: (3144, 3144), summed for the current day
        visits_t = np.sum(M_t, axis=0)  # Total visits per county (shape: 3144)
        print('no visits:', np.sum(visits_t == 0))
        visits_t = np.where(visits_t == 0, 1, visits_t)  # Replace zeros with 1
        Prob_ts[d_i, :] = np.diag(M_t) / visits_t
    return Prob_ts


def get_diagonal(Ms):
    """
    Ms is a 4D array of shape (7,17,3144,3144)
    sum over the first to get the visits to all categories
    get the diagonal of each day of 3144x3144
    Inside county visits
    """
    M_sum = np.sum(Ms, axis=1)
    Visits_ts = np.zeros((7, 3144))
    for d_i in range(7):
        M_t = M_sum[d_i]  # Shape: (3144, 3144), summed for the current day
        Visits_ts[d_i, :] = np.diag(M_t)
    return Visits_ts

def get_travelling_out(Ms,exclude_self=True):
    """
    Ms is a 4D array of shape (7,17,3144,3144)
    sum over the first to get the visits to all categories
    sum over the i to get the visits to all counties
    Outside county visits
    """
    M_sum = np.sum(Ms, axis=1)  # Shape becomes (7, 3144, 3144)
    Out_ts = np.zeros((7, 3144))
    for d_i in range(7):
        M_t = M_sum[d_i]  # Shape: (3144, 3144), summed for the current day
        Out_all = np.sum(M_t, axis=0) # Total visits out per county (shape: 3144)
        if exclude_self:
            Within = np.diag(M_t)  # Visits within the county (shape: 3144)
            Out_ts[d_i, :] = Out_all - Within
        else:
            Out_ts[d_i, :] = Out_all
    return Out_ts

def relave_diff_D(D1, D0):
    """
    D1 and D0 are 2D arrays of shape (7,3144)
    D0 is the base day
    """
    temp = (D1 - D0)/D0
    temp = np.where(np.isinf(temp), 0, temp)
    temp = np.where(np.isnan(temp), 0, temp)
    return temp


def array_summary(array):
    mean = np.mean(array)
    median = np.median(array)
    std_dev = np.std(array)
    variance = np.var(array)
    minimum = np.min(array)
    maximum = np.max(array)
    percentiles = np.percentile(array, [10, 25, 50, 75, 90])  # 25th, 50th (median), 75th percentiles

    print(f"Mean: {mean}")
    print(f"Median: {median}")
    print(f"Standard Deviation: {std_dev}")
    print(f"Variance: {variance}")
    print(f"Minimum: {minimum}")
    print(f"Maximum: {maximum}")
    print(f"Percentiles 10 25 50 75 90: {percentiles}")


def region_mobility(Ms, selected_idx):
    M_within_region = np.zeros((Ms.shape[0], Ms.shape[1],len(selected_idx)))
    M_out_region = np.zeros((Ms.shape[0], Ms.shape[1],len(selected_idx)))
    M_fin_region = np.zeros((Ms.shape[0], Ms.shape[1],len(selected_idx)))
    for d_i in range(Ms.shape[0]):
        for c_i in range(Ms.shape[1]):
            for j_id, j in enumerate(selected_idx):
                v_j = Ms[d_i, c_i, :, j]## from selected region to all other regions
                within_region = np.sum(v_j[selected_idx])
                M_within_region[d_i,c_i,j_id] = within_region
                out_region = np.sum(v_j) - within_region
                M_out_region[d_i,c_i,j_id] = out_region
                
                fv_j = Ms[d_i, c_i, j,:] ### from all regions (including selected regions) to selected region
                flow_in = np.sum(fv_j)
                M_fin_region[d_i,c_i,j_id] = flow_in - within_region ## excluding the selected regions
    return M_within_region, M_out_region, M_fin_region

def region_out_desitination(Ms, selected_idx):
    M_out_desitination = np.zeros((Ms.shape[0], Ms.shape[1], len(selected_idx), Ms.shape[2]))
    # day, category, all counties including selected regions
    for d_i in range(Ms.shape[0]):
        for c_i in range(Ms.shape[1]):
            for j_id, j in enumerate(selected_idx):
                v_j = Ms[d_i, c_i, :, j]## from selected county to all other regions including selected regions
                M_out_desitination[d_i,c_i,j_id,:] = v_j
    return np.sum(M_out_desitination,axis=1)