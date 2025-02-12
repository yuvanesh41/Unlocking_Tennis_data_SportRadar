import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# Establish the database connection

connection = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="vijay45",
    database="tennis_data"
)
cursor = connection.cursor()

# Sidebar - Navigation
st.sidebar.title("Dashboard")
menu = st.sidebar.selectbox(
    "Go to:",
    ["Homepage Dashboard", "Search Competitors", "Competitor Details", "Country Analysis", "Leaderboards"]
)

# Homepage Dashboard
if menu == "Homepage Dashboard":
    st.write("# SPORTS RADAR API")
    st.subheader('*Summary about the title:*')
    st.markdown("""
    SportRadar's API provides comprehensive tennis data, including match stats, player performance, and tournament insights, enabling advanced analytics and predictive modeling. It empowers users to track trends, optimize strategies, and gain actionable insights for sports analysis. :trophy: :tennis:
    """)

    # Metrics
    cursor.execute("SELECT COUNT(*) FROM competitors_table")
    total_competitors = cursor.fetchone()[0]
    st.metric("TOTAL COMPETITORS", total_competitors)

    cursor.execute("SELECT COUNT(DISTINCT country) FROM competitors_table")
    countries_represented = cursor.fetchone()[0]
    st.metric("COUNTRY REPRESENTED", countries_represented)

    cursor.execute("SELECT MAX(points) FROM competitor_rankings_table")
    highest_points = cursor.fetchone()[0]
    st.metric("HIGHEST POINTS", highest_points)

# Search Competitors
elif menu == "Search Competitors":
    st.header("Search Competitors")

    # Search filters
    competitor_name = st.text_input("SEARCH COMPETITOR BY NAME")
    rank_range = st.slider("FILTER BY RANK RANGE", 1, 500, (1, 50))
    points_threshold = st.number_input("POINTS THRESHOLD", min_value=0, step=1)

    # Query
    query1 = f"""
    SELECT c.competitor_id, c.name, c.country, r.rank, r.points
    FROM competitors_table c
    JOIN competitor_rankings_table r ON c.competitor_id = r.competitor_id
    WHERE c.name LIKE '%{competitor_name}%'
    AND r.rank BETWEEN {rank_range[0]} AND {rank_range[1]}
    AND r.points >= {points_threshold}
    ORDER BY r.points DESC
    """
    cursor.execute(query1)
    competitors = cursor.fetchall()

    # Display results
    if competitors:
        df_competitors = pd.DataFrame(
            competitors, 
            columns=["Competitor ID", "Name", "Country", "Rank", "Points"]
        )
        st.dataframe(df_competitors)
    else:
        st.write("No competitors found.")

# Competitor Details
elif menu == "Competitor Details":
    st.header("Competitor Details Viewer")

    # Dropdown to select a competitor
    cursor.execute("SELECT name FROM competitors_table")
    competitors_list = [row[0] for row in cursor.fetchall()]
    selected_competitor = st.selectbox("Select a competitor:", competitors_list)

    # Query competitor details
    if selected_competitor:
        query2 = f"""
        SELECT r.rank,movement, r.competitions_played, c.country
        FROM competitors_table c
        JOIN competitor_rankings_table r ON c.competitor_id = r.competitor_id
        WHERE c.name = '{selected_competitor}'
        """
        cursor.execute(query2)
        details = cursor.fetchone()

        if details:
            rank, movement, competitions_played, country = details
            st.subheader(f"Details for {selected_competitor}")
            st.write(f"**Rank:** {rank}")
            st.write(f"**Movement:** {movement}")
            st.write(f"**Competitions Played:** {competitions_played}")
            st.write(f"**Country:** {country}")
        else:
            st.error("No details found for the selected competitor.")

# Country Analysis
elif menu == "Country Analysis":
    st.header("Country-Wise Analysis")

    # Query to list countries with total competitors and average points
    query3 = """
    SELECT c.country, COUNT(c.competitor_id) AS total_competitors, AVG(r.points) AS avg_points
    FROM competitors_table c
    JOIN competitor_rankings_table r ON c.competitor_id = r.competitor_id
    GROUP BY c.country
    ORDER BY total_competitors DESC
    """
    cursor.execute(query3)
    country_data = cursor.fetchall()

    # Display results
    df_country = pd.DataFrame(country_data, columns=["Country", "Total Competitors", "Average Points"])
    st.dataframe(df_country)

    # Visualization
    fig = px.bar(df_country, x="Country", y="Total Competitors", color="Average Points", title="Country-Wise Analysis")
    st.plotly_chart(fig)

# Leaderboards
elif menu == "Leaderboards":
    st.header("Leaderboards")

    # Top-ranked competitors
    query4 = """
    SELECT c.name, c.country, r.rank
    FROM competitors_table c
    JOIN competitor_rankings_table r ON c.competitor_id = r.competitor_id
    ORDER BY r.rank ASC
    LIMIT 10
    """
    cursor.execute(query4)
    top_ranked = cursor.fetchall()
    df_top_ranked = pd.DataFrame(top_ranked, columns=["Name", "Country", "Rank"])
    st.subheader("Top-Ranked Competitors")
    st.dataframe(df_top_ranked)

    # Competitors with the highest points
    query5 = """
    SELECT c.name, c.country, r.points
    FROM competitors_table c
    JOIN competitor_rankings_table r ON c.competitor_id = r.competitor_id
    ORDER BY r.points DESC
    LIMIT 10
    """
    cursor.execute(query5)
    top_points = cursor.fetchall()
    df_top_points = pd.DataFrame(top_points, columns=["Name", "Country", "Points"])
    st.subheader("Competitors with the Highest Points")
    st.dataframe(df_top_points)
