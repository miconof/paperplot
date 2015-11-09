#!/usr/bin/env python

import os
import sys
import string
import common
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter
from collections import OrderedDict

def mk_clusterstacked(title, xticks, legend, data, data_err=None, ylim=None, xticks_per_bar=None):
    assert(len(legend)==len(data))
    ind = np.arange(len(xticks))                # the x locations for the groups
    barwidth = 1.0/float(num_clustered+1)       # the width of the bars

    # create a new figure and axes instance
    fig = plt.figure(figsize=figure_size) # figure size specified in config
    ax = fig.add_subplot(111)

    # Set ylim and xlim
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlim(right=len(ind))

    # calculate bottoms for stacking
    y = np.row_stack(data)
    # this call to 'cumsum' (cumulative sum), passing in your y data,
    # is necessary to avoid having to manually order the datasets
    y_stack = np.cumsum(y, axis=0)

    # add bars to be printed
    rects = []
    left_empty = barwidth/2.0
    for idx,d in enumerate(data):
        for i in xrange(num_clustered):
            # this gives every n'th element given a starting position 'i'
            # will give the values for a certain configuration for one breakdown component
            dd = d[i::num_clustered]

            # calculate bottoms
            if idx == 0:
                bb = [0] * len(dd)
            else:
                b = y_stack[idx-1]
                bb = b[i::num_clustered]

            assert(len(ind)==len(dd)==len(bb))
            rects.append(ax.bar(left=left_empty+ind+(i*barwidth), height=dd, width=barwidth, bottom=bb,
                            alpha=1, color=colors[idx], ecolor='black', edgecolor='black', hatch=hatch_patterns[idx]))

    # put labels for data bars that overflow ylim
    if ylim and label_enable:
        for i,elem in enumerate(y_stack[idx]):
            if elem > ylim[1]:
                ax.text(x=left_empty+(i*barwidth)+((i/num_clustered)*barwidth)+(barwidth/2.),
                        y=ylim[1]+label_y_space, s='%s'%round(elem,2), ha='center', va='bottom',
                        rotation=label_angle_rotation, fontsize=numbers_fontsize)

    # general formating
    common.set_titles(ax, title, xtitle, ytitle, title_fontsize,
                        xtitle_fontsize, ytitle_fontsize, ylabel_fontsize)

    # xticks possition and labels
    ax.set_xticks(ind + left_empty + (num_clustered/2.0)*barwidth)
    ax.set_xticklabels(xticks,y=-.05, fontsize=xlabel_fontsize)
    plt.gcf().subplots_adjust(bottom=0.2)

    # sublabels for each element of the cluster
    for i in xrange(num_clustered):
        for idx in xrange(len(ind)):
            ax.text(rects[i][idx].get_x()+rects[i][idx].get_width()/2., labels_y, '%s'%xticks_per_bar[i],
                ha='center', va='baseline', fontsize=text_fontsize, rotation=labels_rotation)

    # legend
    leg = ax.legend([a[0] for a in rects[0::num_clustered]], # get the right colors
          legend, # labels
          loc=legend_loc,
          ncol=legend_ncol,
          frameon=True,
          borderaxespad=0.5,
          bbox_to_anchor=bbox,
          fancybox=True,
          #prop={'size':10}, # smaller font size
          )
    for t in leg.get_texts():
        t.set_fontsize(legend_fontsize)    # the legend text fontsize

    # Graph shrinking if desired, no shrinking by default
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * shrink_width_factor, box.height * shrink_height_factor])

    ax.set_axisbelow(True)
    plt.gca().yaxis.grid(color='gray', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    return plt

def mk_clusterstacked_recursively(basedir):
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
                column_names = header[2:]

            # labels, use benchmark names
            xtick_labels = list(OrderedDict.fromkeys([a[xticks_id] for a in data]))

            # get data from specified columns
            columns_data, columns_errdata = common.get_data(data,
                                                        column_ids_data,
                                                        column_ids_err)

            # Add arithmetic and/or geometric means
            if do_add_average:
                print 'Warning AVERAGE not implemented for cluster stacked plots'
                #columns_data, columns_errdata, xtick_labels = common.add_average(columns_data, columns_errdata, xtick_labels)
            if do_add_geomean:
                print 'Warning GEOMEAN not implemented for cluster stacked plots'
                #columns_data, columns_errdata, xtick_labels = common.add_geomean(columns_data, columns_errdata, xtick_labels)

            # set specific ylim for the chart, defined in the config file
            ylim = None
            if fname in my_ylim:
                ylim = my_ylim[fname]

            # get additional xticks_per_bar
            xticks_per_bar_labels = [a[xticks_per_bar_id] for a in data]

            # call the plotting function
            plt = mk_clusterstacked(title=string.capwords(fname) if title == "from-filename" else title,
                              xticks=xtick_labels,
                              legend=column_names,
                              data=columns_data,
                              data_err = columns_errdata,
                              ylim = ylim,
                              xticks_per_bar=xticks_per_bar_labels,
                              )

            # save figure
            plt.savefig("%s/%s.pdf" % (root, fname))


if __name__ == "__main__":

    if len(sys.argv) != 2:
        common.print_usage(__file__)
        exit(1)

    if os.path.isdir(sys.argv[1]):
        mk_clusterstacked_recursively(sys.argv[1]) # will go into subfolders
    else:
        print 'ERROR: Invalid path provided: ' + sys.argv[1]
        common.print_usage(__file__)
        exit(1)

