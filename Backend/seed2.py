from app import db, User, Department, Project, Task, UserProject
from faker import Faker
import random
from datetime import datetime, timedelta

db.session.rollback()
db.drop_all()
db.create_all()

db.session.commit()

# Initialize Faker to generate random user data
fake = Faker()

# Create test user on Product Department
d1 = Department(name="Product Management")
db.session.add(d1)
db.session.commit()

email = "barry@company.com"
first_name = "Barry"
last_name = "Dunderwerk"
department = "Product Management"
role = "VP of Product"
password = "Barry123!!!"
profile_img = "https://headshots-inc.com/wp-content/uploads/2020/11/Professional-Headshot-Poses-Blog-Post.jpg"

test_user = User.signup(email,
                        first_name,
                        last_name,
                        department,
                        role,
                        password,
                        profile_img
                        )

# Create other teams
departments = ["Marketing", "UX", "Development", "Senior Leadership"]
department_objects = []

for department in departments:
    d = Department(name=department)
    db.session.add(d)
    department_objects.append(d)

db.session.commit()

# Create 4 users, each on a different department
profile_imgs = [
    'https://sharpfocusphoto.com/wp-content/uploads/2020/08/DSC_0275.jpg',
    'https://headshots-inc.com/wp-content/uploads/2023/03/professional-Headshot-Example-2-1.jpg',
    'https://images.squarespace-cdn.com/content/v1/530ce8d1e4b067ea68a9f821/1612484390216-5NVBC0NJJTFP1OPNRU6F/corporate%2Bbusiness%2Bheadshots%2Blos%2Bangeles_Danielle%2BSpires.jpg',
    'https://miro.medium.com/v2/resize:fit:377/0*OD29YviapogfjXGP.jpg'
]

for i in range(4):
    user = User.signup(
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        department_name=departments[i],
        role=f'{department_objects[i].name} Director',
        password=fake.password(),
        profile_img=profile_imgs[i]
    )




# Create 3 users who report into the Test User

roles = ["Product Manager", "Co-ordinator", "Analyst"]
subordinate_imgs = ["https://media.istockphoto.com/id/1394347360/photo/confident-young-black-businesswoman-standing-at-a-window-in-an-office-alone.jpg?s=612x612&w=0&k=20&c=tOFptpFTIaBZ8LjQ1NiPrjKXku9AtERuWHOElfBMBvY=",
                    "https://media.istockphoto.com/id/1279504799/photo/businesswomans-portrait.jpg?s=612x612&w=0&k=20&c=I-54ajKgmxkY8s5-myHZDv_pcSCveaoopf1DH3arv0k=",
                    "https://media.istockphoto.com/id/1016761216/photo/portrait-concept.jpg?s=612x612&w=0&k=20&c=JsGhLiCeBZs7NeUY_3wjDlLfVkgDJcD9UCXeWobe7Ak="
                    ]

subordinates = []

for i in range(3):

    user = User(
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        department_id=d1.id,
        role=roles[i],
        password=fake.password(),
        profile_img=subordinate_imgs[i],
        manager_id=test_user.id
    )

    db.session.add(user)
    subordinates.append(user)
    db.session.commit()


# Create a "Miscellaneous Project"

misc_proj = Project(
    project_name="Miscellaneous",
    description=fake.text(),
    end_date=(datetime.now() + timedelta(days=30)).date(),
    user_id=test_user.id
)

db.session.add(misc_proj)
db.session.commit()


# Create 3 random tasks for each subordinate

for i in range(3):
    task = Task.create_new_task(
        task_name=fake.text(),
        description=fake.text(),
        notes="",
        type="task",
        priority="Medium",
        status=random.choice(["Not Started", "In Progress", "Complete"]),
        end_date=datetime(2023,10,15),
        user_id=test_user.id,
        meeting_user_id=None,
        project_id=misc_proj.id,
        users=subordinates
    )



#  Create an actual project for the test user

project = Project(
    project_name="AI Task Management App",
    description=fake.text(),
    end_date=(datetime.now() + timedelta(days=30)).date(),
    user_id=test_user.id,
)
db.session.add(project)


db.session.commit()

# Create 5 tasks for project

task_objects=[
    {"name":"Project Planning and Requirements Gathering",
     "department":None},
    {"name":"Work with UX/UI to design and build prototype",
     "department":"UX"},
    {"name":"Work with Development team to build back-end and front-end",
     "department":"Development"},
    {"name":"Work with Marketing to build go-to-market plan",
     "department":"Marketing"},
    {"name":"Bring final plan to Senior Leadership",
     "department": "Senior Leadership"}
]

for i in range(5):
    task_type = "task"
    if i < 3:
        # Set 2 tasks to end in September 2023
        end_date = datetime(2023, 9, i + 1).date()
        status = "In Progress"
    else:
        # Set the remaining 3 tasks to end in November and December 2023
        end_date = datetime(2023, 11, 2).date() if i < 4 else datetime(2023, 12, 15).date()
        status=random.choice(["Not Started", "In Progress"])

    department_name = task_objects[i]["department"]
    users = []
    if department_name:
        print("***************",department)
        department = Department.query.filter_by(name=department_name).one()
        other_user = User.query.filter_by(department=department).first()
        users.append(other_user)

    task = Task.create_new_task(
        task_name=task_objects[i]["name"],
        description="",
        notes="",
        type=task_type,
        status=status,
        priority=random.choice(["Low", "Medium", "High"]),
        end_date=end_date,
        user_id=test_user.id,
        project_id=project.id,
        meeting_user_id=None,
        users=users
    )


# # Associate users with projects
# for project in projects:
#     user_project = UserProject(user_id=test_user.id, project_id=project.id)
#     db.session.add(user_project)

# db.session.commit()

# # Create 3 projects for the test user
# projects = []
# for i in range(3):
#     project = Project(
#         project_name=fake.company(),
#         description=fake.text(),
#         end_date=(datetime.now() + timedelta(days=30)).date(),
#         user_id=test_user.id,
#     )
#     db.session.add(project)
#     projects.append(project)

# db.session.commit()

# # Create 5 tasks for each project
# for project in projects:
#     for i in range(5):
#         task_type = "task"
#         if i < 2:
#             # Set 5 tasks to end in September 2023
#             end_date = datetime(2023, 9, i + 1).date()
#             status = "In Progress"
#         else:
#             # Set the remaining 10 tasks to end in November and December 2023
#             end_date = datetime(2023, 11, 2).date() if i < 4 else datetime(2023, 12, 15).date()
#             status=random.choice(["Not Started", "In Progress"])


#         task = Task(
#             task_name=fake.catch_phrase(),
#             description=fake.text(),
#             type=task_type,
#             status=status,
#             priority=random.choice(["Low", "Medium", "High"]),
#             end_date=end_date,
#             user_id=test_user.id,
#             project_id=project.id,
#         )
#         db.session.add(task)

# db.session.commit()

# # Associate users with projects
# for project in projects:
#     user_project = UserProject(user_id=test_user.id, project_id=project.id)
#     db.session.add(user_project)

# db.session.commit()

print("Database seeded with users, departments, projects, and tasks.")
