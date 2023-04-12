import openai
import mysql.connector

openai.api_key = "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"

def generate_response(prompt):
    completions = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    message = completions.choices[0].text.strip()
    return message

def classify_site(site_name, evaluation_criteria):
    prompt = f"Classify {site_name} according to {evaluation_criteria}"
    response = generate_response(prompt)
    return response

db = mysql.connector.connect(
    host="localhost",
    user="username",
    password="password",
    database="database_name"
)

cursor = db.cursor()
cursor.execute("SELECT id, site_name, evaluation_criteria FROM site_table")
site_data = cursor.fetchall()

for site in site_data:
    site_id = site[0]
    site_name = site[1]
    evaluation_criteria = site[2]
    classification = classify_site(site_name, evaluation_criteria)
    cursor.execute("UPDATE site_table SET classification=%s WHERE id=%s", (classification, site_id))
    db.commit()
