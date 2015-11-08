################
### barchart ###
################



######################
### clusterstacked ###
######################

# ID of the column that holds xtick labels for the cluster
xticks_per_bar_id = 1

# number of clustered bars for clusterstacked charts
num_clustered = 4

# xtick labels for each element of the cluster
labels_rotation='horizontal'    # rotation
labels_y=-0.08                  # placement w.r.t y=0


###############
### stacked ###
###############



##################
### ALL charts ###
##################

# name of the local configuration files
config_fname = "local.config.py"

# figure size (x,y)
figure_size = (5,4)

# ID of the column that holds the xtick (horizontal) labels
xticks_id = 0

# Column names
column_names = ["First", "Second", "Third"]

# ID of columns holding data and error data
column_ids_data = [1, 2, 3]
column_ids_err = [] # not implemented

# titles and font sizes for figure, x and y axis
title = "from-filename"
xtitle='X-Axis Title'
ytitle='Y-Axis Title'
title_fontsize=20
xtitle_fontsize=16
ytitle_fontsize=17
xlabel_fontsize=15.5
ylabel_fontsize=16
legend_fontsize=20
text_fontsize=14.5
numbers_fontsize=16

# y axes limit
my_ylim = {}

# legend
bbox=(0, 0, 1, 1)       # legend located at the figure corner
legend_ncol = 3         # number of columns for the legend (1 means vertical)
legend_loc = 'best'
# 'best'         : 0, (only implemented for axis legends)
# 'upper right'  : 1,
# 'upper left'   : 2,
# 'lower left'   : 3,
# 'lower right'  : 4,
# 'right'        : 5,
# 'center left'  : 6,
# 'center right' : 7,
# 'lower center' : 8,
# 'upper center' : 9,
# 'center'       : 10,

# labels for bars that overflow ylim
label_enable=1                  # enable labels
label_angle_rotation=0          # rotation angle
label_y_space=0                 # distance after ylim

# Allows modification of the figure bounding box in case some elements
# like the legend get cut off of the figure.
shrink_width_factor=1.
shrink_height_factor=1.

# hatching and marking patterns
hatch_patterns = ( ' ', 'oo', '', '\\\\', 'x', '++', '//', 'O', '..', 'O', '-')
marker_patterns = ( 's' , 'd' , '<' , 'h' , '^' , 'o' , 'p' , 'D' , 'H' ,
 '_' , '>' , 'v' , 'x' , ',', '+' , '*' , ',' , '.' , '1' , '2' , '3' , '4' , )

# colors
# palete_blue_simple = "#0070C0 lightblue"
# palete_contrast = "green yellow lightsteelblue lightblue"
### http://www.netstrider.com/tutorials/HTMLRef/color/
palette_netscape_blue_green = "darkcyan lightseagreen turquoise aqua mediumturquoise cadetblue azure #AFEEEE darkturquoise teal"
# palette_netscape_green = "forestgreen limegreen lime chartreuse lawngreen greenyellow palegreen lightgreen springgreen mediumspringgreen darkgreen seagreen mediumseagreen darkseagreen mediumaquamarine aquamarine green darkolivegreen olivedrab olive"
### http://www.colourlovers.com/palette/944213/forever_lost?widths=0
palette_forever_lost = "#5D4157 #838689 #A8CABA #CAD7B2 #EBE3AA"
### http://www.colourlovers.com/palette/1542449/fighting_the_9-5.?widths=0
palette_fighting = "#262626 #475959 #689493 #9DC4C4 #EBDDC7"
### http://www.colorcombos.com/color-schemes/2/ColorCombo2.html etc
#palette_blue2 = "#097054 #FFDE00 #6599FF #FF9900 "
#palette_blue25 = "#0000FF #FF0000 #FFFFFF #333333 "
#palette_blue15 = "#CC0000 #99FF00 #FFCC00 #3333FF "
palette_1 = "#777777 #FFFFFF #CCCCCC #FFFFFF "
palette_2 = "#DDDDDD #FFFFFF #FFFFFF #DDDDDD "

colors = [colorConverter.to_rgb(a) for a in (palette_1 + palette_2).split()] # use palette_blue2+palette_blue15 for colored

# extensions allows for raw data files
EXTENSIONS=['.csv']

# paper formating - allow only type 1 core fonts
mp.rcParams['ps.useafm'] = True
mp.rcParams['pdf.use14corefonts'] = True
#mp.rcParams['text.usetex'] = True
