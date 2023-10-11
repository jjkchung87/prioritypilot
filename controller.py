import os
import openai
import json
from datetime import datetime
from models import Conversation, Project, db, Task, User, Team


# Load your API key from an environment variable or secret management service
openai.api_key = os.environ["OPENAI_API_KEY"]

#Create new project plan


def generate_ai_tasks(project_id, user_id, prompt):
    """generates tasks from ChatGPT"""
	
    messages = [
	    {"role": "system", 
		"content": 'You will be asked to recommend an array of tasks to complete a project. Your output should ONLY include an array of task objects like this: [{}, {}]. Task objects should have this shape {"task_name", "type":"task", "description", "date_time"}. "date_time" should have "MM-DD-YYYY HH:MM" format. The first task should have a "date_time" that is todays date. '
		},
		{"role": "user", "content": prompt}
    	]
    
# ADD MEETING OBJECT LATER: Meeting objects should have this shape {"task_name","type":"meeting", "description","date_time", "team"}. "date_time" should have "MM-DD-YYYY HH:MM" format. The first task should have a "date_time" that is todays date. The "teams" are Product Management, Finance, R&D, Operations, Supply Chain, Senior Leadership, Marketing.

    response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=messages
	)
    
    print("***************from ChatGPT******************")
    print(response.choices[0].message.content)
    print(type(response.choices[0].message.content))


    task_list = json.loads(response.choices[0].message.content)

    
    print("*************converted to Python********************")
    print(task_list)
    print(type(task_list[0]))

    for task in task_list:
        if task["type"] == "task":
            t = Task.create_new_task(task_name=task["task_name"],
                                        description=task["description"],
                                        notes="",
                                        type=task["type"],
                                        priority="Moderate",
                                        status="Not Started",
                                        # start_date=task["start_date"],
                                        end_date=task["date_time"],
                                        user_id=user_id,
                                        project_id=project_id,
                                        meeting_user_id=None
                        )
            
        # if task["type"] == "meeting":
        #     team = Team.query.filter_by(name=task["team"]).first()
        #     team_id = team.id
        #     meeting_user = User.query.filter_by(team_id=team_id).first()


        #     t = Task.create_new_task(task_name=task["task_name"],
        #                                 description=task["description"],
        #                                 notes="",
        #                                 type=task["type"],
        #                                 status="Not Started",
        #                                 priority="Moderate",
        #                                 # start_date=task["start_date"],
        #                                 end_date=task["date_time"],
        #                                 user_id=user_id,
        #                                 meeting_user_id=meeting_user.id,
        #                                 project_id=project_id
        #                                 )
        
        db.session.add(t)
        db.session.commit()
    
    messages.append(
        {"role":"assistant",
         "content":task_list}
    )

    return messages
    