'''Part 1: Data Management'''

import pandas as pd
import sqlite3

csv = "cell-count.csv"
database = "Outputs/loblawbio.db"

#Load cell_count.csv into a Data Frame
df = pd.read_csv(csv)

#Split csv data into tables
subjects = df[['subject', 'condition', 'age', 'sex', 'treatment', 'response']].drop_duplicates()
subjects.columns = ['subject_id', 'condition', 'age', 'sex',  'treatment', 'response']

samples = df[['sample', 'subject', 'project', 'sample_type', 'time_from_treatment_start']].drop_duplicates()
samples.columns = ['sample_id', 'subject_id', 'project', 'sample_type', 'time_from_treatment_start']

cell_columns = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
cell_counts = df[['sample'] + cell_columns].melt(id_vars='sample', var_name='population', value_name='count')
cell_counts.columns = ['sample_id', 'population', 'count']

#Connect to the SQLite database
con = sqlite3.connect(database)
cur = con.cursor()

#Make tables
cur.executescript("""
DROP TABLE IF EXISTS cell_counts;
DROP TABLE IF EXISTS samples;
DROP TABLE IF EXISTS subjects;

CREATE TABLE subjects (
    subject_id TEXT PRIMARY KEY,
    condition TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT
);

CREATE TABLE samples (
    sample_id TEXT PRIMARY KEY,
    subject_id TEXT,
    project TEXT,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE TABLE cell_counts (
    sample_id TEXT,
    population TEXT,
    count INTEGER,
    PRIMARY KEY (sample_id, population),
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
);
""")

#Insert data into tables
# Subjects
for _, row in subjects.iterrows():
    cur.execute("INSERT OR IGNORE INTO subjects (subject_id, condition, age, sex, treatment, response) VALUES (?, ?, ?, ?, ?, ?)", tuple(row))

# Samples
for _, row in samples.iterrows():
    cur.execute("INSERT OR IGNORE INTO samples (sample_id, subject_id, project, sample_type, time_from_treatment_start) VALUES (?, ?, ?, ?, ?)", tuple(row))

# Cell Counts
for _, row in cell_counts.iterrows():
    cur.execute("INSERT OR IGNORE INTO cell_counts (sample_id, population, count) VALUES (?, ?, ?)", tuple(row))

con.commit()
con.close()

#Print confirmation
print("Data loaded successfully into the database.")