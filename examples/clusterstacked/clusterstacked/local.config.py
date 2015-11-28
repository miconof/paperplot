chart_type = "clusterstacked"

xtitle=''
ytitle='Normalized execution time breakdown'
title=''

column_ids_data = [2, 3, 4, 5, 6, 7, 8, 9]
column_ids_err = []

figure_size = (20,6.5)

num_clustered = 3

legend_loc=9
legend_ncol=4

ylim = (0, 1.8)
label_y_space=0.01

palette_1 = "#777777 #FFFFFF #CCCCCC #FFFFFF "
palette_2 = "#DDDDDD #FFFFFF #FFFFFF #DDDDDD "
colors = [colorConverter.to_rgb(a) for a in (palette_1 + palette_2).split()]
