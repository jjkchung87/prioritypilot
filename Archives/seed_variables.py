from datetime import datetime
import random

# List of 50 users

users_info = []

for i in range(1, 50):
    username = f"user_{i}"
    first_name = random.choice(["John", "Jane", "Michael", "Emily", "David", "Emma", "William", "Olivia", "James", "Sophia"])
    last_name = random.choice(["Smith", "Johnson", "Brown", "Miller", "Davis", "Garcia", "Martinez", "Jones", "Lee", "Gonzalez"])
    email = f"{username}@example.com"
    password = f"password{i}"

    fake_account = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }

    users_info.append(fake_account)




# List of 7 leagues
leagues_info = [
    {
        "league_name": "Public Drafted League",
        "privacy": "public",
        "start_date": datetime(2023, 7, 25),
        "end_date": datetime(2023, 8, 15),
        "max_teams": 5,
        "golfer_count": 10,
        "draft_completed": True,
        "league_manager_username": "user_1",
    },
    {
        "league_name": "Private Undrafted League",
        "privacy": "private",
        "start_date": datetime(2023, 8, 5),
        "end_date": datetime(2023, 8, 15),
        "max_teams": 5,
        "golfer_count": 10,
        "draft_completed": False,
        "league_manager_username": "user_1",
    },
    # Add more leagues here up to 7
    # ...
    {
        "league_name": "Sample League",
        "privacy": "public",
        "start_date": datetime(2023, 7, 1),
        "end_date": datetime(2023, 7, 31),
        "max_teams": 5,
        "golfer_count": 15,
        "draft_completed": True,
        "league_manager_username": "user_2",
    },
    # Continue adding leagues up to 7
    # ...
]

# List of 35 teams
teams_info = [
    {
        "team_name": "The Chungs",
        "user_username": "user_1",
        "league_name": "Public Drafted League",
    },
    {
        "team_name": "The Office",
        "user_username": "user_2",
        "league_name": "Private Undrafted League",
    },
    # Add more teams here up to 35
    # ...
    {
        "team_name": "Team A",
        "user_username": "user_3",
        "league_name": "Sample League",
    },
    # Continue adding teams up to 35
    # ...
]

