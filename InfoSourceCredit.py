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
    user="root",
    password="mariadbPW",
    database="InfoSourceCredit",
    port=3306,
    client_flags=[mysql.connector.ClientFlag.INTERACTIVE]
)

cursor = db.cursor()
cursor.execute("SELECT site_name, evaluation_criteria FROM site_table")
site_data = cursor.fetchall()

for site in site_data:
    site_name = site[0]
    evaluation_criteria = site[1]
    classification = classify_site(site_name, evaluation_criteria)
    cursor.execute("UPDATE site_table SET classification=%s WHERE site_name=%s", (classification, site_name))
    db.commit()
