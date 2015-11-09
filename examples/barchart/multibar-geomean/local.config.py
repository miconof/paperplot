figure_size = (20,6.5)

title=''
xtitle=''
ytitle='Speed-up w.r.t single-threaded execution'

column_ids_data = [1, 2, 3, 4, 5, 6]
column_names = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
column_ids_err = []

bbox=(0.305,0.)
legend_ncol=1
legend_loc=3

my_ylim['multibar-geomean'] = (0, 8.0)

do_add_geomean = True

hatch_patterns = (' ','\\\\','//',' ',' ', ' ')
palette_1 = "#FFFFFF #FFFFFF #FFFFFF #DDDDDD "
palette_2 = "#999999 #444444 #FFFFFF #DDDDDD "

colors = [colorConverter.to_rgb(a) for a in (palette_1 + palette_2).split()]

