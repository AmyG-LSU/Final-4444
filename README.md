# 🏡 Home Value Prediction (10-Year Forecasting Project)

## 📌 Overview
This project aims to **predict the future value of a home 10 years from now** using a combination of historical housing data, socioeconomic indicators, and machine-learning models. The project uses a **five-year cleaned dataset** to train two core models:

- **CatBoost Regressor** — for tabular, gradient-boosted predictions  
- **LSTM Neural Network** — for sequential, time-dependent forecasting

All data preparation, model training, and analysis scripts are included in this repository.

Project planning details and dataset strategy originate from our project notes.

---

# 👥 Team & Roles

### **Amy (`AmyG-LSU`) — Data Loading & Reporting**
- Reads raw CSV/XLSX datasets into Python  
- Performs initial cleaning and organizes dataframes  
- Generates an exploratory data analysis (EDA) summary  
- Contributes to written project reporting  

### **Carter (`cmauer2`) — Five-Year Period Extraction**
- Determines the correct 5-year window to use  
- Extracts, validates, and stores this period as a working dataset variable  
- Ensures alignment across income, crime, school, and home-value series  

### **Nguyen (`NguyenVu2005`) — CatBoost Model**
- Implements CatBoostRegressor  
- Handles preprocessing for categorical / numerical features  
- Tunes hyperparameters and evaluates model performance  
- Produces CatBoost feature-importance reports  

### **Cole (`c0lbalt`) — LSTM Model**
- Designs LSTM architecture for sequential home-value prediction  
- Handles windowing, scaling, and sequence preparation  
- Trains and evaluates the neural network  
- Provides plots of predicted vs. actual values  

### **Malachi (`MalachiF18`) — Repository README & Organization**
- Manages project documentation  
- Maintains a clean, consistent GitHub structure  
- Ensures proper folder organization and version control standards  

---

# 🎯 Project Goal
**Predict the value of a Louisiana home 10 years into the future.**

### Inputs Used
- Current home value  
- Location  
- School quality ratings  
- Crime statistics  
- Median income  
- Income growth  
- Mortgage interest rate trends  

### Open Questions from Project Notes
- How should inflation be incorporated?  
- Should we predict *growth rate* or *actual home value*?  
- How far back should historical data extend? (Team leaning toward 10–15 years)

(See full project notes in `/Project Notes 4444.docx`.)

---

# 📂 Repository Structure

```
project-root/
│
├── src/
│   ├── data_loading.py
│   ├── catboost_model.py
│   ├── lstm_model.py
│   └── utils/ (optional future folder)
│
├── data/
│   ├── Home Values Month Year.csv
│   ├── Crime Data Month Year.csv
│   ├── School Ratings/
│   ├── Income Data/
│   ├── Mortgage Rates.xlsx
│   ├── year datasets (2014–2024)
│   └── cleaned_data.csv
│
├── reports/
│   ├── eda_report.md
│   ├── model_results_catboost.md
│   └── model_results_lstm.md
│
├── Project Notes 4444.docx
├── README.md
└── requirements.txt
```

---

# 🚀 How to Run the Project

### **1. Install Dependencies**
```
pip install -r requirements.txt
```

### **2. Run Data Loading / Cleaning**
```
python src/data_loading.py
```

### **3. Train the CatBoost Model**
```
python src/catboost_model.py
```

### **4. Train the LSTM Model**
```
python src/lstm_model.py
```

---

# 🧠 Methodology Summary

### **1. Data Preparation**
- Load all raw datasets  
- Clean missing values, remove outliers  
- Normalize/standardize when required  
- Align time periods across all sources  

### **2. Feature Engineering**
- Merge datasets by location + year  
- Build multi-year sequences for LSTM  
- Encode categorical variables  

### **3. Modeling**
- **CatBoost** for tabular regression  
- **LSTM** for sequence prediction  

### **4. Evaluation**
- RMSE  
- MAE  
- Prediction error plots  
- Feature importance (CatBoost)  

---

# 📘 Academic Notice
This project is for academic use for CSC 4444 (Artificial Intelligence).  
All contributors retain ownership of their respective work.  
External data sources follow their original usage licenses.