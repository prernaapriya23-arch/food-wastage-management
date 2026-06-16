"""
app.py  –  Local Food Wastage Management System
Streamlit multi-page application with:
  • Home / Dashboard
  • SQL Query Explorer (all 15 queries)
  • Filter & Search
  • CRUD Operations
  • EDA & Visualizations
"""

import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import date
from sql_queries import QUERIES

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a3a2a; }
    [data-testid="stSidebar"] * { color: #d4edda !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a3a2a, #2d6a4f);
        border-radius: 12px;
        padding: 14px;
        border-left: 4px solid #52b788;
        color: white;
    }
    [data-testid="metric-container"] label { color: #b7e4c7 !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #ffffff !important; }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #1a3a2a, #2d6a4f);
        color: #d4edda;
        padding: 10px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 18px;
        font-weight: 600;
    }

    /* Query card */
    .query-card {
        background: #f0faf4;
        border-left: 4px solid #52b788;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }

    /* Success banner */
    .success-msg {
        background: #d4edda;
        border: 1px solid #52b788;
        padding: 10px 16px;
        border-radius: 6px;
        color: #1a3a2a;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

import os

# ── Paths (work regardless of working directory) ────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "food_wastage.db")

def _build_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS providers (Provider_ID INTEGER PRIMARY KEY, Name TEXT, Type TEXT, Address TEXT, City TEXT, Contact TEXT);
    CREATE TABLE IF NOT EXISTS receivers (Receiver_ID INTEGER PRIMARY KEY, Name TEXT, Type TEXT, City TEXT, Contact TEXT);
    CREATE TABLE IF NOT EXISTS food_listings (Food_ID INTEGER PRIMARY KEY, Food_Name TEXT, Quantity INTEGER, Expiry_Date TEXT, Provider_ID INTEGER, Provider_Type TEXT, Location TEXT, Food_Type TEXT, Meal_Type TEXT);
    CREATE TABLE IF NOT EXISTS claims (Claim_ID INTEGER PRIMARY KEY, Food_ID INTEGER, Receiver_ID INTEGER, Status TEXT, Timestamp TEXT);
    """)
    conn.commit()
    for tbl, csv in [("providers","providers_data.csv"),("receivers","receivers_data.csv"),("food_listings","food_listings_data.csv"),("claims","claims_data.csv")]:
        p = os.path.join(BASE_DIR, csv)
        if os.path.exists(p):
            pd.read_csv(p).to_sql(tbl, conn, if_exists="replace", index=False)
    conn.close()

def _db_ok():
    if not os.path.exists(DB_PATH): return False
    try:
        conn = sqlite3.connect(DB_PATH)
        ok = all(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]>0 for t in ["providers","receivers","food_listings","claims"])
        conn.close()
        return ok
    except: return False

if not _db_ok(): _build_db()

# ── DB helpers ─────────────────────────────────────────────────────────────────
def _build_database():
    """Create the SQLite DB from the CSV files if it doesn't exist or is empty/invalid."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS providers (
        Provider_ID   INTEGER PRIMARY KEY,
        Name          TEXT NOT NULL,
        Type          TEXT,
        Address       TEXT,
        City          TEXT,
        Contact       TEXT
    );
    CREATE TABLE IF NOT EXISTS receivers (
        Receiver_ID   INTEGER PRIMARY KEY,
        Name          TEXT NOT NULL,
        Type          TEXT,
        City          TEXT,
        Contact       TEXT
    );
    CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID       INTEGER PRIMARY KEY,
        Food_Name     TEXT NOT NULL,
        Quantity      INTEGER,
        Expiry_Date   TEXT,
        Provider_ID   INTEGER,
        Provider_Type TEXT,
        Location      TEXT,
        Food_Type     TEXT,
        Meal_Type     TEXT
    );
    CREATE TABLE IF NOT EXISTS claims (
        Claim_ID      INTEGER PRIMARY KEY,
        Food_ID       INTEGER,
        Receiver_ID   INTEGER,
        Status        TEXT,
        Timestamp     TEXT
    );
    """)
    conn.commit()

    tables = {
        "providers":     "providers_data.csv",
        "receivers":     "receivers_data.csv",
        "food_listings": "food_listings_data.csv",
        "claims":        "claims_data.csv",
    }
    for table, csv_file in tables.items():
        csv_path = os.path.join(BASE_DIR, csv_file)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()


def _database_ready() -> bool:
    """Check the DB exists and has data in all 4 tables."""
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        for tbl in ["providers", "receivers", "food_listings", "claims"]:
            count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            if count == 0:
                conn.close()
                return False
        conn.close()
        return True
    except Exception:
        return False


# Auto-build the database on first run (or if it's missing/corrupted)
if not _database_ready():
    _build_database()


@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def run_query(sql: str, params=()) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query(sql, conn, params=params)

def execute_dml(sql: str, params=()):
    conn = get_connection()
    conn.execute(sql, params)
    conn.commit()

def get_cities():
    return sorted(run_query("SELECT DISTINCT City FROM providers")["City"].tolist())

def get_food_types():
    return sorted(run_query("SELECT DISTINCT Food_Type FROM food_listings")["Food_Type"].tolist())

def get_meal_types():
    return sorted(run_query("SELECT DISTINCT Meal_Type FROM food_listings")["Meal_Type"].tolist())

def get_provider_types():
    return sorted(run_query("SELECT DISTINCT Type FROM providers")["Type"].tolist())

# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/food-bank.png", width=80)
    st.markdown("## 🥗 Food Wastage\nManagement System")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Home Dashboard",
         "📊 SQL Query Explorer",
         "🔍 Filter & Search",
         "✏️ CRUD Operations",
         "📈 EDA & Visualizations"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Built with Python • SQL • Streamlit")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — HOME DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home Dashboard":
    st.markdown("## 🥗 Local Food Wastage Management System")
    st.markdown("*Connecting surplus food providers with those in need — reducing waste, fighting hunger.*")
    st.markdown("---")

    # KPI row
    total_providers = run_query("SELECT COUNT(*) AS n FROM providers")["n"][0]
    total_receivers  = run_query("SELECT COUNT(*) AS n FROM receivers")["n"][0]
    total_food       = run_query("SELECT SUM(Quantity) AS n FROM food_listings")["n"][0]
    total_claims     = run_query("SELECT COUNT(*) AS n FROM claims")["n"][0]
    completed        = run_query("SELECT COUNT(*) AS n FROM claims WHERE Status='Completed'")["n"][0]
    cities_count     = run_query("SELECT COUNT(DISTINCT City) AS n FROM providers")["n"][0]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("🏪 Providers",   total_providers)
    c2.metric("🤝 Receivers",   total_receivers)
    c3.metric("🍱 Food Units",  f"{total_food:,}")
    c4.metric("📋 Claims",      total_claims)
    c5.metric("✅ Completed",   completed)
    c6.metric("🏙️ Cities",      cities_count)

    st.markdown("---")

    # Two charts side by side
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">📍 Food Listings by City</div>', unsafe_allow_html=True)
        df_city = run_query("""
            SELECT Location AS City, COUNT(*) AS Listings, SUM(Quantity) AS Quantity
            FROM food_listings GROUP BY Location ORDER BY Listings DESC
        """)
        fig = px.bar(df_city, x="City", y="Listings", color="Quantity",
                     color_continuous_scale="Greens", template="plotly_white")
        fig.update_layout(margin=dict(t=20, b=40), height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">📊 Claim Status Breakdown</div>', unsafe_allow_html=True)
        df_status = run_query("SELECT Status, COUNT(*) AS Count FROM claims GROUP BY Status")
        fig2 = px.pie(df_status, names="Status", values="Count",
                      color_discrete_sequence=["#52b788","#f4a261","#e76f51"],
                      hole=0.4, template="plotly_white")
        fig2.update_layout(margin=dict(t=20, b=20), height=320)
        st.plotly_chart(fig2, use_container_width=True)

    # Recent claims
    st.markdown('<div class="section-header">🕐 Recent 10 Claims</div>', unsafe_allow_html=True)
    df_recent = run_query("""
        SELECT c.Claim_ID, fl.Food_Name, r.Name AS Receiver, c.Status, c.Timestamp
        FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        JOIN receivers r       ON c.Receiver_ID = r.Receiver_ID
        ORDER BY c.Timestamp DESC LIMIT 10
    """)
    st.dataframe(df_recent, use_container_width=True, hide_index=True)

    # About section
    st.markdown("---")
    st.markdown("### 🎯 Project Overview")
    cols = st.columns(3)
    with cols[0]:
        st.info("**Problem**\nRestaurants, households & grocery stores discard surplus food while many face food insecurity.")
    with cols[1]:
        st.success("**Solution**\nA structured platform to list, claim, and track surplus food with real-time SQL-backed data.")
    with cols[2]:
        st.warning("**Impact**\nReduce food waste, enable NGOs/individuals to claim food, and generate actionable analytics.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SQL QUERY EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 SQL Query Explorer":
    st.markdown("## 📊 SQL Query Explorer")
    st.markdown("Browse all **15 analytical queries** — click any query to see its SQL and results.")
    st.markdown("---")

    # Query selector
    query_options = [f"Q{q['id']:02d}. {q['title']}" for q in QUERIES]
    selected_label = st.selectbox("Select a Query", query_options)
    selected_idx = int(selected_label[1:3]) - 1
    q = QUERIES[selected_idx]

    # Display query card
    st.markdown(f"""
    <div class="query-card">
        <b>Query {q['id']} of 15</b> — {q['title']}<br/>
        <span style="color:#555">{q['description']}</span>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 View SQL", expanded=False):
        st.code(q["sql"].strip(), language="sql")

    df = run_query(q["sql"])
    st.markdown(f"**Results: {len(df)} rows**")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Auto chart for numeric results
    numeric_cols = df.select_dtypes("number").columns.tolist()
    text_cols    = df.select_dtypes("object").columns.tolist()
    if len(numeric_cols) >= 1 and len(text_cols) >= 1:
        st.markdown("---")
        st.markdown("**📈 Auto Visualization**")
        fig = px.bar(df.head(15), x=text_cols[0], y=numeric_cols[0],
                     color_discrete_sequence=["#52b788"], template="plotly_white",
                     title=q["title"])
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    # All-queries summary table
    st.markdown("---")
    st.markdown("### 📋 All 15 Queries Summary")
    summary = [{"#": q["id"], "Title": q["title"], "Description": q["description"]} for q in QUERIES]
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — FILTER & SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Filter & Search":
    st.markdown("## 🔍 Filter & Search")
    st.markdown("Filter food listings and find providers/receivers by your criteria.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🍱 Food Listings", "🏪 Providers", "🤝 Receivers"])

    # ── Food Listings tab ──────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Filter Food Listings")
        f1, f2, f3, f4 = st.columns(4)
        cities_fl   = ["All"] + sorted(run_query("SELECT DISTINCT Location FROM food_listings")["Location"].tolist())
        food_types_fl = ["All"] + get_food_types()
        meal_types_fl = ["All"] + get_meal_types()
        prov_types_fl = ["All"] + get_provider_types()

        city_sel     = f1.selectbox("City",          cities_fl,   key="fl_city")
        food_sel     = f2.selectbox("Food Type",     food_types_fl, key="fl_food")
        meal_sel     = f3.selectbox("Meal Type",     meal_types_fl, key="fl_meal")
        prov_sel     = f4.selectbox("Provider Type", prov_types_fl, key="fl_prov")

        query = "SELECT * FROM food_listings WHERE 1=1"
        params = []
        if city_sel != "All":    query += " AND Location=?";      params.append(city_sel)
        if food_sel != "All":    query += " AND Food_Type=?";     params.append(food_sel)
        if meal_sel != "All":    query += " AND Meal_Type=?";     params.append(meal_sel)
        if prov_sel != "All":    query += " AND Provider_Type=?"; params.append(prov_sel)

        df_fl = run_query(query, params)
        st.markdown(f"**{len(df_fl)} listings found**")
        st.dataframe(df_fl, use_container_width=True, hide_index=True)

    # ── Providers tab ──────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Find Providers")
        pc1, pc2 = st.columns(2)
        city_p = pc1.selectbox("City", ["All"] + get_cities(), key="p_city")
        type_p = pc2.selectbox("Type", ["All"] + get_provider_types(), key="p_type")

        q_p = "SELECT * FROM providers WHERE 1=1"
        pp  = []
        if city_p != "All": q_p += " AND City=?"; pp.append(city_p)
        if type_p != "All": q_p += " AND Type=?"; pp.append(type_p)

        df_p = run_query(q_p, pp)
        st.markdown(f"**{len(df_p)} providers found**")
        st.dataframe(df_p, use_container_width=True, hide_index=True)

        if not df_p.empty:
            st.markdown("**📞 Contact Directory**")
            for _, row in df_p.iterrows():
                st.markdown(f"- **{row['Name']}** ({row['Type']}) — {row['City']} | ☎️ `{row['Contact']}`")

    # ── Receivers tab ──────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Find Receivers")
        rc1, rc2 = st.columns(2)
        city_r = rc1.selectbox("City", ["All"] + get_cities(), key="r_city")
        type_r = rc2.selectbox("Type", ["All"] + sorted(run_query("SELECT DISTINCT Type FROM receivers")["Type"].tolist()), key="r_type")

        q_r = "SELECT * FROM receivers WHERE 1=1"
        rp  = []
        if city_r != "All": q_r += " AND City=?"; rp.append(city_r)
        if type_r != "All": q_r += " AND Type=?"; rp.append(type_r)

        df_r = run_query(q_r, rp)
        st.markdown(f"**{len(df_r)} receivers found**")
        st.dataframe(df_r, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CRUD OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ CRUD Operations":
    st.markdown("## ✏️ CRUD Operations")
    st.markdown("Create, Read, Update, and Delete records across all tables.")
    st.markdown("---")

    crud_tab = st.tabs(["➕ Add Records", "✏️ Update Records", "🗑️ Delete Records", "📖 View All Tables"])

    # ── ADD ────────────────────────────────────────────────────────────────────
    with crud_tab[0]:
        st.markdown("### ➕ Add New Record")
        entity = st.selectbox("Select Table", ["Food Listing", "Provider", "Receiver", "Claim"], key="add_entity")

        if entity == "Food Listing":
            with st.form("add_food"):
                c1, c2 = st.columns(2)
                food_name  = c1.text_input("Food Name")
                quantity   = c2.number_input("Quantity", 1, 10000, 50)
                expiry     = c1.date_input("Expiry Date", value=date.today())
                provider_id = c2.number_input("Provider ID", 1, 1000, 1)
                provider_type = c1.selectbox("Provider Type", get_provider_types())
                location   = c2.selectbox("Location (City)", get_cities())
                food_type  = c1.selectbox("Food Type", get_food_types())
                meal_type  = c2.selectbox("Meal Type", get_meal_types())
                if st.form_submit_button("➕ Add Food Listing"):
                    execute_dml("""
                        INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                        VALUES (?,?,?,?,?,?,?,?)
                    """, (food_name, quantity, str(expiry), provider_id, provider_type, location, food_type, meal_type))
                    st.success(f"✅ Food listing '{food_name}' added successfully!")
                    st.cache_resource.clear()

        elif entity == "Provider":
            with st.form("add_provider"):
                c1, c2 = st.columns(2)
                name    = c1.text_input("Provider Name")
                ptype   = c2.selectbox("Type", get_provider_types())
                address = c1.text_input("Address")
                city    = c2.selectbox("City", get_cities())
                contact = c1.text_input("Contact")
                if st.form_submit_button("➕ Add Provider"):
                    execute_dml("INSERT INTO providers (Name, Type, Address, City, Contact) VALUES (?,?,?,?,?)",
                                (name, ptype, address, city, contact))
                    st.success(f"✅ Provider '{name}' added successfully!")

        elif entity == "Receiver":
            with st.form("add_receiver"):
                c1, c2 = st.columns(2)
                name   = c1.text_input("Receiver Name")
                rtype  = c2.selectbox("Type", ["NGO", "Community Center", "Individual", "Orphanage", "Old Age Home", "Shelter"])
                city   = c1.selectbox("City", get_cities())
                contact = c2.text_input("Contact")
                if st.form_submit_button("➕ Add Receiver"):
                    execute_dml("INSERT INTO receivers (Name, Type, City, Contact) VALUES (?,?,?,?)",
                                (name, rtype, city, contact))
                    st.success(f"✅ Receiver '{name}' added successfully!")

        elif entity == "Claim":
            with st.form("add_claim"):
                c1, c2 = st.columns(2)
                food_id    = c1.number_input("Food ID", 1, 10000, 1)
                receiver_id = c2.number_input("Receiver ID", 1, 10000, 1)
                status     = c1.selectbox("Status", ["Pending", "Completed", "Cancelled"])
                timestamp  = c2.text_input("Timestamp", value=str(pd.Timestamp.now())[:19])
                if st.form_submit_button("➕ Add Claim"):
                    execute_dml("INSERT INTO claims (Food_ID, Receiver_ID, Status, Timestamp) VALUES (?,?,?,?)",
                                (food_id, receiver_id, status, timestamp))
                    st.success("✅ Claim added successfully!")

    # ── UPDATE ─────────────────────────────────────────────────────────────────
    with crud_tab[1]:
        st.markdown("### ✏️ Update Record")
        upd_entity = st.selectbox("Select Table", ["Food Listing", "Claim Status"], key="upd_entity")

        if upd_entity == "Food Listing":
            with st.form("upd_food"):
                food_id   = st.number_input("Food ID to Update", 1, 10000, 1)
                new_qty   = st.number_input("New Quantity", 1, 10000, 50)
                new_expiry = st.date_input("New Expiry Date")
                if st.form_submit_button("✏️ Update"):
                    execute_dml("UPDATE food_listings SET Quantity=?, Expiry_Date=? WHERE Food_ID=?",
                                (new_qty, str(new_expiry), food_id))
                    st.success(f"✅ Food ID {food_id} updated!")

        elif upd_entity == "Claim Status":
            with st.form("upd_claim"):
                claim_id   = st.number_input("Claim ID to Update", 1, 10000, 1)
                new_status = st.selectbox("New Status", ["Pending", "Completed", "Cancelled"])
                if st.form_submit_button("✏️ Update Status"):
                    execute_dml("UPDATE claims SET Status=? WHERE Claim_ID=?", (new_status, claim_id))
                    st.success(f"✅ Claim {claim_id} status updated to '{new_status}'!")

    # ── DELETE ─────────────────────────────────────────────────────────────────
    with crud_tab[2]:
        st.markdown("### 🗑️ Delete Record")
        st.warning("⚠️ Deletion is permanent. Proceed with caution.")
        del_entity = st.selectbox("Select Table", ["Food Listing", "Claim"], key="del_entity")

        with st.form("del_form"):
            del_id = st.number_input(f"{del_entity} ID to Delete", 1, 100000, 1)
            confirm = st.checkbox("I confirm this deletion")
            if st.form_submit_button("🗑️ Delete"):
                if confirm:
                    if del_entity == "Food Listing":
                        execute_dml("DELETE FROM food_listings WHERE Food_ID=?", (del_id,))
                    else:
                        execute_dml("DELETE FROM claims WHERE Claim_ID=?", (del_id,))
                    st.success(f"✅ {del_entity} ID {del_id} deleted.")
                else:
                    st.error("Please confirm the deletion first.")

    # ── VIEW ALL ────────────────────────────────────────────────────────────────
    with crud_tab[3]:
        st.markdown("### 📖 View All Tables")
        for tbl in ["providers", "receivers", "food_listings", "claims"]:
            with st.expander(f"Table: **{tbl}**"):
                df_tbl = run_query(f"SELECT * FROM {tbl}")
                st.dataframe(df_tbl, use_container_width=True, hide_index=True)
                st.caption(f"{len(df_tbl)} records")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — EDA & VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 EDA & Visualizations":
    st.markdown("## 📈 Exploratory Data Analysis & Visualizations")
    st.markdown("---")

    # ── Row 1 ──────────────────────────────────────────────────────────────────
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.markdown("**Provider Type Distribution**")
        df = run_query("SELECT Type, COUNT(*) AS Count FROM providers GROUP BY Type")
        fig = px.pie(df, names="Type", values="Count", hole=0.35,
                     color_discrete_sequence=px.colors.sequential.Greens_r,
                     template="plotly_white")
        fig.update_layout(height=320, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        st.markdown("**Receiver Type Distribution**")
        df = run_query("SELECT Type, COUNT(*) AS Count FROM receivers GROUP BY Type")
        fig = px.bar(df, x="Type", y="Count",
                     color="Count", color_continuous_scale="Greens",
                     template="plotly_white")
        fig.update_layout(height=320, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2 ──────────────────────────────────────────────────────────────────
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.markdown("**Food Type vs Meal Type Heatmap**")
        df = run_query("""
            SELECT Food_Type, Meal_Type, COUNT(*) AS Count
            FROM food_listings GROUP BY Food_Type, Meal_Type
        """)
        pivot = df.pivot(index="Food_Type", columns="Meal_Type", values="Count").fillna(0)
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Greens",
                        template="plotly_white")
        fig.update_layout(height=320, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        st.markdown("**Monthly Claims Trend**")
        df = run_query("""
            SELECT substr(Timestamp,1,7) AS Month, COUNT(*) AS Claims
            FROM claims GROUP BY Month ORDER BY Month
        """)
        fig = px.line(df, x="Month", y="Claims", markers=True,
                      color_discrete_sequence=["#52b788"], template="plotly_white")
        fig.update_layout(height=320, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3 ──────────────────────────────────────────────────────────────────
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.markdown("**Top 10 Food Items by Total Quantity**")
        df = run_query("""
            SELECT Food_Name, SUM(Quantity) AS Total_Qty
            FROM food_listings GROUP BY Food_Name
            ORDER BY Total_Qty DESC LIMIT 10
        """)
        fig = px.bar(df, x="Total_Qty", y="Food_Name", orientation="h",
                     color="Total_Qty", color_continuous_scale="Greens",
                     template="plotly_white")
        fig.update_layout(height=380, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with r3c2:
        st.markdown("**Claim Status by City**")
        df = run_query("""
            SELECT fl.Location AS City, c.Status, COUNT(*) AS Count
            FROM claims c JOIN food_listings fl ON c.Food_ID = fl.Food_ID
            GROUP BY City, c.Status
        """)
        fig = px.bar(df, x="City", y="Count", color="Status",
                     color_discrete_map={"Completed":"#52b788","Pending":"#f4a261","Cancelled":"#e76f51"},
                     template="plotly_white", barmode="stack")
        fig.update_layout(height=380, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 4 — Scatter ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Quantity vs Claims per Provider (bubble = total quantity)**")
    df = run_query("""
        SELECT p.Name AS Provider, p.Type, p.City,
               COUNT(c.Claim_ID) AS Claims, SUM(fl.Quantity) AS Total_Qty
        FROM providers p
        JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
        LEFT JOIN claims c    ON fl.Food_ID = c.Food_ID
        GROUP BY p.Provider_ID
        HAVING Claims > 0
    """)
    fig = px.scatter(df, x="Claims", y="Total_Qty", size="Total_Qty",
                     color="Type", hover_name="Provider", hover_data=["City"],
                     color_discrete_sequence=px.colors.qualitative.Safe,
                     template="plotly_white",
                     labels={"Total_Qty": "Total Quantity Donated"})
    fig.update_layout(height=440)
    st.plotly_chart(fig, use_container_width=True)

    # ── Row 5 — Expiry & Wastage Trends ───────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🗓️ Food Wastage Trend Analysis")
    r5c1, r5c2 = st.columns(2)

    with r5c1:
        st.markdown("**Food Expiry Distribution (by Expiry Date)**")
        df_exp = run_query("""
            SELECT Expiry_Date, COUNT(*) AS Items, SUM(Quantity) AS Total_Qty
            FROM food_listings
            GROUP BY Expiry_Date
            ORDER BY Expiry_Date
        """)
        fig = px.bar(df_exp, x="Expiry_Date", y="Total_Qty",
                     color="Items", color_continuous_scale="Reds",
                     template="plotly_white",
                     labels={"Total_Qty": "Quantity at Risk", "Expiry_Date": "Expiry Date"})
        fig.update_layout(height=340, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with r5c2:
        st.markdown("**Wastage Risk by Food Category**")
        df_waste = run_query("""
            SELECT Food_Type, Meal_Type,
                   COUNT(*) AS Listings,
                   SUM(Quantity) AS Total_Qty,
                   ROUND(AVG(Quantity),1) AS Avg_Qty
            FROM food_listings
            GROUP BY Food_Type, Meal_Type
            ORDER BY Total_Qty DESC
        """)
        fig = px.treemap(df_waste, path=["Food_Type", "Meal_Type"],
                         values="Total_Qty",
                         color="Avg_Qty",
                         color_continuous_scale="RdYlGn",
                         template="plotly_white",
                         title="")
        fig.update_layout(height=340, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 6 — Provider contribution vs claims gap (wastage insight) ──────────
    r6c1, r6c2 = st.columns(2)

    with r6c1:
        st.markdown("**Donation vs Claims Gap per City (Wastage Indicator)**")
        df_gap = run_query("""
            SELECT fl.Location AS City,
                   SUM(fl.Quantity)       AS Total_Donated,
                   COUNT(c.Claim_ID)      AS Total_Claims,
                   SUM(fl.Quantity) - COUNT(c.Claim_ID)*10 AS Estimated_Waste
            FROM food_listings fl
            LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
            GROUP BY fl.Location
            ORDER BY Estimated_Waste DESC
        """)
        fig = px.bar(df_gap, x="City", y=["Total_Donated","Total_Claims"],
                     barmode="group",
                     color_discrete_map={"Total_Donated":"#52b788","Total_Claims":"#f4a261"},
                     template="plotly_white",
                     labels={"value":"Count","variable":"Metric"})
        fig.update_layout(height=340, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with r6c2:
        st.markdown("**Receiver Type vs Avg Food Claimed**")
        df_recv = run_query("""
            SELECT r.Type AS Receiver_Type,
                   COUNT(c.Claim_ID) AS Total_Claims,
                   ROUND(AVG(fl.Quantity),1) AS Avg_Quantity
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            JOIN food_listings fl ON c.Food_ID = fl.Food_ID
            GROUP BY r.Type
            ORDER BY Total_Claims DESC
        """)
        fig = px.bar(df_recv, x="Receiver_Type", y="Avg_Quantity",
                     color="Total_Claims", color_continuous_scale="Blues",
                     template="plotly_white",
                     labels={"Avg_Quantity":"Avg Quantity Claimed","Receiver_Type":"Receiver Type"})
        fig.update_layout(height=340, margin=dict(t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── City-wise summary table ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🏙️ City-wise Food Distribution Summary")
    df_city_sum = run_query("""
        SELECT
            fl.Location                         AS City,
            COUNT(DISTINCT fl.Provider_ID)      AS Providers,
            COUNT(DISTINCT fl.Food_ID)          AS Food_Listings,
            SUM(fl.Quantity)                    AS Total_Food_Units,
            COUNT(c.Claim_ID)                   AS Total_Claims,
            SUM(CASE WHEN c.Status='Completed' THEN 1 ELSE 0 END) AS Completed,
            ROUND(SUM(CASE WHEN c.Status='Completed' THEN 1.0 ELSE 0 END)
                  / NULLIF(COUNT(c.Claim_ID),0)*100, 1) AS Success_Rate_Pct
        FROM food_listings fl
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
        GROUP BY fl.Location
        ORDER BY Total_Food_Units DESC
    """)
    st.dataframe(df_city_sum, use_container_width=True, hide_index=True)

    # ── Summary stats ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Key Statistical Summary")
    df_fl = run_query("SELECT Quantity FROM food_listings")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Min Quantity",    int(df_fl["Quantity"].min()))
    col2.metric("Max Quantity",    int(df_fl["Quantity"].max()))
    col3.metric("Mean Quantity",   f"{df_fl['Quantity'].mean():.1f}")
    col4.metric("Median Quantity", int(df_fl["Quantity"].median()))

    # ── Raw data explorer ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔬 Raw Data Explorer")
    eda_tbl = st.selectbox("Select table to explore", ["food_listings","providers","receivers","claims"], key="eda_raw")
    df_raw = run_query(f"SELECT * FROM {eda_tbl}")
    st.markdown(f"**Shape: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns**")
    st.dataframe(df_raw.describe(include="all").T.reset_index().rename(columns={"index":"Column"}),
                 use_container_width=True, hide_index=True)
    st.dataframe(df_raw.head(20), use_container_width=True, hide_index=True)
