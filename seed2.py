from app import db, User, Team, Project, Task, UserProject
from faker import Faker
import random

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
team_id=t1.id
role = "Product_Manager"
password = "Barry123!!!"

test_user = User.signup(email, first_name, last_name, team_id, role, password)


# Create other teams
teams = ["Marketing", "Finance", "Supply Chain", "Senior Leadership"]
team_objects = []

for team_name in teams:
    team = Team(name=team_name)
    db.session.add(team)
    team_objects.append(team)

db.session.commit()

# Create 4 users, each on a different team
users = []
for i in range(4):
    user = User(
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        team_id=team_objects[i].id,
        role=f'{team_objects[i].name} Manager',
        password=fake.password(),
    )
    db.session.add(user)
    users.append(user)

db.session.commit()

# Create 2 projects with associated tasks
projects = []
for i in range(2):
    project = Project(
        project_name=fake.company(),
        description=fake.text(),
        # start_date=fake.date_time_this_decade(),
        end_date=fake.date_time_this_decade(),
        user_id=users[0].id,
    )
    db.session.add(project)
    projects.append(project)

db.session.commit()

# Create 5 tasks for each project, 2 of which are meetings
for project in projects:
    for i in range(5):
        task_type = "meeting" if i < 2 else "task"
        task = Task(
            task_name=fake.catch_phrase(),
            description=fake.text(),
            type=task_type,
            status=random.choice(["Not Started", "In Progress", "Complete", "Delayed"]),
            priority=random.choice(["Low", "Moderate", "High"]),
            # start_date=fake.date_time_this_decade(),
            end_date=fake.date_time_this_decade(),
            user_id=test_user.id,
            project_id=project.id,
        )
        db.session.add(task)

db.session.commit()

# Associate users with projects
for user in users:
    for project in projects:
        user_project = UserProject(user_id=user.id, project_id=project.id)
        db.session.add(user_project)

db.session.commit()

print("Database seeded with users, teams, projects, and tasks.")
