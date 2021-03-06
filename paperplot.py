#!/usr/bin/env python

import os
import sys
import string
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
import csv
from math import log, atan2, degrees
from matplotlib.colors import colorConverter
from collections import OrderedDict
from default_config import *
from pprint import pprint
from adjustText import adjust_text

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def print_usage(caller):
    USAGE="""
    %(a)s expects a single valid folder as an argument. This folder should contain valid CSV and local configuration files in one or multiple subfolders.

    A number of use cases are provided in the `examples` folder. To test the script and generate the plots run:

        python %(a)s examples/%(c)s
    """ % { 'a' : caller.split('/')[-1] , 'c' : caller.split('/')[-1].split('.')[0] }
    print(USAGE)


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
    for item in ax.get_xticklabels():
        item.set_fontsize(xlabel_fontsize)


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

def frange(start, stop, step=1.0):
    f = start
    while f < stop:
        f += step
        yield f

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
        xticks.append("Average")
        for idx,d in enumerate(data):
            for i in xrange(num_clustered):
                dd = d[i::num_clustered]
                d.append(sum(dd)/len(dd))

    if do_add_geomean:
        print('Warning GEOMEAN not implemented for cluster stacked plots')
        #columns_data, columns_errdata, xtick_labels = add_geomean(columns_data, columns_errdata, xtick_labels)

    assert(len(legend)==len(data))
    ind = np.arange(len(xticks))                # the x locations for the groups
    barwidth = (1.0/float(num_clustered+0.5))     # the width of the bars
    one_barwidth = (barwidth/len(data))*0.8       # the width of one bar if not staked

    # create a new figure and axes instance
    fig = plt.figure(figsize=figure_size) # figure size specified in config
    ax = fig.add_subplot(111)

    # Draw horizontal lines
    for line in hlines:
        ax.axhline(line,color="grey",zorder=0)

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
    if stacked: # Draw the bars staked
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
    else: # Draw the bars next to the others
        for idx,d in enumerate(data):
            for i in xrange(num_clustered):
                # this gives every n'th element given a starting position 'i'
                # will give the values for a certain configuration for one breakdown component
                dd = d[i::num_clustered]

                assert(len(ind)==len(dd))
                rects.append(ax.bar(left=left_empty+ind+(i*barwidth)+idx*one_barwidth, height=dd, width=one_barwidth,
                                alpha=1, color=colors[idx], ecolor='black', edgecolor='black', hatch=hatch_patterns[idx]))

    # put labels for data bars that overflow ylim
    if 'ylim' in label_enable:
        for i,elem in enumerate(y_stack[idx]):
            if elem > ylim[1]:
                ax.text(x=left_empty+(i*barwidth)+((i/num_clustered)*barwidth)+(barwidth/2.),
                        y=ylim[1]+label_y_space, s='%s'%round(elem,2), ha='center', va='bottom',
                        rotation=label_angle_rotation, fontsize=numbers_fontsize)
    # put labels for all data bars
    if 'always' in label_enable:
        for i,elem in enumerate(y_stack[idx]):
            if not np.isfinite(elem):
                elem = 0
            ax.text(x=left_empty+(i*barwidth)+((i/num_clustered)*barwidth)+(barwidth/2.),
                        y=elem+label_y_space, s='%s'%round(elem,2), ha='center', va='bottom',
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
            if line_label_enable:
                for j,coord in enumerate(y[i]):
                    # print coord
                    # ax.text(x=left_empty+ind[j]+barwidth/2, y=coord, s='%s'%round(coord,2), ha='center', va='bottom',
                        # rotation=label_angle_rotation, fontsize=numbers_fontsize)
                    plt.annotate('%s'%round(coord,2),
                             xy = (left_empty+ind[j]+barwidth/2, coord), xytext = (10, -10),
                             textcoords = 'offset points', ha = 'center', va = 'center',
                             # bbox = dict(boxstyle = 'round,pad=0.2', fc = 'black', alpha = .3),
                             # arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
                             )


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
    elif yticks:
        ax.set_yticks(yticks)

    # xticks possition and labels
    ax.set_xticks(ind + left_empty + (num_clustered/2.0)*barwidth)
    ax.set_xticklabels(xticks, y=xticks_y, fontsize=xlabel_fontsize, rotation=xticks_rotation)
    plt.gcf().subplots_adjust(bottom=0.2)

    # sublabels for each element of the cluster
    if do_sublabels:
        for i in xrange(num_clustered):
            for idx in xrange(len(ind)):
                if stacked:
                    ax.text(rects[i][idx].get_x()+rects[i][idx].get_width()/2., labels_y, '%s'%xticks_per_bar[i],
                        ha='center', va='baseline', fontsize=text_fontsize, rotation=labels_rotation)
                else:
                    ax.text(rects[i][idx].get_x()+len(data)*(rects[i][idx].get_width()/2.), labels_y, '%s'%xticks_per_bar[i],
                        ha='center', va='baseline', fontsize=text_fontsize, rotation=labels_rotation)

    # legend
    if do_legend:
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
    else:
        leg = ax.legend([], frameon=False)

    # Graph shrinking if desired, no shrinking by default
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * shrink_width_factor, box.height * shrink_height_factor])

    ax.set_axisbelow(True)
    if line_split:
        ax2.set_axisbelow(True)
    plt.gca().yaxis.grid(color='0.5', linestyle='--', linewidth=0.3)
    plt.tight_layout()
    return plt,leg


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
    ax.set_xticklabels(xticks, fontsize=xlabel_fontsize, rotation=xticks_rotation)
    plt.gcf().subplots_adjust(bottom=0.2)

    # legend
    if do_legend:
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
    else:
        leg = ax.legend([], frameon=False)

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
    return plt,leg

def get_line_data(data):
    labels = [a[1] for a in data]
    x = [a[2] for a in data]
    y = [a[3] for a in data]
    return labels, x, y

def angle_between(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return np.rad2deg((ang1 - ang2) % (2 * np.pi))

# expects
# ceilings[0] = [ mem_ceiling_name, ...]
# ceilings[1] = [ GB/s (float) , ...]
# ceilings[2] = [ cpu_ceiling_name, ...]
# ceilings[3] = [ Gflops/s (float) , ...]
# ra format:
# [ "legend elem", "data label", Operational intensity (float) , Gflops/s (float) ]
# [ "legend elem", "data label", Operational intensity (float) , Gflops/s (float) ]
def mk_roofline(title, ceilings, ra):
    alldata, header = parse_recarray(ra)

    mem_ceiling_names = ceilings[0]
    mem_ceiling_values = ceilings[1]
    cpu_ceiling_names = ceilings[2]
    cpu_ceiling_values = ceilings[3]
    application_data = alldata

    names = [elem[0] for elem in application_data]
    legend = list(sorted(set(names), key=names.index)) # Keep order

    # create a new figure and axes instance
    fig = plt.figure(figsize=figure_size) # figure size specified in config
    ax = fig.add_subplot(111)

    # Set axis scales
    ax.set_yscale(yscale, basey=2)
    ax.set_xscale(xscale, basex=2)

    # Set ylim and xlim
    if ylim:
        ax.set_ylim(*ylim)
    try:
        ax.set_xlim(*xlim)
    except NameError:
        pass
    if yticks:
        # ax.set_yticks(np.linspace(ax.get_ybound()[0], ax.get_ybound()[1], num_yticks))
        #plt.locator_params(axis='y', nbins=num_yticks)
        ax.set_yticks(yticks)
    max_flops = max(cpu_ceiling_values)
    max_bw = max(mem_ceiling_values)
    global xticks
    if xticks is None:
        xticks = [2.**i for i in range(-4, int(log(max_flops/float(max_bw),2))+2)]

    ax.set_xticks(xticks)
    x = list(frange(min(xticks), max(xticks), 0.01))

    # Upper bw bound
    for i,elem in enumerate(mem_ceiling_values):
        ax.plot(x, [min(elem*val, float(max_flops)) for val in x], color=mem_linecolors[i], linewidth=3 if i == 0 else 2)
        xdiff = x[10] - x[1]
        ydiff = (x[10]*elem) - (x[1]*elem)
        angle = degrees(atan2(ydiff, xdiff))
        plot_location = np.array([x[1], elem*x[1]])
        trans_angle = plt.gca().transData.transform_angles(np.array((angle,)),
                                                   plot_location.reshape((1, 2)))[0]
        ax.text(x[1], elem*x[1], mem_ceiling_names[i], size=text_fontsize, rotation=trans_angle, horizontalalignment = 'left', verticalalignment = 'bottom')

    # Upper cpu bound
    cpu_text_pos = -len(x) / 6
    for i,elem in enumerate(cpu_ceiling_values):
        ax.plot([max(elem/float(max_bw), val) for val in x], [elem for val in x], color=cpu_linecolors[i], linewidth=3 if i==0 else 2)
        ax.text(x[cpu_text_pos], elem+2, cpu_ceiling_names[i], size=text_fontsize, horizontalalignment='right')
        ax.plot(x[cpu_text_pos/2], elem, marker_patterns[len(cpu_ceiling_values)-1-i], color='k', markersize=marker_sizes[num_points-1-i])

    # Application data
    mylines = []
    mymarkers = []
    for i,elem in enumerate(application_data):
        if i%num_points == 1:
            mylines.append(ax.plot([elem[2],elem[2]], [0, max_flops], color=linecolors[i/num_points],linestyle=line_styles[i%num_points], **lineargs))
        mymarkers.append(ax.plot(elem[2], elem[3], marker_patterns[i%num_points], color=linecolors[i/num_points],
                markersize=marker_sizes[i%num_points],markeredgecolor='k',markeredgewidth=1.5))
        # mymarkers.append(ax.plot(elem[2], elem[3], color=linecolors[i%num_points], label=elem[1]))

    # plot points
    for pnt in points:
        ax.plot(pnt["x"], pnt["y"], color = pnt["color"], marker = pnt["marker"], markersize = pnt["markersize"], mec = pnt["mec"])

    # Draw horizontal lines
    for line in hlines:
        ax.axhline(**line)

    # Draw horizontal lines
    for line in vlines:
        ax.axvline(**line)

    # Draw text labels
    for text in text_labels:
        ax.text(**text)

    # general formating
    set_titles(ax, title, xtitle, ytitle, title_fontsize,
                        xtitle_fontsize, ytitle_fontsize, ylabel_fontsize)

    # Graph shrinking if desired, no shrinking by default
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * shrink_width_factor, box.height * shrink_height_factor])

    # legend
    if do_legend:
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
        for line in leg.get_lines():
            line.set_linewidth(line.get_linewidth()*2)
        for t in leg.get_texts():
            t.set_fontsize(legend_fontsize)    # the legend text fontsize
    else:
        leg = ax.legend([], frameon=False)

    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(plt.ScalarFormatter())
    ax.yaxis.set_major_formatter(plt.ScalarFormatter())
    plt.gca().yaxis.grid(color='0.5', linestyle='--', linewidth=0.3)
    plt.tight_layout()
    return plt,leg

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
        print('Warning AVERAGE not implemented for cluster stacked plots')
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
    try:
        ax.set_xlim(*xlim)
    except NameError:
        pass
    if num_yticks:
        # ax.set_yticks(np.linspace(ax.get_ybound()[0], ax.get_ybound()[1], num_yticks))
        plt.locator_params(axis='y', nbins=num_yticks)
    if num_xticks:
        plt.locator_params(axis='x', nbins=num_xticks)

    global yticks
    if yticks is not None:
        ax.set_yticks(yticks)

    global xticks
    if xticks is not None:
        ax.set_xticks(xticks)

    ax.tick_params(axis='both', which='major', pad=5)
    # Plot x as xticks
    if do_x_as_xticks:
        xticks_labels = [[str(j) for j in elem] for elem in x]
        x = [range(1,len(elem)+1) for elem in x]
        ax.set_xlim(x[0][0]-0.25, x[0][-1]+0.25)
        # xticks possition and labels
        ax.set_xticks(x[0])
        ax.set_xticklabels(xticks_labels[0], fontsize=xlabel_fontsize, rotation=xticks_rotation)
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
            # ax2.set_yticks(np.linspace(ax2.get_ybound()[0], ax2.get_ybound()[1], num_yticks))
            plt.locator_params(axis='y', nbins=num_yticks)
        if num_xticks:
            plt.locator_params(axis='x', nbins=num_xticks)
        ax2.set_ylabel(ytitle2, fontsize=ytitle_fontsize)
        for item in ax2.get_yticklabels():
            item.set_fontsize(ylabel_fontsize)

    # Plot all lines
    mylines = []
    texts = []
    for i,d in enumerate(x):
        if line_split and i >= line_split:
            mylines.append(ax2.plot(x[i], y[i], alpha=1,
                                color=linecolors[i],
                                marker=marker_patterns[i],
                                mec=linecolors[i],
                                linestyle=line_styles[i],
                                **lineargs))
            if do_labels:
                for label, xval, yval in zip(labels[i], x[i], y[i]):
                    # ax2.annotate(label,
                                 # xy = (xval, yval), xytext = xytext_tomarker,
                                 # textcoords = 'offset points', ha = 'center', va = 'center', fontsize = text_fontsize,
                                 # )
                    texts.append(ax2.text(xval,yval,label,size=text_fontsize))
                # adjust_text(texts, arrowprops=dict(arrowstyle="-", color='k', lw=0.5))
                # adjust_text(texts)
        else:
            mylines.append(ax.plot(x[i], y[i], alpha=1,
                                color=linecolors[i],
                                marker=marker_patterns[i],
                                mec=linecolors[i],
                                linestyle=line_styles[i],
                                **lineargs))
            if do_labels:
                for label, xval, yval in zip(labels[i], x[i], y[i]):
                    # ax.annotate(label,
                                 # xy = (xval, yval), xytext = xytext_tomarker,
                                 # textcoords = 'offset points', ha = 'center', va = 'center', fontsize = text_fontsize,
                                 # )
                    texts.append(ax.text(xval,yval,label,size=text_fontsize))
                # adjust_text(texts, arrowprops=dict(arrowstyle="-", color='k', lw=0.5))
                # adjust_text(texts)
    # adjust_text(texts, force_objects=0,force_text=0.05, add_objects=[item for sublist in mylines for item in sublist])
    # adjust_text(texts, force_objects=0, add_objects=[item for sublist in mylines for item in sublist]) # DEFAULT
    adjust_text(texts)
    # adjust_text(texts, arrowprops=dict(arrowstyle="-", color='k', lw=0.5))


    # if do_labels:
        # for i,l in enumerate(labels):
            # for label, xval, yval in zip(labels[i], x[i], y[i]):
                # print label, xval, yval
                # plt.annotate(label,
                             # xy = (xval, yval), xytext = xytext_tomarker,
                             # textcoords = 'offset points', ha = 'center', va = 'center', fontsize = text_fontsize,
                             ## bbox = dict(boxstyle = 'round,pad=0.2', fc = 'black', alpha = .3),
                             ## arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
                             # )

    # plot points
    for pnt in points:
        ax.plot(pnt["x"], pnt["y"], color = pnt["color"], marker = pnt["marker"], markersize = pnt["markersize"], mec = pnt["mec"])

    # Draw horizontal lines
    for line in hlines:
        ax.axhline(**line)

    # Draw text labels
    for text in text_labels:
        ax.text(**text)

    # general formating
    set_titles(ax, title, xtitle, ytitle, title_fontsize,
                        xtitle_fontsize, ytitle_fontsize, ylabel_fontsize)

    # Graph shrinking if desired, no shrinking by default
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * shrink_width_factor, box.height * shrink_height_factor])

    # legend
    if do_legend:
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
    else:
        leg = ax.legend([], frameon=False)

    ax.set_axisbelow(True)
    if line_split:
        ax2.set_axisbelow(True)
    plt.gca().yaxis.grid(color='0.5', linestyle='--', linewidth=0.3)
    plt.tight_layout()
    return plt,leg


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
            print("Updating the figure %s/%s.pdf" % (root, fname))
            ra = mp.mlab.csv2rec('%s/%s%s' % (root, fname, fext), names=headers, skiprows=1)

            if chart_type == "barchart":
                # call the plotting function
                plt,leg = mk_barchart(title=fname if title == "from-filename" else title,
                                    ra=ra)

            elif chart_type == "clusterstacked":
                # call the plotting function
                plt,leg = mk_clusterstacked(title=fname if title == "from-filename" else title,
                                    ra=ra)

            elif chart_type == "stacked":
                # call the plotting function
                plt,leg = mk_stacked()

            elif chart_type == "linechart":
                # call the plotting function
                plt,leg = mk_linechart(title=fname if title == "from-filename" else title,
                                    ra=ra)

            elif chart_type == "roofline":
                # Open the file that contains the ceilings
                filename_ceilings = '%s/%s.cei' % (root, fname)
                with open(filename_ceilings, 'rb') as f:
                    reader = csv.reader(f)
                    ceilings = list(reader)
                for row in [1,3]:
                    for i in range(len(ceilings[row])):
                        ceilings[row][i] = float(ceilings[row][i])

                # call the plotting function
                plt,leg = mk_roofline(title=fname if title == "from-filename" else title,
                                    ceilings=ceilings, ra=ra)

            else:
                print("Wrong chart type")
                exit(1)

            #plt.show()
            plt.savefig("%s/%s.pdf" % (root, fname),bbox_extra_artists=(leg,), bbox_inches='tight')


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print_usage(__file__)
        exit(1)

    if os.path.isdir(sys.argv[1]):
        mk_charts(sys.argv[1]) # will go into subfolders
    else:
        print('ERROR: Invalid path provided: ' + sys.argv[1])
        print_usage(__file__)
        exit(1)
