import os
import tempfile
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Chart Generator", layout="wide")
st.title("📊 Movie Analysis Chart-Generator")
uploaded_file = st.file_uploader("Upload an Excel file with Movie data in each sheets", type=["xlsx"])

if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    df_list = []
    for sheet in sheet_names:
        df = pd.read_excel(uploaded_file, sheet_name=sheet)
        df['Movie'] = sheet
        df_list.append(df)


    # Combine all into one DataFrame
    dt = pd.concat(df_list, ignore_index=True)
    st.subheader("📄 Data Preview")
    st.dataframe(dt.head())
    group_col = 'Movie'
    dt.columns = dt.columns.str.strip()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        category_col = st.selectbox("Select Column", dt.columns.to_list())    
    with col2:
        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart"])
    with col3:
        palette = st.selectbox("Select Color Palette", ["Set2", "Dark2", "muted", "colorblind", "husl", "deep"])
    
    dt[category_col] = dt[category_col].str.strip()
    dt[category_col] = dt[category_col].str.capitalize()
    dt[category_col] = dt[category_col].str.replace('/ ', '/', regex=False)
    dt[category_col] = dt[category_col].str.replace(' /', '/', regex=False)
    dt[category_col] = dt[category_col].str.replace(' / ', '/', regex=False)
    dt[category_col] = dt[category_col].str.replace('/', ' or ', regex=False)
    dt[category_col] = dt[category_col].str.replace('-', '', regex=False)
    # Calculate total counts by group_col
    summary_df = dt.groupby(group_col)[category_col].count().reset_index(name="Total")

    # Show KPI-style summary
    st.subheader(f"🔢 Total '{category_col}' Count by '{group_col}'")
    st.dataframe(summary_df)
    if chart_type == "Bar Chart":
        # Compute grouped counts
        count_df = dt.groupby([category_col, group_col]).size().reset_index(name='count')
        
        # Compute total counts for sorting
        total_counts = count_df.groupby(category_col)['count'].sum().sort_values(ascending=False)
        count_df[category_col] = pd.Categorical(count_df[category_col], categories=total_counts.index, ordered=True)


        # Plotting
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
        plt.legend(loc='lower right', title=group_col)
        plt.tight_layout()

    elif chart_type == "Pie Chart":
        if group_col:
            # Multiple pie charts per group
            grouped = dt.groupby(group_col)[category_col].value_counts().unstack(fill_value=0)
            fig, axs = plt.subplots(1, len(grouped), figsize=(6 * len(grouped), 6))
            if len(grouped) == 1:
                axs = [axs]
            for ax, (grp, values) in zip(axs, grouped.iterrows()):
                ax.pie(values, labels=values.index, autopct='%1.1f%%', colors=sns.color_palette(palette, len(values)))
                ax.set_title(f"{category_col} - {grp}")
            title = f"{category_col} Count by {group_col}"
        else:
            title = f"{category_col} Count by {group_col}"
            pie_data = dt[category_col].value_counts()
            plt.figure(figsize=(6, 6))
            plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', colors=sns.color_palette(palette, len(pie_data)))
            plt.title(f"{category_col} Distribution")
            plt.tight_layout()
            plt.clf()

    # Show in Streamlit
    st.subheader("📊 Chart")
    st.pyplot(plt)

    # Save plot to temp path and offer download
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, f"{title}.png")
        plt.savefig(path, dpi=300, bbox_inches='tight')
        with open(path, "rb") as f:
            st.download_button("📥 Download Chart as PNG", f, f"{title}.png", "image/png")

else:
    st.info("📂 Please upload Excel file to begin.")