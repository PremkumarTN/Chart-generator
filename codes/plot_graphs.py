import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_grouped_horizontal_bars(path, filename, category_col, group_col, palette='muted'):
    """
    Plots a horizontal grouped bar chart showing counts of a categorical column grouped by another column.
    Categories are sorted by total count in descending order.

    Parameters:
        path (str): The input data path only.
        filename (str): The xlsx file name which has data in sheets.
        category_col (str): Name of the categorical column to count.
        group_col (str): Name of the column to group by.
        palette (str or list): Color palette for the groups.
    """
    # Read all sheet names
    filepath = f"{path}/{filename}.xlsx"
    xls = pd.ExcelFile(filepath)
    sheet_names = xls.sheet_names

    # Read and merge all sheets
    df_list = []
    for sheet in sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet)
        df['Movie'] = sheet  # Add sheet name as a column
        df_list.append(df)

    # Combine all into one DataFrame
    dt = pd.concat(df_list, ignore_index=True)
    dt.columns = dt.columns.str.strip()
    dt[category_col] = dt[category_col].str.strip()
    dt[category_col] = dt[category_col].str.capitalize()
    dt[category_col] = dt[category_col].str.replace('/ ', '/', regex=False)
    dt[category_col] = dt[category_col].str.replace(' /', '/', regex=False)
    dt[category_col] = dt[category_col].str.replace(' / ', '/', regex=False)
    dt[category_col] = dt[category_col].str.replace('/', ' or ', regex=False)
    dt[category_col] = dt[category_col].str.replace('-', '', regex=False)
    # Compute grouped counts
    count_df = dt.groupby([category_col, group_col]).size().reset_index(name='count')

    # Compute total counts for sorting
    total_counts = count_df.groupby(category_col)['count'].sum().sort_values(ascending=False)
    count_df[category_col] = pd.Categorical(count_df[category_col], categories=total_counts.index, ordered=True)

    # Plot
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    ax = sns.barplot(
        data=count_df,
        y=category_col,
        x='count',
        hue=group_col,
        orient='h',
        palette=palette
    )

    # Add labels to bars
    for container in ax.containers:
        ax.bar_label(container, label_type='edge', padding=2, fontsize=9)

    title = f"{category_col} Count by {group_col}"

    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel("Count")
    plt.ylabel(category_col)
    plt.tight_layout()
    plt.savefig(f"{path}/{title}.png")
    plt.show()






