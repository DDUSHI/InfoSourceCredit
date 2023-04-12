import mysql.connector
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to the database
db = mysql.connector.connect(
    host="localhost",
    user="username",
    password="password",
    database="database_name"
)

# Fetch the site list and evaluation criteria from the database
cursor = db.cursor()
cursor.execute("SELECT site_name, evaluation_criteria FROM site_table")
site_list = cursor.fetchall()

# Define the ChatGPT API function
def classify_site(site_name, evaluation_criteria):
    prompt = f"Classify {site_name} according to {evaluation_criteria}"
    response = generate_response(prompt)
    return response

# Classify the sites and store the results in a new table
for site in site_list:
    site_name = site[0]
    evaluation_criteria = site[1]
    classification = classify_site(site_name, evaluation_criteria)
    cursor.execute("INSERT INTO classification_table (site_name, evaluation_criteria, classification) VALUES (%s, %s, %s)", (site_name, evaluation_criteria, classification))
    db.commit()
