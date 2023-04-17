import mysql.connector
import openai_secret_manager
import openai
import re
from datetime import datetime
import sys
sys.setrecursionlimit(10**6)


# Set up MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mariadbPW",
    database="infosourcecredit",
    port=3306,
    client_flags=[mysql.connector.ClientFlag.INTERACTIVE]
)
cursor = db.cursor()

# Set up OpenAI API credentials
#secrets = openai_secret_manager.get_secret("openai")
#openai.api_key = secrets["api_key"]
with open('openai_api_key.txt', 'r') as f:
    openai.api_key = f.read().strip()


# Fetch list of websites from site_table
cursor.execute("SELECT site_address, authority, accuracy, objectivity, currency, coverage, consistency FROM site_table")
websites = cursor.fetchall()

# Loop through each website and evaluate its reliability using OpenAI GPT
for website in websites:
    address = website[0]
    current_scores = list(website[1:])
    
    # Escape special characters in the website address
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Assess the reliability of {address} based on the following criteria: authority, accuracy, objectivity, currency, coverage, consistency.",
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5
        )
        updated_scores = response.choices[0].text.split(',')
        print(updated_scores)
        # Update the corresponding reliability criteria in the site_table table
        if len(updated_scores) >= 6:
            sql = "UPDATE site_table SET authority=%s, accuracy=%s, objectivity=%s, currency=%s, coverage=%s, consistency=%s, score_change_date=%s WHERE site_address = %s"
            
            cursor.execute(sql, tuple(updated_scores + [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), address]))
            db.commit()
            
            # Insert site issue data into site_issues table
            for i in range(len(current_scores)):
                if current_scores[i] != updated_scores[i]:
                    issue_item = ["authority", "accuracy", "objectivity", "currency", "coverage", "consistency"][i]
                    old_score = current_scores[i].strip()
                    new_score = updated_scores[i].strip()
                    reason = "Credit score change"
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sql = "INSERT INTO site_issues (site_address, issue_item, old_score, new_score, reason, date) VALUES (%s, %s, %s, %s, %s, %s)"
                    # print(address+"\n"+issue_item +"\n"+"")
                    cursor.execute(sql, (address, issue_item, old_score, new_score, reason, date))
                    db.commit()
        else:
            print(f"Error: {address} - updated_scores list length is less than 6")
    except mysql.connector.errors.ProgrammingError as e:
        print(f"Error: {e}")

cursor.close()
db.close()
