import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

#Load and normalize all data
relative_freq = pd.read_csv("Outputs/relative_frequencies.csv")
relative_freq.columns = relative_freq.columns.str.strip().str.lower()

mel_pbmcs = pd.read_csv("Outputs/mel_PBMC_samples_t0.csv")
mel_pbmcs.columns = mel_pbmcs.columns.str.strip().str.lower()

project_counts = pd.read_csv("Outputs/project_sample_nums.csv")
response_counts = pd.read_csv("Outputs/response_subject_nums.csv")
sex_counts = pd.read_csv("Outputs/sex_subject_nums.csv")

cell_pops = pd.read_csv("Outputs/cell_pops_miraclib.csv")
cell_pops.columns = cell_pops.columns.str.strip().str.lower()

cp_time0 = pd.read_csv("Outputs/cp_time0.csv")
cp_time0.columns = cp_time0.columns.str.strip().str.lower()
cp_time7 = pd.read_csv("Outputs/cp_time7.csv")
cp_time7.columns = cp_time7.columns.str.strip().str.lower()
cp_time14 = pd.read_csv("Outputs/cp_time14.csv")
cp_time14.columns = cp_time14.columns.str.strip().str.lower()

stats_time0 = pd.read_csv("Outputs/stats_time0.csv")
stats_time0.columns = stats_time0.columns.str.strip().str.lower()
stats_time7 = pd.read_csv("Outputs/stats_time7.csv")
stats_time7.columns = stats_time7.columns.str.strip().str.lower()
stats_time14 = pd.read_csv("Outputs/stats_time14.csv")
stats_time14.columns = stats_time14.columns.str.strip().str.lower()

population_stats = pd.read_csv("Outputs/population_stats.csv")
population_stats.columns = population_stats.columns.str.strip().str.lower()

#Set the page configuration
st.set_page_config(page_title="Loblaw Bio Clinical Trial Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>Loblaw Bio Clinical Trial Dashboard</h1>", unsafe_allow_html=True)

#Sidebar navigation
page = st.sidebar.radio("Navigate", [
    "Data Overview", 
    "Immune Response Statistics", 
    "Subset Analysis"
])

#Page 1: Data Overview
if page == "Data Overview":
    st.markdown("<h2 style='text-align: center;'>Immune Cell Population Frequencies per Sample</h2>", unsafe_allow_html=True)

    sample_filter = st.multiselect("Filter by Sample ID:", options=relative_freq['sample_id'].unique())
    pop_filter = st.multiselect("Filter by Population:", options=relative_freq['population'].unique())

    filtered = relative_freq.copy()
    if sample_filter:
        filtered = filtered[filtered['sample_id'].isin(sample_filter)]
    if pop_filter:
        filtered = filtered[filtered['population'].isin(pop_filter)]

    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", csv, "filtered_frequencies.csv", "text/csv")

#Page 2: Immune Response Statistics
elif page == "Immune Response Statistics":
    st.markdown("<h2 style='text-align: center;'>Immune Response Statistics</h2>", unsafe_allow_html=True)

    st.subheader("Overall Immune Response (Timepoints 7 and 14 Combined)")

    static_or_interactive = st.radio("View Type:", ["Interactive", "Static (from PNG)"], key="overall_view")

    if static_or_interactive == "Interactive":
        overall_data = pd.concat([cp_time7, cp_time14])
        pop_options = overall_data['population'].unique()
        selected_pops = st.multiselect("Filter by Cell Population:", pop_options, default=list(pop_options), key="overall")
        filtered_overall = overall_data[overall_data['population'].isin(selected_pops)]

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(
            data=filtered_overall,
            x="population",
            y="percentage",
            hue="response",
            ax=ax
        )
        ax.set_title("Comparison of Relative Frequencies of Immune Cell Populations in Miraclib Responders vs. Non-Responders")
        ax.set_ylabel("Relative Frequency (%)")
        ax.set_xlabel("Cell Population")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button("Download Plot as PNG", buf.getvalue(), "overall_immune_response.png", "image/png")
    else:
        static_file = "Outputs/stats_boxplot.png"
        st.image(static_file, caption="Static Boxplot - Combined Timepoints")
        with open(static_file, "rb") as f:
            st.download_button("Download Static Plot", f, file_name=static_file, mime="image/png")

    st.subheader("Immune Response Summary T-Test Results")
    st.dataframe(population_stats.style.applymap(lambda val: 'background-color: yellow' if isinstance(val, (float, int)) and val < 0.05 else '', subset=['p_value']), use_container_width=True)
    st.markdown("<i>Analysis suggests that B-cells and CD4 T-cells have a significant difference in relative frequency between responders and non-responders. Respectively, p=0.011 < 0.05 and p=0.002 < 0.05 (given a significance level of 0.05,). No other populations showed significant differences.</i>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Immune Response by Time from Treatment")

    time_choice = st.selectbox("Select Timepoint:", options=[0, 7, 14])
    view_type = st.radio("View Type:", ["Interactive", "Static (from PNG)"], key=f"view_type_{time_choice}")

    data_map = {0: cp_time0, 7: cp_time7, 14: cp_time14}
    stats_map = {0: stats_time0, 7: stats_time7, 14: stats_time14}
    blurbs = {
        0: "Given a significance level of 0.05, analysis suggests that there is no significant difference in relative frequencies between responders and non-responders when time from treatment = 0.",
        7: "Analysis suggests that CD4 T-cells have a statistically significant difference in relative frequencies between responders and non-responders when time from treatment = 7. Given a significance level of 0.05, p=0.01 < 0.05.",
        14: "Analysis suggests that B-cells have a statistically significant difference in relative frequencies between responders and non-responders when time from treatment = 14. Given a significance level of 0.05, p=0.03 < 0.05."
    }

    if view_type == "Interactive":
        plot_data = data_map[time_choice]

        pop_options = plot_data['population'].unique()
        selected_pops = st.multiselect("Filter by Cell Population:", pop_options, default=list(pop_options), key=f"pops_{time_choice}")
        filtered_plot_data = plot_data[plot_data['population'].isin(selected_pops)]

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(
            data=filtered_plot_data,
            x="population",
            y="percentage",
            hue="response",
            ax=ax
        )
        ax.set_title(f"Frequencies of Immune Cell Populations in Miraclib Responders vs. Non-Responders when Time From Treatment = {time_choice}")
        ax.set_ylabel("Relative Frequency (%)")
        ax.set_xlabel("Cell Population")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button("Download Plot as PNG", buf.getvalue(), f"timepoint_{time_choice}_plot.png", "image/png")
    else:
        static_map = {
            0: "Outputs/stats_boxplot_time0.png",
            7: "Outputs/stats_boxplot_time7.png",
            14: "Outputs/stats_boxplot_time14.png"
        }
        static_file = static_map[time_choice]
        st.image(static_file, caption=f"Static Boxplot - Time {time_choice}")
        with open(static_file, "rb") as f:
            st.download_button("Download Static Plot", f, file_name=static_file, mime="image/png")

    st.subheader("T-Test Results")
    def highlight_significant(val):
        try:
            return 'background-color: yellow' if float(val) < 0.05 else ''
        except:
            return ''

    stat_df = stats_map[time_choice].sort_values("p_value")
    st.dataframe(stat_df.style.applymap(highlight_significant, subset=['p_value']), use_container_width=True)
    st.markdown(f"<i>{blurbs[time_choice]}</i>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Download Source Tables")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "Download Overall Response Data",
            cell_pops.to_csv(index=False).encode('utf-8'),
            "cell_pops_miraclib.csv",
            "text/csv"
        )
        st.download_button(
            "Download Overall Response Stats",
            population_stats.to_csv(index=False).encode('utf-8'),
            "population_stats.csv",
            "text/csv"
        )

    with col2:
        st.download_button(
            "Download Timepoint 0 Data",
            cp_time0.to_csv(index=False).encode('utf-8'),
            "cp_time0.csv",
            "text/csv"
        )
        st.download_button(
            "Download Timepoint 0 Stats",
            stats_time0.to_csv(index=False).encode('utf-8'),
            "stats_time0.csv",
            "text/csv"
        )

    with col3:
        st.download_button(
            "Download Timepoint 7 Data",
            cp_time7.to_csv(index=False).encode('utf-8'),
            "cp_time7.csv",
            "text/csv"
        )
        st.download_button(
            "Download Timepoint 7 Stats",
            stats_time7.to_csv(index=False).encode('utf-8'),
            "stats_time7.csv",
            "text/csv"
        )
        st.download_button(
            "Download Timepoint 14 Data",
            cp_time14.to_csv(index=False).encode('utf-8'),
            "cp_time14.csv",
            "text/csv"
        )
        st.download_button(
            "Download Timepoint 14 Stats",
            stats_time14.to_csv(index=False).encode('utf-8'),
            "stats_time14.csv",
            "text/csv"
        )

#Page 3: Subset Analysis
elif page == "Subset Analysis":
    st.markdown("<h2 style='text-align: center;'>Melanoma PBMC Samples at Basline: Subset Analysis</h2>", unsafe_allow_html=True)

    query_choice = st.selectbox("Choose Analysis Question:", [
        "Baseline melanoma PBMC samples treated with miraclib",
        "How many samples from each project?",
        "How many subjects were responders/non-responders?",
        "How many subjects were males/females?"
    ])

    file_name_map = {
        "Baseline melanoma PBMC samples treated with miraclib": "mel_PBMC_samples_t0.csv",
        "How many samples from each project?": "project_sample_nums.csv",
        "How many subjects were responders/non-responders?": "response_subject_nums.csv",
        "How many subjects were males/females?": "sex_subject_nums.csv"
    }

    table = None
    query_heading = ""

    if query_choice == "Baseline melanoma PBMC samples treated with miraclib":
        query_heading = "Identify all melanoma PBMC samples at baseline (time_from_treatment_start = 0) from patients treated with miraclib:"
        table = mel_pbmcs
    elif query_choice == "How many samples from each project?":
        table = project_counts
    elif query_choice == "How many subjects were responders/non-responders?":
        table = response_counts
    elif query_choice == "How many subjects were males/females?":
        table = sex_counts

    if table is not None:
        if query_heading:
            st.markdown(f"**{query_heading}**")
        st.dataframe(table, use_container_width=True)
        csv = table.to_csv(index=False).encode('utf-8')
        st.download_button("Download This Table", csv, file_name_map[query_choice], "text/csv")

st.markdown("---")
