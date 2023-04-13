import openai
import mysql.connector

# Set up OpenAI API key
openai.api_key = ""

# Connect to MySQL/MariaDB
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="asdf",
    database="InfoSourceCredit",
    port=3306,
    client_flags=[mysql.connector.ClientFlag.INTERACTIVE]
)

# Create a cursor object to execute SQL queries
cursor = db.cursor()

# Retrieve the list of websites from the site_table table
cursor.execute("SELECT site_address FROM site_table")
websites = cursor.fetchall()

# Loop through each website and evaluate its reliability using OpenAI GPT
for website in websites:
    address = website[0]
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Assess the reliability of {address} based on the following criteria: authority, accuracy, objectivity, currency, coverage, consistency.",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5
    )
    reliability_scores = response.choices[0].text.split(',')
    
    # Update the corresponding reliability criteria in the site_table table
    if len(reliability_scores) >= 6:
        address_escaped = mysql.connector.escape(address)
        sql = f"UPDATE site_table SET authority={reliability_scores[0]}, accuracy={reliability_scores[1]}, objectivity={reliability_scores[2]}, currency={reliability_scores[3]}, coverage={reliability_scores[4]}, consistency={reliability_scores[5]} WHERE site_address='{address_escaped}'"
        cursor.execute(sql)
        db.commit()
    else:
        print(f"Error: {address} - reliability_scores list length is less than 6")




# Close the database connection
db.close()
