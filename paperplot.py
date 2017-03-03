#!/usr/bin/env python

import os
import sys
import string
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
import csv
from matplotlib.colors import colorConverter
from collections import OrderedDict
from default_config import *
from pprint import pprint

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


def select_results(ra, rowfilters = None, colfilters = None, sortby = None, newfield = None):
    # apply rowfilter dictionary
    for k,v in rowfilters.items():
        filter_idx = [i for i,s in enumerate(ra[k]) if s in v]
        ra = ra[filter_idx]

    # apply colfilters list
    if colfilters:
        ra = ra[colfilters]

    # add a new field (column) in the recarray
    if newfield:
        new_desc = ra.dtype.descr
        new_desc.insert(1, ('newfield', type(newfield))) # insert dtype in position 1
        y = np.empty(ra.shape, dtype=new_desc)
        for name in ra.dtype.names:
            y[name] = ra[name]
        y['newfield'] = [newfield] * ra.size
        ra = y

    # sortby
    if sortby:
        # for s in sortby:
        ra.sort(order=sortby)

    return ra


def parse_recarray(ra):
    # parse final recarray to obtain header and data objects

    d2 = []
    header = []
    for d in ra:
        d2.append(row_data_process(d))
    for n in ra.dtype.names:
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


def mk_clusterstacked(title, ra):
    # convert ra into header and data objects
    if line_split:
        alldata, header = parse_recarray(ra[:line_split])
        alldata2, header2 = parse_recarray(ra[line_split:])
    else:
        alldata, header = parse_recarray(ra)

    # labels, use benchmark names untill line_split
    xticks = list(OrderedDict.fromkeys([a[xticks_id] for a in alldata]))

    # get additional xticks_per_bar untill line_split
    xticks_per_bar = [a[xticks_per_bar_id] for a in alldata]

    # column names
    if auto_column_names:
        legend = header[2:]
        column_ids_data = range(2, len(legend)+2)

    # get data from specified columns
    data, data_err = get_data(alldata, column_ids_data, column_ids_err)

    # Add arithmetic and/or geometric means
    if do_add_average:
        print 'Warning AVERAGE not implemented for cluster stacked plots'
        #columns_data, columns_errdata, xtick_labels = add_average(columns_data, columns_errdata, xtick_labels)
    if do_add_geomean:
        print 'Warning GEOMEAN not implemented for cluster stacked plots'
        #columns_data, columns_errdata, xtick_labels = add_geomean(columns_data, columns_errdata, xtick_labels)

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


    # Check if secondary y axis
    if line_split:
        names = [elem[0] for elem in alldata2]
        legend2 = list(sorted(set(names), key=names.index)) # Keep order
        legend.extend(legend2)

        labels = []
        x = []
        y = []
        # get data from specified columns
        for b in legend2:
            if do_labels:
                labels.append([elem[1] for elem in alldata2 if elem[0] == b])
                x.append([elem[2] for elem in alldata2 if elem[0] == b])
                y.append([elem[3] for elem in alldata2 if elem[0] == b])
            else:
                x.append([elem[1] for elem in alldata2 if elem[0] == b])
                y.append([elem[2] for elem in alldata2 if elem[0] == b])

        ax2 = ax.twinx()
        ax2.set_yscale(yscale)
        ax2.tick_params(axis='both', which='major', pad=5)
        if do_x_as_xticks:
            ax2.set_xlim(x[0][0]-0.25, x[0][-1]+0.25)
        if ylim2:
            ax2.set_ylim(*ylim2)
        if num_yticks:
            ax2.set_yticks(np.linspace(ax2.get_ybound()[0], ax2.get_ybound()[1], num_yticks))
        ax2.set_ylabel(ytitle2, fontsize=ytitle_fontsize)
        for item in ax2.get_yticklabels():
            item.set_fontsize(ylabel_fontsize)

        # Plot all lines
        mylines = []
        for i,d in enumerate(x):
            mylines.append(ax2.plot(left_empty+ind+barwidth/2, y[i], alpha=1,
                                color=linecolors[i],
                                marker=marker_patterns[i],
                                mec=linecolors[i],
                                linestyle=line_styles[i],
                                **lineargs))

        if do_labels:
            for i,l in enumerate(labels):
                for label, xval, yval in zip(labels[i], x[i], y[i]):
                    plt.annotate(label,
                             xy = (xval, yval), xytext = (10, -10),
                             textcoords = 'offset points', ha = 'center', va = 'center',
                             # bbox = dict(boxstyle = 'round,pad=0.2', fc = 'black', alpha = .3),
                             # arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
                             )

    # general formating
    set_titles(ax, title, xtitle, ytitle, title_fontsize,
                        xtitle_fontsize, ytitle_fontsize, ylabel_fontsize)
    if num_yticks:
        ax.set_yticks(np.linspace(ax.get_ybound()[0], ax.get_ybound()[1], num_yticks))

    # xticks possition and labels
    ax.set_xticks(ind + left_empty + (num_clustered/2.0)*barwidth)
    ax.set_xticklabels(xticks, y=xticks_y, fontsize=xlabel_fontsize)
    plt.gcf().subplots_adjust(bottom=0.2)

    # sublabels for each element of the cluster
    if do_sublabels:
        for i in xrange(num_clustered):
            for idx in xrange(len(ind)):
                ax.text(rects[i][idx].get_x()+rects[i][idx].get_width()/2., labels_y, '%s'%xticks_per_bar[i],
                    ha='center', va='baseline', fontsize=text_fontsize, rotation=labels_rotation)

    # legend
    lencolors = [a[0] for a in rects[0::num_clustered]]
    if line_split:
        lencolors.extend([a[0] for a in mylines])
    leg = ax.legend(lencolors, # get the right colors
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
    if line_split:
        ax2.set_axisbelow(True)
    plt.gca().yaxis.grid(color='0.5', linestyle='--', linewidth=0.3)
    plt.tight_layout()
    return plt


def mk_barchart(title, ra):
    # convert ra into header and data objects
    alldata, header = parse_recarray(ra)

    # labels, use benchmark names
    xticks = list(OrderedDict.fromkeys([a[xticks_id] for a in alldata]))

    # column names
    if auto_column_names:
        legend = header[1:]
        column_ids_data = range(1, len(legend)+1)

    # get data from specified columns
    data, data_err = get_data(alldata, column_ids_data, column_ids_err)

    # Add arithmetic and/or geometric means
    if do_add_average:
        data, data_err, xticks = add_average(data, data_err, xticks)
    elif do_add_geomean:
        data, data_err, xticks = add_geomean(data, data_err, xticks)

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

    # Draw horizontal lines
    for line in hlines:
        ax.axhline(**line)

    # Draw text labels
    for text in text_labels:
        ax.text(**text)

    # Graph shrinking if desired, no shrinking by default
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * shrink_width_factor, box.height * shrink_height_factor])

    ax.set_axisbelow(True)
    if line_split:
        ax2.set_axisbelow(True)
    plt.gca().yaxis.grid(color='0.5', linestyle='--', linewidth=0.3)
    plt.tight_layout()
    return plt

def get_line_data(data):
    labels = [a[1] for a in data]
    x = [a[2] for a in data]
    y = [a[3] for a in data]
    return labels, x, y


# expects ["legend element", "data point label", "x", "y"]
def mk_linechart(title, ra):
    # convert ra into header and data objects
    alldata, header = parse_recarray(ra)

    names = [elem[0] for elem in alldata]
    legend = list(sorted(set(names), key=names.index)) # Keep order

    labels = []
    x = []
    y = []
    # get data from specified columns
    for b in legend:
        if do_labels:
            labels.append([elem[1] for elem in alldata if elem[0] == b])
            x.append([elem[2] for elem in alldata if elem[0] == b])
            y.append([elem[3] for elem in alldata if elem[0] == b])
        else:
            x.append([elem[1] for elem in alldata if elem[0] == b])
            y.append([elem[2] for elem in alldata if elem[0] == b])

    # Add arithmetic and/or geometric means
    if do_add_average:
        print 'Warning AVERAGE not implemented for cluster stacked plots'
    elif do_add_geomean:
        gmean = []
        for i in range(len(y[0])):
            gmean.append(reduce(lambda xx, yy: xx*yy, [elem[i] for elem in y])**(1.0/len(y[0])))
        y.append(gmean)
        legend.append('Geomean')
        x.append(x[0])

    if do_labels:
        assert(len(legend)==len(labels)==len(x)==len(y))
    else:
        assert(len(legend)==len(x)==len(y))

    # create a new figure and axes instance
    fig = plt.figure(figsize=figure_size) # figure size specified in config
    ax = fig.add_subplot(111)

    # Set axis scales
    ax.set_yscale(yscale)
    ax.set_xscale(xscale)

    # Set ylim and xlim
    if ylim:
        ax.set_ylim(*ylim)
    if num_yticks:
        ax.set_yticks(np.linspace(ax.get_ybound()[0], ax.get_ybound()[1], num_yticks))

    ax.tick_params(axis='both', which='major', pad=5)
    # Plot x as xticks
    if do_x_as_xticks:
        xticks_labels = [[str(j) for j in elem] for elem in x]
        x = [range(1,len(elem)+1) for elem in x]
        ax.set_xlim(x[0][0]-0.25, x[0][-1]+0.25)
        # xticks possition and labels
        ax.set_xticks(x[0])
        ax.set_xticklabels(xticks_labels[0], fontsize=xlabel_fontsize)
        plt.gcf().subplots_adjust(bottom=0.2)

    # Check if secondary y axis
    if line_split:
        ax2 = ax.twinx()
        ax2.set_yscale(yscale)
        ax2.tick_params(axis='both', which='major', pad=5)
        if do_x_as_xticks:
            ax2.set_xlim(x[0][0]-0.25, x[0][-1]+0.25)
        if ylim2:
            ax2.set_ylim(*ylim2)
        if num_yticks:
            ax2.set_yticks(np.linspace(ax2.get_ybound()[0], ax2.get_ybound()[1], num_yticks))
        ax2.set_ylabel(ytitle2, fontsize=ytitle_fontsize)
        for item in ax2.get_yticklabels():
            item.set_fontsize(ylabel_fontsize)

    # Plot all lines
    mylines = []
    for i,d in enumerate(x):
        if line_split and i >= line_split:
            mylines.append(ax2.plot(x[i], y[i], alpha=1,
                                color=linecolors[i],
                                marker=marker_patterns[i],
                                mec=linecolors[i],
                                linestyle=line_styles[i],
                                **lineargs))
        else:
            mylines.append(ax.plot(x[i], y[i], alpha=1,
                                color=linecolors[i],
                                marker=marker_patterns[i],
                                mec=linecolors[i],
                                linestyle=line_styles[i],
                                **lineargs))

    if do_labels:
        for i,l in enumerate(labels):
            for label, xval, yval in zip(labels[i], x[i], y[i]):
                plt.annotate(label,
                             xy = (xval, yval), xytext = (10, -10),
                             textcoords = 'offset points', ha = 'center', va = 'center',
                             # bbox = dict(boxstyle = 'round,pad=0.2', fc = 'black', alpha = .3),
                             # arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
                             )

    # general formating
    set_titles(ax, title, xtitle, ytitle, title_fontsize,
                        xtitle_fontsize, ytitle_fontsize, ylabel_fontsize)

    # legend
    leg = ax.legend([a[0] for a in mylines],
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
    if line_split:
        ax2.set_axisbelow(True)
    plt.gca().yaxis.grid(color='0.5', linestyle='--', linewidth=0.3)
    plt.tight_layout()
    return plt


def load_default_config():
    default_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_config.py')
    execfile(default_config_path, globals(), globals())


def mk_charts(basedir):
    for root, dirs, files in os.walk(basedir):

        # Reset default config and load local config if any
        load_default_config()

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

            filename = '%s/%s%s' % (root, fname, fext)

            # csv2rec will lower case the headers, spaces will be converted to underscores, and illegal attribute name characters removed.
            # this is a workaround
            with open(filename, 'r') as f_input:
                 headers = next(csv.reader(f_input))

            # Read csv file, returns a recarray
            print "Updating the figure %s/%s.pdf" % (root, fname)
            ra = mp.mlab.csv2rec('%s/%s%s' % (root, fname, fext), names=headers, skiprows=1)

            if chart_type == "barchart":
                # call the plotting function
                plt = mk_barchart(title=string.capwords(fname) if title == "from-filename" else title,
                                    ra=ra)

            elif chart_type == "clusterstacked":
                # call the plotting function
                plt = mk_clusterstacked(title=string.capwords(fname) if title == "from-filename" else title,
                                    ra=ra)

            elif chart_type == "stacked":
                # call the plotting function
                plt = mk_stacked()

            elif chart_type == "linechart":
                # call the plotting function
                plt = mk_linechart(title=string.capwords(fname) if title == "from-filename" else title,
                                    ra=ra)

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
