#!/usr/bin/env python

import os
import sys
import string
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter
from collections import OrderedDict


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def print_usage(caller):
    USAGE="""
    %(a)s expects a single valid folder as an argument. This folder should contain valid CSV and local configuration files in one or multiple subfolders.

    A number of use cases are provided in the `examples` folder. To test the script and generate the plots run:

        python %(a)s examples/%(c)s
    """ % { 'a' : caller.split('/')[-1] , 'c' : caller.split('/')[-1].split('.')[0] }
    print USAGE


def row_data_process(r):
    return r


def read_csv_file(root, fname, fext):
    # read csv file and return list
    print "Updating the figure %s/%s.pdf" % (root, fname)
    data = mp.mlab.csv2rec('%s/%s%s' % (root, fname, fext))

    d2 = []
    header = []
    for d in data:
        d2.append(row_data_process(d))
    for n in data.dtype.names:
        header.append(row_data_process(n))

    return d2, header


def get_data(data, column_ids_data, column_ids_err):
    # populate columns data
    columns_data = []
    for i in column_ids_data:
        t = [a[i] for a in data]
        columns_data.append(t)

    columns_errdata = []
    for i in column_ids_err:
        t = [a[i] for a in data]
        columns_errdata.append(t)

    return columns_data, columns_errdata


def set_titles(ax, title, xtitle, ytitle, title_fontsize,
                xtitle_fontsize, ytitle_fontsize, ylabel_fontsize):
    ax.set_title(title, fontsize=title_fontsize)
    ax.set_xlabel(xtitle, fontsize=xtitle_fontsize)
    ax.set_ylabel(ytitle, fontsize=ytitle_fontsize)
    for item in ax.get_yticklabels():
        item.set_fontsize(ylabel_fontsize)


def add_average(data, errdata, names):
    for col in data:
        col.append(sum(col)/float(len(col)))

    for col in errdata:
        col.append(sum(col)/float(len(col)))

    names.append('Average')
    return data, errdata, names


def add_geomean(data, errdata, names):
    for col in data:
        col.append(reduce(lambda x, y: x*y, col)**(1.0/len(col)))

    for col in errdata:
        col.append(reduce(lambda x, y: x*y, col)**(1.0/len(col)))

    names.append('Geomean')
    return data, errdata, names


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

    # Set axis scales
    ax.set_yscale(yscale)
    ax.set_xscale(xscale)

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
    set_titles(ax, title, xtitle, ytitle, title_fontsize,
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

    # Set axis scales
    ax.set_yscale(yscale)
    ax.set_xscale(xscale)

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
    set_titles(ax, title, xtitle, ytitle, title_fontsize,
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

    # Graph shrinking if desired, no shrinking by default
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * shrink_width_factor, box.height * shrink_height_factor])

    ax.set_axisbelow(True)
    plt.gca().yaxis.grid(color='gray', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    return plt


def mk_charts(basedir):
    for root, dirs, files in os.walk(basedir):

        # Reset default config and load local config if any
        default_config_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'default.config.py')
        execfile(default_config_path, globals(), globals())

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
            data, header = read_csv_file(root, fname, fext)

            # labels, use benchmark names
            xtick_labels = list(OrderedDict.fromkeys([a[xticks_id] for a in data]))
            #xtick_labels = [a[xticks_id] for a in data]

            # get data from specified columns
            columns_data, columns_errdata = get_data(data,
                                                        column_ids_data,
                                                        column_ids_err)

            if chart_type == "barchart":
                # column names
                if auto_column_names:
                    column_names = header[1:]

                # Add arithmetic and/or geometric means
                if do_add_average:
                    columns_data, columns_errdata, xtick_labels = add_average(columns_data, columns_errdata, xtick_labels)
                elif do_add_geomean:
                    columns_data, columns_errdata, xtick_labels = add_geomean(columns_data, columns_errdata, xtick_labels)

                plt = mk_barchart(title=string.capwords(fname) if title == "from-filename" else title,
                              xticks=xtick_labels,
                              legend=column_names,
                              data=columns_data,
                              data_err = columns_errdata,
                              ylim = ylim,
                              )

            elif chart_type == "clusterstacked":
                # column names
                if auto_column_names:
                    column_names = header[2:]

                # labels, use benchmark names
                #xtick_labels = list(OrderedDict.fromkeys([a[xticks_id] for a in data]))

                # Add arithmetic and/or geometric means
                if do_add_average:
                    print 'Warning AVERAGE not implemented for cluster stacked plots'
                    #columns_data, columns_errdata, xtick_labels = add_average(columns_data, columns_errdata, xtick_labels)
                if do_add_geomean:
                    print 'Warning GEOMEAN not implemented for cluster stacked plots'
                    #columns_data, columns_errdata, xtick_labels = add_geomean(columns_data, columns_errdata, xtick_labels)

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

            elif chart_type == "stacked":
                plt = mk_stacked()
            elif chart_type == "linechart":
                plt = mk_linechart()
            else:
                print "Wrong chart type"
                exit(1)

            #plt.show()
            plt.savefig("%s/%s.pdf" % (root, fname))


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print_usage(__file__)
        exit(1)

    if os.path.isdir(sys.argv[1]):
        mk_charts(sys.argv[1]) # will go into subfolders
    else:
        print 'ERROR: Invalid path provided: ' + sys.argv[1]
        print_usage(__file__)
        exit(1)
