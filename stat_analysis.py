'''Part 3: Statistical Analysis'''

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

'''Compare Population Relative Frequencies in Immune Responses from Responders and Non-responders'''
#Connect to the SQLite database
con = sqlite3.connect("Outputs/loblawbio.db")

#Run SQL query to get cell population relative frequency data for melanoma patients receiving miraclib
#Exclude samples taken at time 0 (see following analysis for time 0 that shows no significant differences in initial populations between responders and nonresponders)
cell_pops_miraclib = pd.read_sql_query("""
    SELECT su.subject_id, su.condition, su.treatment, su.response, sa.sample_id, sa.sample_type, totals.total_count, cc.population, cc.count, CAST(100.0 * cc.count AS FLOAT) / totals.total_count AS percentage
    FROM subjects su
    JOIN samples sa ON su.subject_id = sa.subject_id
    JOIN cell_counts cc ON sa.sample_id = cc.sample_id
    JOIN (
        SELECT sample_id, SUM(count) AS total_count
        FROM cell_counts
        GROUP BY sample_id
    ) AS totals ON cc.sample_id = totals.sample_id
    WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start > 0;
    """, con)

# print(cell_pops_miraclib)
cell_pops_miraclib.to_csv("Outputs/cell_pops_miraclib.csv", index=False)

con.close()

#T-test to compare the relative frequencies of populations between responders and non-responders
#Null hypothesis = no difference in relative frequencies between responders and non-responders
#Alternative hypothesis = there's a difference in relative frequencies between responders and non-responders
stats = []

for pop in cell_pops_miraclib['population'].unique():
    responder_vals = cell_pops_miraclib[(cell_pops_miraclib['population'] == pop) & (cell_pops_miraclib['response'] == 'yes')]['percentage']
    non_responder_vals = cell_pops_miraclib[(cell_pops_miraclib['population'] == pop) & (cell_pops_miraclib['response'] == 'no')]['percentage']
    if len(responder_vals) > 0 and len(non_responder_vals) > 0:
        t_stat, p_value = ttest_ind(responder_vals, non_responder_vals, equal_var=False)
        stats.append({
            'population': pop,
            'responder_mean': responder_vals.mean(),
            'non_responder_mean': non_responder_vals.mean(),
            't_statistic': t_stat,
            'p_value': p_value
        })

#Convert stats to DataFrame
stats_df = pd.DataFrame(stats)
print("T-Test Results:")
print(stats_df)
print()
print("Analysis suggests that B-cells and CD4 T-cells have a significant difference in relative frequency between responders and non-responders. Respectively, p=0.011 < p=0.05 and p=0.002 < 0.05 (given a significance level of 0.05). There is no significant difference between the other cell population relative frequencies.")
print()

#Save stats to CSV
stats_df.to_csv("Outputs/population_stats.csv", index=False)

#Boxplot
plt.figure(figsize=(12, 6))
sns.boxplot(x='population', y='percentage', hue='response', data=cell_pops_miraclib)
for i, row in stats_df.iterrows():
    p = row['p_value']
    label = f"p = {p:.3g}"
    y_max = cell_pops_miraclib[cell_pops_miraclib['population'] == row['population']]['percentage'].max()
    plt.text(i, y_max + 1, label, ha='center', fontsize=10)
plt.title('Comparison of Relative Frequencies of Immune Cell Populations in Miraclib Responders vs. Non-Responders')
plt.xlabel('Cell Population')
plt.ylabel('Relative Frequency (%)')
plt.legend(title='Response', loc='upper right')
plt.tight_layout()
plt.savefig("Outputs/stats_boxplot.png")
plt.show()

'''Compare Population Relative Frequencies at Each Time Point from Treatment Start'''
#Day 0 Analysis
con = sqlite3.connect("Outputs/loblawbio.db")

cp_time0 = pd.read_sql_query("""
    SELECT su.subject_id, su.condition, su.treatment, su.response, sa.sample_id, sa.sample_type, sa.time_from_treatment_start, totals.total_count, cc.population, cc.count, CAST(100.0 * cc.count AS FLOAT) / totals.total_count AS percentage
    FROM subjects su
    JOIN samples sa ON su.subject_id = sa.subject_id
    JOIN cell_counts cc ON sa.sample_id = cc.sample_id
    JOIN (
        SELECT sample_id, SUM(count) AS total_count
        FROM cell_counts
        GROUP BY sample_id
    ) AS totals ON cc.sample_id = totals.sample_id
    WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start = 0;
    """, con)

# print(cp_time0)
cp_time0.to_csv("Outputs/cp_time0.csv", index=False)

con.close()

#T-tests
stats = []

for pop in cp_time0['population'].unique():
    responder_vals = cp_time0[(cp_time0['population'] == pop) & (cp_time0['response'] == 'yes')]['percentage']
    non_responder_vals = cp_time0[(cp_time0['population'] == pop) & (cp_time0['response'] == 'no')]['percentage']
    if len(responder_vals) > 0 and len(non_responder_vals) > 0:
        t_stat, p_value = ttest_ind(responder_vals, non_responder_vals, equal_var=False)
        stats.append({
            'population': pop,
            'responder_mean': responder_vals.mean(),
            'non_responder_mean': non_responder_vals.mean(),
            't_statistic': t_stat,
            'p_value': p_value
        })

stats_df = pd.DataFrame(stats)
print("T-Test Results when Time from Treatment = 0:")
print(stats_df)
print()
print("Given a significance level of 0.05, analysis suggests that there is no significant difference in relative frequencies between responders and non-responders when time from treatment = 0.")
print()

stats_df.to_csv("Outputs/stats_time0.csv", index=False)

#Boxplot
plt.figure(figsize=(12, 6))
sns.boxplot(x='population', y='percentage', hue='response', data=cp_time0)
for i, row in stats_df.iterrows():
    p = row['p_value']
    label = f"p = {p:.3g}"
    y_max = cp_time0[cp_time0['population'] == row['population']]['percentage'].max()
    plt.text(i, y_max + 1, label, ha='center', fontsize=10)
plt.title(f'Frequencies of Immune Cell Populations in Miraclib Responders vs. Non-Responders when Time From Treatment = 0')
plt.xlabel('Cell Population')
plt.ylabel('Relative Frequency (%)')
plt.legend(title='Response', loc='upper right')
plt.tight_layout()
plt.savefig("Outputs/stats_boxplot_time0.png")
plt.show()

#Day 7 Analysis
con = sqlite3.connect("Outputs/loblawbio.db")

cp_time7 = pd.read_sql_query("""
    SELECT su.subject_id, su.condition, su.treatment, su.response, sa.sample_id, sa.sample_type, sa.time_from_treatment_start, totals.total_count, cc.population, cc.count, CAST(100.0 * cc.count AS FLOAT) / totals.total_count AS percentage
    FROM subjects su
    JOIN samples sa ON su.subject_id = sa.subject_id
    JOIN cell_counts cc ON sa.sample_id = cc.sample_id
    JOIN (
        SELECT sample_id, SUM(count) AS total_count
        FROM cell_counts
        GROUP BY sample_id
    ) AS totals ON cc.sample_id = totals.sample_id
    WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start = 7;
    """, con)

# print(cp_time7)
cp_time7.to_csv("Outputs/cp_time7.csv", index=False)

con.close()

#T-tests
stats = []

for pop in cp_time7['population'].unique():
    responder_vals = cp_time7[(cp_time7['population'] == pop) & (cp_time7['response'] == 'yes')]['percentage']
    non_responder_vals = cp_time7[(cp_time7['population'] == pop) & (cp_time7['response'] == 'no')]['percentage']
    if len(responder_vals) > 0 and len(non_responder_vals) > 0:
        t_stat, p_value = ttest_ind(responder_vals, non_responder_vals, equal_var=False)
        stats.append({
            'population': pop,
            'responder_mean': responder_vals.mean(),
            'non_responder_mean': non_responder_vals.mean(),
            't_statistic': t_stat,
            'p_value': p_value
        })

stats_df = pd.DataFrame(stats)
print("T-Test Results when Time from Treatment = 7:")
print(stats_df)
print()
print("Analysis suggests that CD4 T-cells have a statistically significant difference in relative frequencies between responders and non-responders when time from treatment = 7. p=0.01 < 0.05 (given a significance level of 0.05). There is no significant difference between the other cell population relative frequencies.")
print()

stats_df.to_csv("Outputs/stats_time7.csv", index=False)

#Boxplot
plt.figure(figsize=(12, 6))
sns.boxplot(x='population', y='percentage', hue='response', data=cp_time7)
for i, row in stats_df.iterrows():
    p = row['p_value']
    label = f"p = {p:.3g}"
    y_max = cp_time7[cp_time7['population'] == row['population']]['percentage'].max()
    plt.text(i, y_max + 1, label, ha='center', fontsize=10)
plt.title(f'Frequencies of Immune Cell Populations in Miraclib Responders vs. Non-Responders when Time From Treatment = 7')
plt.xlabel('Cell Population')
plt.ylabel('Relative Frequency (%)')
plt.legend(title='Response', loc='upper right')
plt.tight_layout()
plt.savefig("Outputs/stats_boxplot_time7.png")
plt.show()

#Day 14 Analysis
con = sqlite3.connect("Outputs/loblawbio.db")

cp_time14 = pd.read_sql_query("""
    SELECT su.subject_id, su.condition, su.treatment, su.response, sa.sample_id, sa.sample_type, sa.time_from_treatment_start, totals.total_count, cc.population, cc.count, CAST(100.0 * cc.count AS FLOAT) / totals.total_count AS percentage
    FROM subjects su
    JOIN samples sa ON su.subject_id = sa.subject_id
    JOIN cell_counts cc ON sa.sample_id = cc.sample_id
    JOIN (
        SELECT sample_id, SUM(count) AS total_count
        FROM cell_counts
        GROUP BY sample_id
    ) AS totals ON cc.sample_id = totals.sample_id
    WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start = 14;
    """, con)

# print(cp_time14)
cp_time14.to_csv("Outputs/cp_time14.csv", index=False)

con.close()

#T-tests
stats = []

for pop in cp_time14['population'].unique():
    responder_vals = cp_time14[(cp_time14['population'] == pop) & (cp_time14['response'] == 'yes')]['percentage']
    non_responder_vals = cp_time14[(cp_time14['population'] == pop) & (cp_time14['response'] == 'no')]['percentage']
    if len(responder_vals) > 0 and len(non_responder_vals) > 0:
        t_stat, p_value = ttest_ind(responder_vals, non_responder_vals, equal_var=False)
        stats.append({
            'population': pop,
            'responder_mean': responder_vals.mean(),
            'non_responder_mean': non_responder_vals.mean(),
            't_statistic': t_stat,
            'p_value': p_value
        })

stats_df = pd.DataFrame(stats)
print("T-Test Results when Time from Treatment = 14:")
print(stats_df)
print()
print("Analysis suggests that B-cells have a statistically significant difference in relative frequencies between responders and non-responders when time from treatment = 14. p=0.03 < 0.05 (given a significance level of 0.05). There is no significant differnce between the other cell population relative frequencies.")
print()

stats_df.to_csv("Outputs/stats_time14.csv", index=False)

#Boxplot
plt.figure(figsize=(12, 6))
sns.boxplot(x='population', y='percentage', hue='response', data=cp_time14)
for i, row in stats_df.iterrows():
    p = row['p_value']
    label = f"p = {p:.3g}"
    y_max = cp_time14[cp_time14['population'] == row['population']]['percentage'].max()
    plt.text(i, y_max + 1, label, ha='center', fontsize=10)
plt.title(f'Frequencies of Immune Cell Populations in Miraclib Responders vs. Non-Responders when Time From Treatment = 14')
plt.xlabel('Cell Population')
plt.ylabel('Relative Frequency (%)')
plt.legend(title='Response', loc='upper right')
plt.tight_layout()
plt.savefig("Outputs/stats_boxplot_time14.png")
plt.show()