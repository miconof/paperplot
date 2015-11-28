# paperplot

This is a set of scripts that try to make plotting easy. The scripts use `matplotlib` and are highly configurable by modifying the configuration files.
A valid data file (csv) with a simple format needs to be provided, there are several examples in the `examples` folder.

The `default.config.py` configuration file is always applied and may be modified if a given change has to be applied to all plots.
However, it is recommended to modify settings in each of the local configuration files that can be placed in the same folder the raw data (csv file) is stored.
By default local configuration files should be called `local.config.py`.

To execute and generate the plots for the provided examples you may run:

`python paperplot.py examples`
