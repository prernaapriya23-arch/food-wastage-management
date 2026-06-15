"""
sql_queries.py
All 15 SQL queries with titles and descriptions.
"""

QUERIES = [
    {
        "id": 1,
        "title": "Providers & Receivers per City",
        "description": "How many food providers and receivers are there in each city?",
        "sql": """
            SELECT 
                p.City,
                COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
                COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
            FROM providers p
            LEFT JOIN receivers r ON p.City = r.City
            GROUP BY p.City
            ORDER BY Total_Providers DESC
        """
    },
    {
        "id": 2,
        "title": "Most Contributing Provider Types",
        "description": "Which type of food provider (restaurant, grocery store, etc.) contributes the most food?",
        "sql": """
            SELECT 
                Provider_Type,
                COUNT(Food_ID)      AS Total_Listings,
                SUM(Quantity)       AS Total_Quantity
            FROM food_listings
            GROUP BY Provider_Type
            ORDER BY Total_Quantity DESC
        """
    },
    {
        "id": 3,
        "title": "Provider Contact Information by City",
        "description": "What is the contact information of food providers in each city?",
        "sql": """
            SELECT 
                City,
                Name,
                Type,
                Address,
                Contact
            FROM providers
            ORDER BY City, Name
        """
    },
    {
        "id": 4,
        "title": "Top Receivers by Food Claims",
        "description": "Which receivers have claimed the most food?",
        "sql": """
            SELECT 
                r.Name              AS Receiver_Name,
                r.Type              AS Receiver_Type,
                r.City,
                COUNT(c.Claim_ID)   AS Total_Claims
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Receiver_ID
            ORDER BY Total_Claims DESC
            LIMIT 10
        """
    },
    {
        "id": 5,
        "title": "Total Food Quantity Available",
        "description": "What is the total quantity of food available from all providers?",
        "sql": """
            SELECT 
                SUM(Quantity)   AS Total_Food_Available,
                COUNT(Food_ID)  AS Total_Listings,
                AVG(Quantity)   AS Avg_Quantity_Per_Listing
            FROM food_listings
        """
    },
    {
        "id": 6,
        "title": "Cities with Most Food Listings",
        "description": "Which city has the highest number of food listings?",
        "sql": """
            SELECT 
                Location        AS City,
                COUNT(Food_ID)  AS Total_Listings,
                SUM(Quantity)   AS Total_Quantity
            FROM food_listings
            GROUP BY Location
            ORDER BY Total_Listings DESC
        """
    },
    {
        "id": 7,
        "title": "Most Common Food Types",
        "description": "What are the most commonly available food types (Vegetarian, Non-Veg, Vegan)?",
        "sql": """
            SELECT 
                Food_Type,
                COUNT(Food_ID)  AS Total_Listings,
                SUM(Quantity)   AS Total_Quantity
            FROM food_listings
            GROUP BY Food_Type
            ORDER BY Total_Listings DESC
        """
    },
    {
        "id": 8,
        "title": "Claims per Food Item",
        "description": "How many food claims have been made for each food item?",
        "sql": """
            SELECT 
                fl.Food_Name,
                fl.Food_Type,
                fl.Meal_Type,
                COUNT(c.Claim_ID) AS Total_Claims
            FROM food_listings fl
            LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
            GROUP BY fl.Food_ID
            ORDER BY Total_Claims DESC
            LIMIT 15
        """
    },
    {
        "id": 9,
        "title": "Providers with Most Successful Claims",
        "description": "Which provider has had the highest number of successful (Completed) food claims?",
        "sql": """
            SELECT 
                p.Name              AS Provider_Name,
                p.Type              AS Provider_Type,
                p.City,
                COUNT(c.Claim_ID)   AS Successful_Claims
            FROM providers p
            JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
            JOIN claims c         ON fl.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID
            ORDER BY Successful_Claims DESC
            LIMIT 10
        """
    },
    {
        "id": 10,
        "title": "Claim Status Distribution",
        "description": "What percentage of food claims are Completed vs Pending vs Cancelled?",
        "sql": """
            SELECT 
                Status,
                COUNT(Claim_ID)                                         AS Count,
                ROUND(COUNT(Claim_ID) * 100.0 / SUM(COUNT(Claim_ID)) OVER(), 2) AS Percentage
            FROM claims
            GROUP BY Status
        """
    },
    {
        "id": 11,
        "title": "Average Quantity Claimed per Receiver",
        "description": "What is the average quantity of food claimed per receiver?",
        "sql": """
            SELECT 
                r.Name                  AS Receiver_Name,
                r.Type,
                r.City,
                COUNT(c.Claim_ID)       AS Total_Claims,
                ROUND(AVG(fl.Quantity), 2) AS Avg_Quantity_Per_Claim
            FROM receivers r
            JOIN claims c        ON r.Receiver_ID = c.Receiver_ID
            JOIN food_listings fl ON c.Food_ID = fl.Food_ID
            GROUP BY r.Receiver_ID
            ORDER BY Avg_Quantity_Per_Claim DESC
            LIMIT 10
        """
    },
    {
        "id": 12,
        "title": "Most Claimed Meal Types",
        "description": "Which meal type (Breakfast, Lunch, Dinner, Snacks) is claimed the most?",
        "sql": """
            SELECT 
                fl.Meal_Type,
                COUNT(c.Claim_ID)   AS Total_Claims,
                SUM(fl.Quantity)    AS Total_Quantity
            FROM food_listings fl
            JOIN claims c ON fl.Food_ID = c.Food_ID
            GROUP BY fl.Meal_Type
            ORDER BY Total_Claims DESC
        """
    },
    {
        "id": 13,
        "title": "Total Quantity Donated by Each Provider",
        "description": "What is the total quantity of food donated by each provider?",
        "sql": """
            SELECT 
                p.Name              AS Provider_Name,
                p.Type,
                p.City,
                SUM(fl.Quantity)    AS Total_Quantity_Donated,
                COUNT(fl.Food_ID)   AS Total_Listings
            FROM providers p
            JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
            GROUP BY p.Provider_ID
            ORDER BY Total_Quantity_Donated DESC
            LIMIT 15
        """
    },
    {
        "id": 14,
        "title": "Expiring Food (Next 7 Days)",
        "description": "Which food items are expiring soon (within the next 7 days of dataset start)?",
        "sql": """
            SELECT 
                Food_Name,
                Quantity,
                Expiry_Date,
                Location,
                Food_Type,
                Meal_Type
            FROM food_listings
            WHERE date(Expiry_Date) <= date('2024-01-08')
            ORDER BY Expiry_Date ASC
            LIMIT 20
        """
    },
    {
        "id": 15,
        "title": "City-wise Claim Success Rate",
        "description": "What is the claim success rate (Completed claims) for each city?",
        "sql": """
            SELECT 
                fl.Location AS City,
                COUNT(c.Claim_ID)                                            AS Total_Claims,
                SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)     AS Completed,
                SUM(CASE WHEN c.Status = 'Pending'   THEN 1 ELSE 0 END)     AS Pending,
                SUM(CASE WHEN c.Status = 'Cancelled' THEN 1 ELSE 0 END)     AS Cancelled,
                ROUND(
                    SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0
                    / COUNT(c.Claim_ID), 2
                ) AS Success_Rate_Pct
            FROM food_listings fl
            JOIN claims c ON fl.Food_ID = c.Food_ID
            GROUP BY fl.Location
            ORDER BY Success_Rate_Pct DESC
        """
    },
]
