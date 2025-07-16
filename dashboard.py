import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# ----------------------
# CONFIGURATION & THEME
# ----------------------
st.set_page_config(
    page_title="HR Attrition Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ----------------------
# DATA LOADING & CACHING
# ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("exported_df.csv")
    # Handle missing data gracefully
    df = df.fillna("(Missing)")
    return df

df = load_data()

# ----------------------
# SIDEBAR FILTERS
# ----------------------
st.sidebar.header("\U0001F50D Filter Data")

# Helper: Get unique sorted values for categorical columns
def get_unique_sorted(col):
    return sorted(df[col].dropna().unique())

# Categorical filters
cat_columns = [
     "BusinessTravel", "Department", "Gender", "MaritalStatus"
]
cat_filters = {}
for col in cat_columns:
    options = get_unique_sorted(col)
    selected = st.sidebar.multiselect(f"{col}", options, default=options)
    cat_filters[col] = selected

# Removed numerical filters

# ----------------------
# FILTER DATAFRAME
# ----------------------
def filter_df(df, cat_filters):
    dff = df.copy()
    for col, vals in cat_filters.items():
        dff = dff[dff[col].isin(vals)]
    return dff

filtered_df = filter_df(df, cat_filters)

# ----------------------
# KPI METRICS
# ----------------------
def kpi_metrics(df):
    total_records = len(df)
    avg_income = df["MonthlyIncome"].mean() if total_records > 0 else 0
    attrition_rate = (
        (df["Attrition"] == "Yes").sum() / total_records * 100 if total_records > 0 else 0
    )
    return total_records, avg_income, attrition_rate

total_records, avg_income, attrition_rate = kpi_metrics(filtered_df)

# ----------------------
# MAIN LAYOUT WITH TABS
# ----------------------
tabs = st.tabs(["Overview", "Visualizations", "Data Table"])

# --- OVERVIEW TAB ---
with tabs[0]:
    st.title("\U0001F4CA HR Attrition Dashboard")
    st.markdown("""
    This dashboard provides interactive exploration of HR attrition data.\
    Use the sidebar to filter and explore key metrics, visualizations, and the underlying data.
    """)
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(f"**Total Records**  \n<span style='font-size:2em'>{total_records:,}</span>", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"**Avg. Monthly Income**  \n<span style='font-size:2em'>${avg_income:,.0f}</span>", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"**Attrition Rate**  \n<span style='font-size:2em'>{attrition_rate:.1f}%</span>", unsafe_allow_html=True)

# --- VISUALIZATIONS TAB ---
with tabs[1]:
    st.header("\U0001F4C8 Visualizations")
    col1, col2 = st.columns(2)
    # 1. Bar chart: Attrition ratio per department
    with col1:
        st.subheader("Graph 1: Attrition Ratio by Department")
        # Calculate attrition ratio per department
        dept_attr = (
            filtered_df.groupby("Department")["Attrition"]
            .apply(lambda x: (x == "Yes").sum() / len(x) * 100 if len(x) > 0 else 0)
            .reset_index()
        )
        dept_attr.columns = ["Department", "Attrition Ratio (%)"]
        fig1 = px.bar(
            dept_attr,
            x="Department",
            y="Attrition Ratio (%)",
            color="Department",
            text=dept_attr["Attrition Ratio (%)"].apply(lambda x: f"{x:.1f}%"),
           
        )
        fig1.update_layout(showlegend=False, yaxis_title="Attrition Ratio (%)")
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown(
            "**Insight**:The Sales department's elevated attrition rate suggests potential issues with workload, compensation, management, or career progression. "
            "This trend warrants further investigation to improve retention strategies in Sales. Conversely, R&D’s lower attrition could offer best practices worth replicating in other departments."
        )
    # 2. Bar chart: Attrition % per JobRole in Sales
    with col2:
        st.subheader("Graph 2: Attrition % by JobRole (Sales Dept)")
        # Filter for Sales department
        sales_df = filtered_df[filtered_df["Department"] == "Sales"]
        # Calculate attrition percentage per JobRole
        jobrole_attr = (
            sales_df.groupby("JobRole")["Attrition"]
            .apply(lambda x: (x == "Yes").sum() / len(x) * 100 if len(x) > 0 else 0)
            .reset_index()
        )
        jobrole_attr.columns = ["JobRole", "Attrition %"]
        fig2 = px.bar(
            jobrole_attr,
            x="JobRole",
            y="Attrition %",
            color="JobRole",
            text=jobrole_attr["Attrition %"].apply(lambda x: f"{x:.1f}%"),
            
        )
        fig2.update_layout(showlegend=False, yaxis_title="Attrition %")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(
            "**Insight**:Attrition in the Sales department is highest among Sales Representatives (39.8%), "
            " might indicat on some challenges that need to be invastigate."
        )

    # 3. Bar chart: Attrition % by Gender (Sales Representative)
    st.subheader("Graph 3:Attrition Percentage by Gender for Sales Representatives")
    # Filter for Sales Representative role
    sales_rep_df = filtered_df[filtered_df["JobRole"] == "Sales Representative"]
    # Calculate attrition percentage by Gender
    gender_attr = (
        sales_rep_df.groupby("Gender")["Attrition"]
        .apply(lambda x: (x == "Yes").sum() / len(x) * 100 if len(x) > 0 else 0)
        .reset_index()
    )
    gender_attr.columns = ["Gender", "Attrition %"]
    fig3 = px.bar(
        gender_attr,
        x="Gender",
        y="Attrition %",
        color="Gender",
        text=gender_attr["Attrition %"].apply(lambda x: f"{x:.1f}%"),
       
    )
    fig3.update_layout(showlegend=False, yaxis_title="Attrition %")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(
        "**Insight**:Female Sales Representatives have a higher attrition rate (42.1%) compared to their male counterparts (37.8%). "
        "The data suggests that female Sales Representatives may face unique challenges contributing to a higher turnover rate—"
        "potentially related to workplace culture, support systems, or work-life balance."
    )

    # 4. Bar chart: Attrition Percentage for Female Sales Representatives by Marital Status
    st.subheader("Graph 4: Attrition Percentage for Female Sales Representatives by Marital Status")

    # Filter for Sales Representative role and Female gender
    female_sales_rep_df = filtered_df[
        (filtered_df["JobRole"] == "Sales Representative") & (filtered_df["Gender"] == "Female")
    ]

    # Calculate total number of female sales reps per MaritalStatus
    total_per_marital = (
        female_sales_rep_df
        .groupby("MaritalStatus")
        .size()
        .reset_index(name="TotalCount")
    )

    # Calculate number of female sales reps with Attrition = 'Yes' per MaritalStatus
    attr_yes_per_marital = (
        female_sales_rep_df[female_sales_rep_df["Attrition"] == "Yes"]
        .groupby("MaritalStatus")
        .size()
        .reset_index(name="AttritionYesCount")
    )

    # Merge totals and attrition counts
    attrition_stats = total_per_marital.merge(attr_yes_per_marital, on="MaritalStatus", how="left")
    attrition_stats["AttritionYesCount"] = attrition_stats["AttritionYesCount"].fillna(0)

    # Calculate the ratio (percentage) of female sales reps with Attrition = 'Yes' per MaritalStatus
    attrition_stats["Attrition %"] = (attrition_stats["AttritionYesCount"] / attrition_stats["TotalCount"]) * 100

    # Sort attrition_stats by 'Attrition %' descending to make bars go from high to low
    attrition_stats_sorted = attrition_stats.sort_values("Attrition %", ascending=False)
    fig4 = px.bar(
        attrition_stats_sorted,
        x="MaritalStatus",
        y="Attrition %",
        color="MaritalStatus",
        text=attrition_stats_sorted["Attrition %"].apply(lambda x: f"{x:.1f}%"),
        category_orders={"MaritalStatus": attrition_stats_sorted["MaritalStatus"].tolist()}
    )
    fig4.update_layout(
        yaxis_title="Attrition Percentage (%)",
        xaxis_title="Marital Status",
        showlegend=False
    )
    fig4.update_traces(textposition='outside')
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(
        "**Insight**:Single female Sales Representatives have the highest attrition rate at 68.4%, significantly higher than their divorced (40.0%) and married (7.1%) peers."
    )
    
    #5. Visualize the monthly income among female Sales Representatives by Marital Status
    # Filter for female Sales Representatives
    st.subheader("Graph 5: Monthly Income Distribution by Marital Status (Female Sales Representatives)")
    female_sales_rep_df = filtered_df[
        (filtered_df["JobRole"] == "Sales Representative") & (filtered_df["Gender"] == "Female")
    ]
    # Create a boxplot of MonthlyIncome by MaritalStatus
    fig5 = px.box(
        female_sales_rep_df,
        x="MaritalStatus",
        y="MonthlyIncome",
        color="MaritalStatus",
        points="all"
    )
    fig5.update_layout(showlegend=False, yaxis_title="Monthly Income")
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown(
        "**Insight**:While income medians are relatively similar, single female sales reps experience the most income inequality. Divorced employees show the most stable earnings."
    )
    # 6. Barplot: BusinessTravel distribution for female Sales Representatives, split by MaritalStatus, with attrition percentage ('Yes') above bars

    st.subheader("Graph 6: Business Travel Distribution of Female Sales Representatives by Marital Status (with Attrition %)")

    # Ensure female_sales_rep_df is available (filtered above)
    # female_sales_rep_df = filtered_df[
    #     (filtered_df["JobRole"] == "Sales Representative") & (filtered_df["Gender"] == "Female")
    # ]

    # Count of BusinessTravel per MaritalStatus
    bt_counts = (
        female_sales_rep_df
        .groupby(['MaritalStatus', 'BusinessTravel'])
        .size()
        .reset_index(name='Count')
    )

    # Calculate attrition percentage ('Yes') per BusinessTravel within each MaritalStatus
    attrition_yes = (
        female_sales_rep_df[female_sales_rep_df['Attrition'] == 'Yes']
        .groupby(['MaritalStatus', 'BusinessTravel'])
        .size()
        .reset_index(name='Attr_Yes_Count')
    )

    # Merge counts and attrition counts
    bt_merged = bt_counts.merge(attrition_yes, on=['MaritalStatus', 'BusinessTravel'], how='left')
    bt_merged['Attr_Yes_Count'] = bt_merged['Attr_Yes_Count'].fillna(0)

    # Calculate attrition percentage ('Yes') per group
    bt_merged['Attrition Yes (%)'] = (bt_merged['Attr_Yes_Count'] / bt_merged['Count']) * 100

    # Annotation: Only show 'Yes' attrition percentage above bars
    bt_merged['Annotation'] = bt_merged['Attrition Yes (%)'].apply(lambda x: f"{x:.1f}%" if x > 0 else "")

    # Sort bt_merged so that within each MaritalStatus, BusinessTravel is ordered by Count descending
    bt_merged_sorted = (
        bt_merged.sort_values(['MaritalStatus', 'Count'], ascending=[True, False])
        .copy()
    )

    # For each MaritalStatus, get the order of BusinessTravel by Count descending
    business_travel_orders = (
        bt_merged_sorted.groupby('MaritalStatus')['BusinessTravel']
        .apply(list)
        .to_dict()
    )

    # To make the bars go from high to low, we need to sort the BusinessTravel categories for each MaritalStatus by Count descending.
    # We'll create a new category_orders dict for BusinessTravel per MaritalStatus, and use it in the plot.

    # Create a category order for BusinessTravel within each MaritalStatus, sorted by Count descending
    business_travel_orders_desc = (
        bt_merged_sorted.groupby('MaritalStatus')
        .apply(lambda df: df.sort_values('Count', ascending=False)['BusinessTravel'].tolist())
        .to_dict()
    )

    # For the plotly express facet_col, we need a single order for BusinessTravel, so we use the union of all orders, preserving the most frequent first
    from collections import OrderedDict
    all_bt = []
    for order in business_travel_orders_desc.values():
        all_bt.extend(order)
    # Remove duplicates, preserve order
    all_bt_unique = list(OrderedDict.fromkeys(all_bt))

    fig6 = px.bar(
        bt_merged_sorted,
        x="BusinessTravel",
        y="Count",
        color="BusinessTravel",
        text="Annotation",
        facet_col="MaritalStatus",
        category_orders={
            "BusinessTravel": all_bt_unique,
            "MaritalStatus": list(business_travel_orders_desc.keys())
        },
    )

    # For each facet, update the x-axis category order to match the sorted order (high to low)
    for i, marital_status in enumerate(business_travel_orders_desc.keys()):
        axis_name = f'xaxis{i+1}' if i > 0 else 'xaxis'
        fig6.layout[axis_name].categoryorder = 'array'
        fig6.layout[axis_name].categoryarray = business_travel_orders_desc[marital_status]

    fig6.update_traces(textposition='outside')
    fig6.update_layout(showlegend=False, yaxis_title="Number of Female Sales Representatives")
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown(
        "**Insight**:Single female Sales Representatives who travel frequently for business face the highest attrition rate at 100%, followed by those who travel rarely (54.5%). In contrast, married and divorced counterparts show significantly lower attrition, especially among non-travelers. This suggests that frequent business travel may be a key driver of attrition among single women, potentially due to lack of personal support or work-life balance challenges."
    )
    # 7. Heatmap: Attrition percentage by MaritalStatus and YearsInCurrentRole
    st.subheader("Graph 7:Attrition Percentage by Marital Status and Years in Current Role")
    # Create a pivot table for heatmap: rows=MaritalStatus, columns=YearsInCurrentRole, values=AttritionPercent
    # First, calculate attrition percentage for each group
    heatmap_data = (
        filtered_df.groupby(['MaritalStatus', 'YearsInCurrentRole'])
        .agg(
            Total=('Attrition', 'count'),
            Attr_Yes=('Attrition', lambda x: (x == 'Yes').sum())
        )
        .reset_index()
    )
    heatmap_data['AttritionPercent'] = (heatmap_data['Attr_Yes'] / heatmap_data['Total']) * 100

    # Pivot table: rows=MaritalStatus, columns=YearsInCurrentRole, values=AttritionPercent
    heatmap_pivot = heatmap_data.pivot_table(
        index='MaritalStatus',
        columns='YearsInCurrentRole',
        values='AttritionPercent',
        fill_value=0.0
    )

    # Clean up: sort index and columns for better readability
    heatmap_pivot = heatmap_pivot.sort_index()
    heatmap_pivot = heatmap_pivot.reindex(sorted(heatmap_pivot.columns), axis=1)

    # Plotly heatmap with visually appealing style
    import plotly.graph_objects as go

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns.astype(str),
            y=heatmap_pivot.index,
            colorscale='YlOrRd',
            colorbar=dict(title='Attrition %'),
            zmin=0,
            zmax=100,
            text=[[f"{val:.1f}%" for val in row] for row in heatmap_pivot.values],
            texttemplate="%{text}",
            hovertemplate="MaritalStatus: %{y}<br>YearsInCurrentRole: %{x}<br>Attrition: %{z:.1f}%<extra></extra>"
        )
    )
    fig_heatmap.update_layout(
        xaxis_title="Years in Current Role",
        yaxis_title="Marital Status",
        template="plotly_white",
        font=dict(size=14),
        margin=dict(l=60, r=20, t=60, b=40)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown(
        "**Insight**:Attrition is highest among single employees in their first year (46.3%) and spikes again around the 15th year (50.0%) in their current role. In contrast, married and divorced employees show more stable and consistently lower attrition across all tenure levels."
    )
    # 8. Distribution of Attrition by Marital Status within Work Life Balance (for Female Sales Representatives)
    st.subheader("Graph 8:Attrition Distribution by Marital Status within Work Life Balance (Female Sales Representatives)")
    # Filter for female Sales Representatives
    female_salesrep_df = filtered_df[
        (filtered_df['Gender'] == 'Female') &
        (filtered_df['JobRole'] == 'Sales Representative')
    ]

    # Group by WorkLifeBalance, MaritalStatus, and Attrition, then count
    dist_data = (
        female_salesrep_df
        .groupby(['WorkLifeBalance', 'MaritalStatus', 'Attrition'])
        .size()
        .reset_index(name='Count')
    )

    # Calculate percentage within each WorkLifeBalance and MaritalStatus
    dist_data['Total'] = dist_data.groupby(['WorkLifeBalance', 'MaritalStatus'])['Count'].transform('sum')
    dist_data['Percent'] = (dist_data['Count'] / dist_data['Total']) * 100

    # Pivot for stacked bar chart: x=WorkLifeBalance, color=Attrition, facet=MaritalStatus
    import plotly.express as px

    # Add index explanation for WorkLifeBalance
    st.markdown(
        """
        **Work Life Balance Index:**  
        1 - Bad &nbsp;&nbsp;|&nbsp;&nbsp; 2 - Not Bad &nbsp;&nbsp;|&nbsp;&nbsp; 3 - Good &nbsp;&nbsp;|&nbsp;&nbsp; 4 - Best
        """
    )

    fig_dist = px.bar(
        dist_data,
        x='WorkLifeBalance',
        y='Percent',
        color='Attrition',
        barmode='stack',
        facet_col='MaritalStatus',
        category_orders={
            'WorkLifeBalance': [1, 2, 3, 4],  
            'MaritalStatus': sorted(dist_data['MaritalStatus'].unique()),
            'Attrition': ['No', 'Yes']
        },
        labels={
            'WorkLifeBalance': 'Work Life Balance',
            'Percent': 'Percentage',
            'Attrition': 'Attrition'
        },
    )
        
    fig_dist.update_layout(
        template="plotly_white",
        font=dict(size=14),
        margin=dict(l=40, r=20, t=60, b=40),
        legend_title_text='Attrition'
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown(
        "**Insight**: Even under the best work-life balance conditions (WLB = 4),single female Sales Representatives continue to show 100% attrition, while married counterparts show near-total retention across all WLB levels. This indicates that work-life balance alone is not enough to retain single employees, and their attrition may be influenced by other unmet needs—such as job satisfaction, growth opportunities, or emotional support in the workplace."
    )


    # --- DATA TABLE TAB ---
    with tabs[2]:
        st.header("\U0001F5C3 Data Table")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_hr_data.csv",
            mime="text/csv"
        )

# ----------------------
# FOOTER
# ----------------------
st.markdown("""
---
*Built with Streamlit, Plotly, and Pandas.*
""") 