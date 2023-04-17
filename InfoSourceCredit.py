import mysql.connector
import openai_secret_manager
import openai
import re

# Set up MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mariadbPW",
    database="InfoSourceCredit",
    port=3306,
    client_flags=[mysql.connector.ClientFlag.INTERACTIVE]
)
cursor = db.cursor()


# Set up OpenAI API credentials

with open('openai_api_key.txt', 'r') as f:
    openai.api_key = f.read().strip()


# Fetch list of websites from site_table
cursor.execute("SELECT site_address FROM site_table")
websites = cursor.fetchall()

# Loop through each website and evaluate its reliability using OpenAI GPT
for website in websites:
    address = website[0]

    # Escape special characters in the website address
    try:
        cursor.execute("SELECT * FROM site_table WHERE site_address = %s", (address,))
        results = cursor.fetchall()
        if len(results) == 0:
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"Assess the reliability of {address} based on the following criteria: authority, accuracy, objectivity, currency, coverage, consistency.",
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5
            )
            reliability_scores = [score.strip() for score in response.choices[0].text.split(',')]

            # Update the corresponding reliability criteria in the site_table table
            if len(reliability_scores) >= 6:
                sql = "UPDATE site_table SET authority=%s, accuracy=%s, objectivity=%s, currency=%s, coverage=%s, consistency=%s WHERE site_address = %s"
                cursor.execute(sql, tuple(reliability_scores + [address]))
                db.commit()
            else:
                print(f"Error: {address} - reliability_scores list length is less than 6")
                
        else:
            print(f"{address} already exists in the site_table")
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"Update the reliability scores for {address} based on the following criteria: authority, accuracy, objectivity, currency, coverage, consistency.",
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5
            )
            updated_scores = response.choices[0].text.split(',')
            print(response.choices[0].text.split(','))
            print("\n")
            # Update the corresponding reliability criteria in the site_table table
            if len(updated_scores) >= 6:
                sql = "UPDATE site_table SET authority=%s, accuracy=%s, objectivity=%s, currency=%s, coverage=%s, consistency=%s WHERE site_address = %s"
                cursor.execute(sql, tuple(updated_scores + [address]))
                db.commit()
            else:
                print(f"Error: {address} - updated_scores list length is less than 6")

    except mysql.connector.errors.ProgrammingError as e:
        print(f"Error: {e}")

cursor.close()
db.close()
