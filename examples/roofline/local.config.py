chart_type = "roofline"

title = "Roofline"
figure_size = (12,8)
ytitle = "GFlop/s"
xtitle = "Operational Intensity (Flop/Byte)"
xscale = 'log'
yscale = 'log'
ylim = (1, 2048)
do_legend = True
num_points = 6
legend_loc = 2

mem_linecolors = ('k', 'red')
cpu_linecolors = ('k', 'k', 'k', 'k', 'k', 'k')
linecolors = ('purple', 'brown', 'darkorange', 'gold', 'green', 'blue', 'k', 'grey')
marker_patterns = ('o', '^', 'v', 'd', 's', 'D')
line_styles = ('-.', '-.')
legend_fontsize = 17
lineargs={
    "linewidth"     : 2
}
yticks = [2**i for i in range(11)]
