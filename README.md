# Teiko Technical
Rhiannon Darling  
July 2025  

---

## Link to dashboard  
[https://rdarlingteikotechnical.streamlit.app/](https://rdarlingteikotechnical.streamlit.app/)

---

## Required files  
- `cell-count.csv`  
- `load_data.py`  
- `summary.py`  
- `stat_analysis.py`  
- `subset_analysis.py`  
- `dashboard.py`  *(no need to run it, but it's the code for the interactive dashboard)*

---

## Execution  
1. Run `load_data.py`  
2. Run `summary.py`  
3. Run `stat_analysis.py`  
4. Run `subset_analysis.py`  

---

## Dependencies  
Please make sure to have the following installed:  
- `sqlite3`  
- `pandas`  
- `matplotlib`  
- `seaborn`  
- `scipy`  
- `streamlit` *(if loading `dashboard.py` locally)*

---

## Relational database schema  

My schema has three tables: `subjects`, `samples`, and `cell_counts`.

### `subjects` has 6 columns:
1. `subject_id` (primary key)  
2. `condition`  
3. `age`  
4. `sex`  
5. `treatment`  
6. `response`

### `samples` has 5 columns:
1. `sample_id` (primary key)  
2. `subject_id` (foreign key)  
3. `project`  
4. `sample_type`  
5. `time_from_treatment_start`

### `cell_counts` has 3 columns:
1. `sample_id` (foreign key)  
2. `population`  
3. `count`  
Primary key = (`sample_id`, `population`)

---

I designed this schema to reduce redundancy but keep queries relatively straightforward. It made sense to split subjects and samples into two separate tables since the subject information remained consistent with each of their samples, while each sample has unique information per patient. Additionally, it made sense to split cell counts from the samples in order to have a population column which was necessary moving forward given the directions.

This structure would scale very easily. For example, if more projects need to be added, you simply add more rows in the samples table and if you have new subjects in that project you add them to the subjects table and their samples to the samples table. You can easily add more columns to the tables moving forward as well if more measurements are recorded going forward. Since my relational schema is normalized, any combination of information from the tables can be queried which ensures it will scale well and be very functional to use for any type of analytics you could want to perform.

---

## Code structure

### Part 1 - `load_data.py`  
- Constructs the SQLite schema  
- Inserts the data from `cell-count.csv` into a database named `loblawbio.db`

### Part 2 - `summary.py`  
- Creates a summary table of the relative frequencies of each cell population as outlined in part 2  
- Summary table is saved as `relative_frequencies.csv`

### Part 3 - `stat_analysis.py`  
- Analyzes immune cell population percentages in PBMC samples from patients with melanoma receiving miraclib as a treatment  
**Note:** I only used the data from samples with a `time_from_treatment > 0` to eliminate noise from the baseline samples that had no statistically significant differences between responders and non-responders. I did additional testing after comparing relative frequencies at each of the three time points.  
- Performs t-tests comparing responders vs. non-responders  
- Repeats analysis at key timepoints (0, 7, 14)  
- Exports CSVs of relative frequencies and statistics as well as boxplot PNGs

### Part 4 - `subset_analysis.py`  
- Filters for appropriate PBMC baseline samples  
- Uses queries to determine:  
    1. How many samples from each project  
    2. How many subjects were responders/non-responders  
    3. How many subjects were males/females  
- Prints results as well as exports CSVs of them
