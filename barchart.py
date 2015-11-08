#!/usr/bin/env python

import os
import sys
import string
import common
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter

def mk_barchart(title, xticks, legend, data, data_err=None, ylim=None):
    assert(len(legend)==len(data))
    ind = np.arange(len(xticks))    # the x locations for the groups
    barwidth = 1.0/(len(legend)+1)  # the width of the bars

    # create a new figure and axes instance
    fig = plt.figure(figsize=figure_size) # figure size specified in config
    ax = fig.add_subplot(111)

    # Set ylim and xlim
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlim(right=len(ind))

    # Generate all bars
    rects = []
    left_empty = barwidth/2.0
    for i,d in enumerate(data):
        if data_err:
            errd = data_err[i]
        else:
            errd = None
        rects.append(ax.bar(left=left_empty+ind+i*barwidth, height=d, width=barwidth, alpha=1,
                            color=colors[i], ecolor='black', edgecolor='black', hatch=hatch_patterns[i]))

    # put labels for data bars that overflow ylim
    if ylim and label_enable:
        for i,d in enumerate(data):
            for ii,bar in enumerate(d):
                if bar > ylim[1]:
                    ax.text(x=left_empty+ind[ii]+(i*barwidth)+barwidth/2.,
                            y=ylim[1]+label_y_space, s='%s'%round(bar,2),
                            ha='center', va='bottom',
                            rotation=label_angle_rotation, fontsize=numbers_fontsize)

    # general formating
    common.set_titles(ax, title, xtitle, ytitle, title_fontsize,
                        xtitle_fontsize, ytitle_fontsize, ylabel_fontsize)

    # xticks possition and labels
    ax.set_xticks(ind + left_empty + (len(legend)/2.0)*barwidth)
    ax.set_xticklabels(xticks, fontsize=xlabel_fontsize)
    plt.gcf().subplots_adjust(bottom=0.2)

    # legend
    leg = ax.legend([a[0] for a in rects],
          legend,
          loc=legend_loc,
          ncol=legend_ncol,
          frameon=True,
          borderaxespad=1.,
          bbox_to_anchor=bbox,
          fancybox=True,
          #prop={'size':10}, # smaller font size
          )
    for t in leg.get_texts():
        t.set_fontsize(legend_fontsize)    # the legend text fontsize

    ax.set_axisbelow(True)
    plt.gca().yaxis.grid(color='gray', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    return plt

def mk_barcharts_recursively(basedir):
    for root, dirs, files in os.walk(basedir):

        # Reset default config and load local config if any
        execfile('default.config.py', globals(), globals())

        rootpart = ""
        for d in root.split('/'):
            rootpart += "%s/" % d
            config = "%s%s" % (rootpart, config_fname)
            if os.path.isfile(config):
                execfile(config, globals(), globals())

        # For each file in dir
        for f in files:
            fname, fext = os.path.splitext(f)
            # extensions: csv
            if fext not in EXTENSIONS:
                continue

            # Read csv file, returns a list
            data, header = common.read_csv_file(root, fname, fext)

            # column names
            if auto_column_names:
                column_names = header[1:]

            # labels, use benchmark names
            xtick_labels = [a[xticks_id] for a in data]

            # get data from specified columns
            columns_data, columns_errdata = common.get_data(data,
                                                        column_ids_data,
                                                        column_ids_err)

            # Add arithmetic and/or geometric means
            if do_add_average:
                columns_data, columns_errdata, xtick_labels = common.add_average(columns_data, columns_errdata, xtick_labels)
            if do_add_geomean:
                columns_data, columns_errdata, xtick_labels = common.add_geomean(columns_data, columns_errdata, xtick_labels)

            # set specific ylim for the chart, defined in the config file
            ylim = None
            if fname in my_ylim:
                ylim = my_ylim[fname]

            plt = mk_barchart(title=string.capwords(fname) if title == "from-filename" else title,
                              xticks=xtick_labels,
                              legend=column_names,
                              data=columns_data,
                              data_err = columns_errdata,
                              ylim = ylim,
                              )
            #plt.show()
            plt.savefig("%s/%s.pdf" % (root, fname))

if __name__ == "__main__":

    if len(sys.argv) != 2:
        common.print_usage(__file__)
        exit(1)

    if os.path.isdir(sys.argv[1]):
        mk_barcharts_recursively(sys.argv[1]) # will go into subfolders
    else:
        print 'ERROR: Invalid path provided: ' + sys.argv[1]
        common.print_usage(__file__)
        exit(1)
