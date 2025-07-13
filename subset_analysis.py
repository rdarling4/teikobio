'''Part 4: Data Subset Analysis'''

import pandas as pd
import sqlite3

con = sqlite3.connect("Outputs/loblawbio.db")

#Identify all melanoma PBMC samples at baseline (time_from_treatment_start is 0) from patients who have been treated with miraclib.
mel_PBMC_samples_t0 = pd.read_sql_query("""
    SELECT sa.sample_id
    FROM subjects su
    JOIN samples sa ON su.subject_id = sa.subject_id
    WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start = 0;
    """, con)

print(mel_PBMC_samples_t0)
print()
mel_PBMC_samples_t0.to_csv("Outputs/mel_PBMC_samples_t0.csv", index=False)

#1. How many samples from each project:
project_sample_nums = pd.read_sql_query("""
    SELECT sa.project, COUNT(sa.sample_id) AS sample_count
    FROM subjects su
    JOIN samples sa ON su.subject_id = sa.subject_id
    WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start = 0
    GROUP BY sa.project;
    """, con)

print("Sample counts for each project:")
print(project_sample_nums)
print()
project_sample_nums.to_csv("Outputs/project_sample_nums.csv", index=False)

#2. How many subjects were responders/non-responders:
response_subject_nums = pd.read_sql_query("""
    SELECT su.response, COUNT(DISTINCT su.subject_id) AS subject_count
    FROM subjects su
    JOIN samples sa ON su.subject_id = sa.subject_id
    WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start = 0
    GROUP BY su.response;
    """, con)

print("Subject counts for each response:")
print(response_subject_nums)
print()
response_subject_nums.to_csv("Outputs/response_subject_nums.csv", index=False)

#3. How many subjects were males/females:
sex_subject_nums = pd.read_sql_query("""
    SELECT su.sex, COUNT(su.subject_id) AS subject_count
    FROM subjects su
    JOIN samples sa ON su.subject_id = sa.subject_id
    WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start = 0
    GROUP BY su.sex;
    """, con)

print("Subject counts for M/F:")
print(sex_subject_nums)
print()
sex_subject_nums.to_csv("Outputs/sex_subject_nums.csv", index=False)

con.close()