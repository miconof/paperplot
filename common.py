# common definitions
import os
import matplotlib as mp

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
