from app import db, User, Team, Project, Task, UserProject
from faker import Faker
import random
from datetime import datetime, timedelta

db.session.rollback()
db.drop_all()
db.create_all()

db.session.commit()

# Initialize Faker to generate random user data
fake = Faker()

# Create test user on Product Team
t1 = Team(name="Product_management")
db.session.add(t1)
db.session.commit()

email = "barry@company.com"
first_name = "Barry"
last_name = "Dunderwerk"
team_name = "Product_management"
role = "Product_Manager"
password = "Barry123!!!"
profile_img = "https://headshots-inc.com/wp-content/uploads/2020/11/Professional-Headshot-Poses-Blog-Post.jpg"

test_user = User.signup(email,
                        first_name,
                        last_name,
                        team_name,
                        role,
                        password,
                        profile_img
                        )

# Create other teams
teams = ["Marketing", "Finance", "Supply Chain", "Senior Leadership"]
team_objects = []

for team_name in teams:
    team = Team(name=team_name)
    db.session.add(team)
    team_objects.append(team)

db.session.commit()

# Create 4 users, each on a different team
profile_imgs = [
    'https://sharpfocusphoto.com/wp-content/uploads/2020/08/DSC_0275.jpg',
    'https://headshots-inc.com/wp-content/uploads/2023/03/professional-Headshot-Example-2-1.jpg',
    'https://images.squarespace-cdn.com/content/v1/530ce8d1e4b067ea68a9f821/1612484390216-5NVBC0NJJTFP1OPNRU6F/corporate%2Bbusiness%2Bheadshots%2Blos%2Bangeles_Danielle%2BSpires.jpg',
    'https://miro.medium.com/v2/resize:fit:377/0*OD29YviapogfjXGP.jpg'
]

users = []
for i in range(4):
    user = User(
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        team_id=team_objects[i].id,
        role=f'{team_objects[i].name} Manager',
        password=fake.password(),
        profile_img=profile_imgs[i - 1]
    )
    db.session.add(user)
    users.append(user)

db.session.commit()

# Create 3 projects for the test user
projects = []
for i in range(3):
    project = Project(
        project_name=fake.company(),
        description=fake.text(),
        end_date=(datetime.now() + timedelta(days=30)).date(),
        user_id=test_user.id,
    )
    db.session.add(project)
    projects.append(project)

db.session.commit()

# Create 5 tasks for each project
for project in projects:
    for i in range(5):
        task_type = "task"
        if i < 2:
            # Set 5 tasks to end in September 2023
            end_date = datetime(2023, 9, i + 1).date()
            status = "In Progress"
        else:
            # Set the remaining 10 tasks to end in November and December 2023
            end_date = datetime(2023, 11, 2).date() if i < 4 else datetime(2023, 12, 15).date()
            status=random.choice(["Not Started", "In Progress"])


        task = Task(
            task_name=fake.catch_phrase(),
            description=fake.text(),
            type=task_type,
            status=status,
            priority=random.choice(["Low", "Medium", "High"]),
            end_date=end_date,
            user_id=test_user.id,
            project_id=project.id,
        )
        db.session.add(task)

db.session.commit()

# Associate users with projects
for project in projects:
    user_project = UserProject(user_id=test_user.id, project_id=project.id)
    db.session.add(user_project)

db.session.commit()

print("Database seeded with users, teams, projects, and tasks.")
