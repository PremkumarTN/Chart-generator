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
    dt = dt.astype(str)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        category_col = st.selectbox("Select Column", dt.columns.to_list())    
    with col2:
        chart_type = st.selectbox("Select Chart Type", ["Bar Chart 2", "Bar Chart", "Pie Chart"])
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
    order_map = {"Managaram": 1, "Kaithi": 2, "Master": 3, "Vikram": 4, "Leo": 5,"MANAGARAM": 1, "KAITHI": 2, "MASTER": 3, "VIKRAM": 4, "LEO": 5}
    summary_df["Rank"] = summary_df[group_col].map(order_map)
    summary_df = summary_df.sort_values("Rank").drop(columns="Rank").reset_index(drop=True)
    st.dataframe(summary_df)

    if chart_type == "Bar Chart":
        # Compute grouped counts
        if group_col==category_col:
            count_df = dt.groupby([category_col]).size().reset_index(name='count')
        else:
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

    # =======================
    # BAR CHART 2 (FIXED)
    # =======================
    elif chart_type == "Bar Chart 2":

        # -------------------------------------------------
        # 1. Remove only 'nan' strings from uniques
        # -------------------------------------------------
        all_categories = [
            x for x in dt[category_col].unique()
            if str(x).lower() != "nan"
        ]
        all_groups = [
            x for x in dt[group_col].unique()
            if str(x).lower() != "nan"
        ]

        # -------------------------------------------------
        # 2. Build full index (fill missing combos with 0)
        # -------------------------------------------------
        idx = pd.MultiIndex.from_product(
            [all_categories, all_groups],
            names=[category_col, group_col]
        )

        count_series = (
            dt.groupby([category_col, group_col])
            .size()
            .reindex(idx, fill_value=0)
        )

        count_df = count_series.reset_index(name="count")

        # -------------------------------------------------
        # 3. Apply Movie order ONLY to Movie column
        # -------------------------------------------------
        order_map = {
            "Managaram": 1, "Kaithi": 2, "Master": 3,
            "Vikram": 4, "Leo": 5,
            "MANAGARAM": 1, "KAITHI": 2,
            "MASTER": 3, "VIKRAM": 4, "LEO": 5
        }

        # Category order (only if category IS Movie)
        if category_col == group_col:
            category_order = [
                k for k, _ in sorted(order_map.items(), key=lambda x: x[1])
                if k in count_df[category_col].unique()
            ]
        else:
            category_order = None

        # Group order (Movie)
        group_order = [
            k for k, _ in sorted(order_map.items(), key=lambda x: x[1])
            if k in count_df[group_col].unique()
        ]

        # -------------------------------------------------
        # 4. Convert to categorical safely
        # -------------------------------------------------
        if category_order is not None:
            count_df[category_col] = pd.Categorical(
                count_df[category_col],
                categories=category_order,
                ordered=True
            )

        count_df[group_col] = pd.Categorical(
            count_df[group_col],
            categories=group_order,
            ordered=True
        )

        # -------------------------------------------------
        # 5. Build labels
        # -------------------------------------------------
        group_totals = (
            count_df.groupby(group_col)["count"]
            .transform("sum")
            .replace(0, 1)
        )

        count_df["percent"] = count_df["count"] / group_totals
        count_df["label"] = (
            count_df["count"].astype(str)
            + " ("
            + (count_df["percent"] * 100).round(1).astype(str)
            + "%)"
        )

        # -------------------------------------------------
        # 6. Plot
        # -------------------------------------------------
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")

        ax = sns.barplot(
            data=count_df,
            y=category_col,
            x="count",
            hue=group_col,
            orient="h",
            palette=palette,
            order=category_order,        # None is safe
            hue_order=group_order
        )

        # -------------------------------------------------
        # 7. PERFECT LABEL ALIGNMENT (ORDER-SAFE)
        # -------------------------------------------------
        legend_labels = [t.get_text() for t in ax.legend_.texts]

        for container, group_val in zip(ax.containers, legend_labels):
            for bar, category in zip(container, ax.get_yticklabels()):
                width = bar.get_width()
                if width <= 0:
                    continue

                row = count_df[
                    (count_df[group_col] == group_val) &
                    (count_df[category_col] == category.get_text())
                ]

                if row.empty:
                    continue

                label = row["label"].iloc[0]

                ax.text(
                    width + 0.1,
                    bar.get_y() + bar.get_height() / 2,
                    label,
                    va="center",
                    ha="left",
                    fontsize=9
                )

        # -------------------------------------------------
        # 8. Titles & layout
        # -------------------------------------------------
        title = f"{category_col} Count by {group_col}"
        plt.title(title, fontsize=16, fontweight="bold")
        plt.xlabel("Count")
        plt.ylabel(category_col)
        # plt.legend(loc="lower right", title=group_col)
        # plt.tight_layout()
        ax.legend(
            title=group_col,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=len(ax.containers),
            frameon=False
        )

        plt.tight_layout(rect=[0, 0.1, 1, 1])
    
    # elif chart_type == "Bar Chart 2":
    #     # Build all category+group combinations
    #     all_categories = [x for x in dt[category_col].unique() if str(x).lower() != "nan"]
    #     all_groups = dt[group_col].unique()

    #     # Count, fill missing with 0
    #     # if group_col==category_col:
    #     #     idx = pd.MultiIndex.from_product([all_categories], names=[category_col])
    #     #     count_series = dt.groupby([category_col]).size().reindex(idx, fill_value=0)
    #     # else:
    #     idx = pd.MultiIndex.from_product([all_categories, all_groups], names=[category_col, group_col])
    #     count_series = dt.groupby([category_col, group_col]).size().reindex(idx, fill_value=0)
    #     count_df = count_series.reset_index(name='count')

    #     # Percent by group
    #     group_totals = count_df.groupby(group_col)['count'].transform('sum').replace(0, 1)
    #     count_df['percent'] = count_df['count'] / group_totals

    #     # Label
    #     count_df['label'] = count_df['count'].astype(str) + ' (' + (count_df['percent']*100).round(1).astype(str) + '%)'

    #     # Plot
    #     plt.figure(figsize=(10, 6))
    #     sns.set_theme(style="whitegrid")
    #     ax = sns.barplot(
    #         data=count_df,
    #         y=category_col,
    #         x='count',
    #         hue=group_col if group_col else None,
    #         orient='h',
    #         palette=palette
    #     )
    #     for container, (group_val, group_data) in zip(ax.containers, count_df.groupby(group_col)):
    #         labels = group_data['label'].tolist()
    #         # Filter only real bars
    #         # bars = [bar for bar in container if bar is not None and bar.get_width() > 0]
    #         if len(container) == len(labels):
    #             ax.bar_label(container, labels=labels, label_type='edge', padding=2, fontsize=9)

    #     title = f"{category_col} Count" + (f" by {group_col}" if group_col else "")
    #     plt.title(title, fontsize=16, fontweight='bold')
    #     plt.xlabel("Count")
    #     plt.ylabel(category_col)
    #     if group_col:
    #         plt.legend(loc='lower right', title=group_col)
    #     plt.tight_layout()

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
