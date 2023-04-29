import mysql.connector
import openai
import asyncio
from datetime import datetime
import aiohttp


def update_site_table(address, updated_scores):
    sql = "UPDATE site_table SET authority=%s, accuracy=%s, objectivity=%s, currency=%s, coverage=%s, consistency=%s, score_change_date=%s WHERE site_address = %s"
    cursor.execute(sql, tuple(updated_scores + [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), address]))
    db.commit()


def insert_site_issues(address, current_scores, updated_scores):
    for i in range(len(current_scores)):
        if current_scores[i] != updated_scores[i]:
            issue_item = ["authority", "accuracy", "objectivity", "currency", "coverage", "consistency"][i]
            old_score = current_scores[i]
            new_score = updated_scores[i]
            reason = "Credit score change"
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO site_issues (site_address, issue_item, old_score, new_score, reason, date) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (address, issue_item, old_score, new_score, reason, date))
            db.commit()




async def evaluate_website_reliability(website_address, scores_sum):
    try:
        headers = {"Authorization": f"Bearer {openai.api_key}"}
        data = {
            #"engine": "text-davinci-003",
            "prompt": f"Assess the reliability of {website_address} based on the following criteria: authority, accuracy, objectivity, currency, coverage, consistency. Score each criterion from 1.0 (lowest) to 5.0 (highest). Your Answering format should be 'score of authority,score of accuracy,score of objectivity,score of currency,score of coverage,score of consistency'",
            "max_tokens": 64,
            "n": 1,
            "stop": None,
            "temperature": 0.1
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/engines/text-davinci-003/completions", headers=headers, json=data) as response:
                result = await response.json()
                updated_scores = result['choices'][0]['text'].split(',')
                updated_scores[0] = updated_scores[0].replace("\n\n", "")
                scores_sum = [sum(x) for x in zip(scores_sum, list(map(float, updated_scores)))]
                return scores_sum
    except Exception as e:
        print(f"Error: {website_address} - {e}")
        return None



async def main():
    cursor.execute("SELECT site_address, authority, accuracy, objectivity, currency, coverage, consistency FROM site_table")
    websites = cursor.fetchall()

    for website in websites:
        address = website[0]
        current_scores = list(website[1:])
        scores_sum = [0] * 6
        tasks = []
        for i in range(1, 11):
            task = asyncio.ensure_future(evaluate_website_reliability(address, scores_sum))
            tasks.append(task)
        scores_list_results = await asyncio.gather(*tasks)

        for s in scores_list_results:
            if s is not None:
                scores_sum = [sum(x) for x in zip(scores_sum, s)]

        updated_scores = [x / 10 for x in scores_sum]


        if len(updated_scores) >= 6:
            update_site_table(address, updated_scores)
            insert_site_issues(address, current_scores, updated_scores)
        else:
            print(f"Error: {address} - updated_scores list length is less than 6")

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mariadbPW",
    database="infosourcecredit",
    port=3306,
    client_flags=[mysql.connector.ClientFlag.INTERACTIVE]
)

cursor = db.cursor()

with open('openai_api_key.txt', 'r') as f:
    openai.api_key = f.read().strip()

asyncio.run(main())
cursor.close()
db.close()
print("Database connection closed")
