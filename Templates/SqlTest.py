import psycopg2

db = psycopg2.connect(
    host="62.109.4.22",
    database="kuchizuchat",
    user="kuchizu",
    port="5432",
    password="Rp858cdf8wZB"
)
cursor = db.cursor()

cursor.execute(
    'Select send_date from private_messages where (from_user_id = %s and to_user_id = %s) or (from_user_id = %s and to_user_id = %s) order by message_id ASC limit 1',
    (1, 2, 2, 1)
)
print(cursor.fetchall())
