# 🥗 Local Food Wastage Management System

A full-stack data project built with **Python · SQLite · Streamlit · Plotly**  
Connecting surplus food providers with those in need — reducing waste, fighting hunger.

---

## 📁 Project Structure

```
food_wastage_project/
│
├── app.py                  ← Main Streamlit application (5 pages)
├── sql_queries.py          ← All 15 SQL analytical queries
├── database_setup.py       ← Creates SQLite DB and loads CSVs
├── generate_data.py        ← Generates realistic sample datasets
│
├── providers_data.csv      ← 50 food providers
├── receivers_data.csv      ← 40 receivers (NGOs, individuals, etc.)
├── food_listings_data.csv  ← 200 food listing records
├── claims_data.csv         ← 150 claim records
│
├── food_wastage.db         ← SQLite database (auto-created)
└── requirements.txt        ← Python dependencies
```

---

## ⚙️ Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate data & create database
```bash
python generate_data.py      # creates the 4 CSV files
python database_setup.py     # creates food_wastage.db and loads data
```

### 3. Launch the Streamlit app
```bash
streamlit run app.py
```
Open your browser at **http://localhost:8501**

---

## 📱 App Pages

| Page | Description |
|------|-------------|
| 🏠 Home Dashboard | KPI metrics, charts, recent claims |
| 📊 SQL Query Explorer | All 15 queries with results & auto-charts |
| 🔍 Filter & Search | Filter food listings, providers, receivers |
| ✏️ CRUD Operations | Add / Update / Delete records |
| 📈 EDA & Visualizations | Heatmaps, trends, scatter plots |

---

## 📊 15 SQL Queries Covered

| # | Query |
|---|-------|
| 1 | Providers & receivers per city |
| 2 | Most contributing provider types |
| 3 | Provider contact info by city |
| 4 | Top receivers by food claims |
| 5 | Total food quantity available |
| 6 | Cities with most food listings |
| 7 | Most common food types |
| 8 | Claims per food item |
| 9 | Providers with most successful claims |
| 10 | Claim status distribution (%) |
| 11 | Average quantity claimed per receiver |
| 12 | Most claimed meal types |
| 13 | Total quantity donated by each provider |
| 14 | Expiring food items (next 7 days) |
| 15 | City-wise claim success rate |

---

## 🗄️ Database Schema

```sql
providers      (Provider_ID, Name, Type, Address, City, Contact)
receivers      (Receiver_ID, Name, Type, City, Contact)
food_listings  (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID,
                Provider_Type, Location, Food_Type, Meal_Type)
claims         (Claim_ID, Food_ID, Receiver_ID, Status, Timestamp)
```

---

## 🎯 Tech Stack
- **Python 3.10+**
- **SQLite** via `sqlite3` (built-in)
- **Pandas** for data manipulation
- **Streamlit** for the web interface
- **Plotly** for interactive charts

---

*Project: Local Food Wastage Management System | Domain: Food Management, Waste Reduction, Social Good*
