import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from plot_graphs import plot_grouped_horizontal_bars

path = "D:/personal/Selvaraj/data/"
filename = "Analysis Data"
category_col='Shot Size', 
group_col='Movie'

plot_grouped_horizontal_bars(path, filename, category_col=category_col, group_col=group_col, palette='colorblind')
