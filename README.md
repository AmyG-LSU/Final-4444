# 🏡 Home Value Prediction — ten year Forecasting Project

### CSC 4444 — Artificial Intelligence

### Louisiana State University

---

# 📌 Overview

This project forecasts **Louisiana home values ten years into the future** using a combination of socioeconomic indicators, crime statistics, school performance data, and mortgage rate trends.  
We construct a unified **five year aligned dataset** (2015–2019) and build two predictive models:

- **CatBoost Regressor** (gradient-boosted tree model)
- **LSTM Neural Network** (sequence model for time-dependent trends)

This README describes all of these major components: data preparation, five year window extraction, modeling, and repository structure.

---

# 👥 Team & Roles

### **Amy Granados (`AmyG-LSU`) -> Data Loading & Reporting**

- Reads raw CSV/XLSX datasets
- Performs initial cleaning
- Produces exploratory analysis

### **Carter Mauer (`cmauer2`) -> Five Year Period Extraction & Dataset Alignment**

- Determines correct five year modeling window
- Ensures year alignment across income, school ratings, crime, home values, and mortgage rates
- Creates and exports the unified dataset
- Maintains `FIVE_YEAR_PANEL` variables inside `data_loading.py`

### **Nguyen Vu (`NguyenVu2005`) -> CatBoost Modeling**

- Builds CatBoostRegressor
- Tunes hyperparameters
- Generates feature-importance plots

### **Cole Heausler (`c0lbalt`) -> LSTM Modeling**

- Constructs LSTM architecture
- Creates input sequences
- Evaluates long term predictions

### **Malachi Fowler (`MalachiF18`) -> Repository Organization & Documentation**

- Maintains folder structure
- Ensures consistent documentation
- Oversees version control workflow

---

# 🎯 Project Goal

**Predict the value of a Louisiana home ten years from any given starting year.**

### Features Used

- Median household income
- Crime totals
- Home values
- School DPS scores and letter grades
- Mortgage interest rates
- Time-dependent engineered variables

---

# 📂 Repository Structure (Updated)

```
project-root/
│
├── src/
│   ├── data_loading.py
│   ├── catboost_model.py
│   ├── lstm_model.py
│   └── utils/
│
├── data/
│   ├── clean/
│   │   └── five_year_panel_2015_2019.csv
│   ├── Median Household Income/
│   ├── School Data Year/
│   ├── Crime Data Month Year.csv
│   ├── Home Mortgage Rates.xlsx
│   ├── Home Values Month Year.xlsx
│
├── README.md
└── requirements.txt
```

---

# 🧩 Five Year Window Extraction (Carter’s Contribution)

### ✔ Shared Year Coverage

Common years across all datasets:

```
2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023
```

2020 is missing → breaks contiguity.

### ✔ Final Modeling Window

**Most recent valid contiguous five year period: 2015–2019**

### ✔ Dataset Construction

- Clean & load each dataset
- Filter by 2015–2019
- Merge on `(parish, year)`
- Merge mortgage rates by `year`
- Expose:
  ```
  FIVE_YEAR_PANEL
  FIVE_YEAR_START = 2015
  FIVE_YEAR_END   = 2019
  ```

### ✔ Exported Dataset

```
data/clean/five_year_panel_2015_2019.csv
```

---

# 🧠 Methodology Summary

### **1. Data Preparation**

- Manage missing values
- Standardize parish naming
- Align time windows
- Verify duplicates

### **2. Feature Engineering**

- Merge all indicators
- Prepare sequences for LSTM
- Encode categories
- Normalize data when necessary

### **3. Modeling**

- CatBoost for tabular regression
- LSTM for sequential prediction

### **4. Evaluation**

- RMSE, MAE
- Prediction vs actual graphs
- CatBoost feature importance

---

# 🚀 How to Run

## Install Requirements

```
pip install -r requirements.txt
```

## Build Dataset

```
python src/data_loading.py
```

Or within Python:

```python
from src.data_loading import FIVE_YEAR_PANEL
```

## Train CatBoost

```
python src/catboost_model.py
```

## Train LSTM

```
python src/lstm_model.py
```

---

# 📘 Academic Notice

This project is for academic use in CSC 4444.  
Data sources retain their original licenses.
