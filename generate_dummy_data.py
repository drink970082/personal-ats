import sqlite3
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
from database.manager import DatabaseManager

# Initialize database
db = DatabaseManager()


def generate_dummy_data(num_records=100):
    fake = Faker()
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()

    categories = ["SWE/SDE", "MLE", "Quant Analyst", "Quant Dev", "DS", "DA", "Others"]

    # Status progression paths
    status_paths = [
        (["Applied"], 0.40),
        (["Applied", "Online Assessment"], 0.05),
        (["Applied", "Online Assessment", "Rejected"], 0.10),
        (["Applied", "1st round"], 0.07),
        (["Applied", "Online Assessment"], 0.07),
        (["Applied", "Online Assessment", "1st round", "2nd round", "Offer"], 0.04),
        (["Applied", "Online Assessment", "1st round", "2nd round", "Offer", "Declined"], 0.01),
        # New: longer interview paths
        (["Applied", "Online Assessment", "1st round", "2nd round", "3rd round", "Rejected"], 0.05),
        (["Applied", "Online Assessment", "1st round", "2nd round", "3rd round", "4th round", "Rejected"], 0.04),
        (
            [
                "Applied",
                "Online Assessment",
                "1st round",
                "2nd round",
                "3rd round",
                "4th round",
                "5th round",
                "Rejected",
            ],
            0.03,
        ),
        (
            [
                "Applied",
                "Online Assessment",
                "1st round",
                "2nd round",
                "3rd round",
                "4th round",
                "5th round",
                "6th round",
                "Offer",
            ],
            0.02,
        ),
        (
            [
                "Applied",
                "Online Assessment",
                "1st round",
                "2nd round",
                "3rd round",
                "4th round",
                "5th round",
                "6th round",
                "Offer",
                "Declined",
            ],
            0.01,
        ),
    ]

    paths, weights = zip(*status_paths)

    for _ in range(num_records):
        company = fake.company()
        title = fake.job()
        url = f"https://www.{company.lower().replace(' ', '').split(',')[0]}.com/careers"
        date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        category = random.choice(categories)
        path = random.choices(paths, weights=weights, k=1)[0]
        notes = fake.sentence() if random.random() > 0.5 else ""
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_status = path[-1]

        # Insert application with final status
        cursor.execute(
            """
            INSERT INTO applications (company_name, job_title, application_url, date_applied, category, status, notes, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (company, title, url, date, category, final_status, notes, last_updated),
        )
        app_id = cursor.lastrowid

        # Insert status history
        status_time = datetime.now() - timedelta(days=len(path))
        for s in path:
            status_time = status_time + timedelta(days=1)
            cursor.execute(
                """
                INSERT INTO status_history (application_id, status, timestamp)
                VALUES (?, ?, ?)
            """,
                (app_id, s, status_time.strftime("%Y-%m-%d %H:%M:%S")),
            )

    conn.commit()
    conn.close()
    print(f"Successfully generated {num_records} dummy records with status history.")


if __name__ == "__main__":
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications;")
    cursor.execute("DELETE FROM status_history;")
    conn.commit()
    conn.close()
    generate_dummy_data()
