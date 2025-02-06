import pandas as pd
import numpy as np
import h5py
from datetime import datetime, timedelta
import sys

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import matplotlib.cm as cm
import matplotlib.colors as colors

def plot_heatmap(data, my_limit, date_p, cut_off_ls, highlight_date,title,savepath):
    n_cut_off = len(cut_off_ls)
    my_min, my_max = -my_limit, my_limit
    plt.figure(figsize=(0.5*n_cut_off, 1),dpi=300)
    plt.imshow(data, cmap='coolwarm', aspect='auto',vmin=my_min, vmax=my_max,origin='lower')
    plt.grid(which='both', color='grey', linestyle='--', linewidth=0.1)

    plt.title(title,size=6)
    plt.xlabel('Date',size=6)
    plt.ylabel('Distance (miles)',size=6)

    plt.xticks(ticks=np.arange(21), labels=date_p.strftime('%m-%d'), rotation=90,size=6)
    plt.yticks(ticks=np.arange(n_cut_off), labels=cut_off_ls,size=6)

    highlight_index = np.where(date_p == highlight_date)[0][0] 
    plt.axvline(x= highlight_index, color='gold', linewidth=1.5, linestyle='-')
    plt.axvline(x= 6.5, color='grey', linewidth=1, linestyle='--')
    plt.axvline(x= 13.5, color='grey', linewidth=1, linestyle='--')

    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=6)  # Adjust tick label size
    cbar.set_label('Visit relative change', fontsize=6) 

    plt.savefig(savepath+'heatmap_{}.png'.format(title),bbox_inches='tight',transparent=True)


def plot_desitination(gdf_main, gdf_destination, gdf_hurricane, col, title,exluding_track=True,ax=None):
    if ax is None:  # Create a new figure and axis if none are provided
        fig, ax = plt.subplots(figsize=(5, 5), dpi=300)
    
    gdf_main.plot(ax=ax, color="lightgrey", edgecolor="white",alpha=0.5,lw=0.2)  # #Plot counties

    # Normalize scaled_re_changes for coloring/ Use LogNorm for logarithmic scaling
    norm = colors.LogNorm(vmin=gdf_destination[col].min(), vmax=gdf_destination[col].max()) #
    cmap = cm.get_cmap('plasma_r')  

    # Create a column in filtered_df for color mapping
    gdf_destination['color'] = gdf_destination[col].apply(lambda x: cmap(norm(x)))
    gdf_destination.plot(ax=ax, color=gdf_destination['color'], edgecolor='none', lw=0.1)
    if exluding_track:
        gdf_hurricane.plot(ax=ax, color='seagreen', edgecolor='none', lw=0.5, alpha=0.5)
    else:
        gdf_hurricane.plot(ax=ax, color='none', edgecolor='seagreen', lw=0.5, alpha=0.5)
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', fraction=0.02, pad=0.04)
    cbar.set_label(f'{col} (log scale)', fontsize=6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_title(title, fontsize=8)
    # plt.show()
    # plt.close()