'''Part 2: Initial Analysis - Data Overview'''

import pandas as pd
import sqlite3

#Connect to the SQLite database
con = sqlite3.connect("Outputs/loblawbio.db")

#Run SQL query
relative_frequencies = pd.read_sql_query("""
    SELECT cc.sample_id, totals.total_count, cc.population, cc.count, CAST(100.0 * cc.count AS FLOAT) / totals.total_count AS percentage
    FROM cell_counts cc
    JOIN (
        SELECT sample_id, SUM(count) AS total_count
        FROM cell_counts
        GROUP BY sample_id
    ) AS totals ON cc.sample_id = totals.sample_id;
    """, con)

print(relative_frequencies)
relative_frequencies.to_csv("Outputs/relative_frequencies.csv", index=False)

con.close()