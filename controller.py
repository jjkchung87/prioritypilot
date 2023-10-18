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
		"content": 'You will be asked to recommend an array of tasks to complete a project. Your output should ONLY include an array of task objects like this: [{}, {}]. Task objects should have this shape {"task_name", "type":"task", "description", "date_time"}. "date_time" should have "MM-DD-YYYY HH:MM" format. No task should have a date before today. '
		},
		{"role": "user", "content": prompt}
    	]
    
# ADD MEETING OBJECT LATER: Meeting objects should have this shape {"task_name","type":"meeting", "description","date_time", "team"}. "date_time" should have "MM-DD-YYYY HH:MM" format. The first task should have a "date_time" that is todays date. The "teams" are Product Management, Finance, R&D, Operations, Supply Chain, Senior Leadership, Marketing.

    response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=messages
	)
    print("***************prompt******************")
    print(prompt)

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
                                        priority="Medium",
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
        #                                 priority="Medium",
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

    messages_no_system = messages[1:]

    return messages_no_system
    
def generate_ai_tips(project_id, task_id):
    """Generate tips for tasks from AI"""



    task = Task.query.get_or_404(task_id)
    task_name = task.task_name
    content = f"I am having trouble with the task: '{task_name}'. Give me 3 tips of how I can navigate this task. Your output should only include an array of 3 tips and nothing else."

    system_message = {"role": "system", 
        "content": "You will be asked to give 3 tips on a particular task from a list of tasks you previously gave for an ongoing project. Your response should only be an array data type of 3 strings and nothing else. Each tip should be no more than 15 words."
    }

    new_message = {
        "role": "user",
        "content": content  # Ensure content is a valid JSON string
    }

    messages = [system_message, new_message]

    conversation = Conversation.query.filter_by(project_id=project_id).first()

    if conversation:
        messages = conversation.get_messages()

        # Iterate through messages and convert content to JSON if it's a list
        for message in messages:
            if isinstance(message['content'], list):
                message['content'] = json.dumps(message['content'])
        
        messages.append(new_message)
        messages.insert(0, system_message)
  
    else:
        conversation = Conversation(user_id=task.user_id,
                                    conversation_type="Assistance",
                                    task_id = task_id,
                                    project_id = project_id)
        db.session.add(conversation)
        db.session.commit()
   
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    tips_str = response.choices[0].message["content"]
    print('*****************TIPS RESPONSE********************')
    print(tips_str)

    tips = json.loads(tips_str)
   
  # Ensure "tips" contains only strings
    updated_tips = []
    for tip in tips:
        if isinstance(tip, dict):
            # Extract the value from the dictionary
            updated_tips.append(next(iter(tip.values())))
        elif isinstance(tip, str):
            updated_tips.append(tip)

    print("*************converted to Python********************")
    print(updated_tips)
    print(type(updated_tips))
    
    # Append the tips to the messages list without converting to JSON
    new_message_for_db = {
            "role": "assistant",
            "content": updated_tips
        }
    
    print('*******************UPDATED MESSAGES******************')
    print(new_message_for_db)



    conversation.set_messages(new_message_for_db)

    return updated_tips





    # messages = [
	#     {"role": "system", 
	# 	"content": 'You will give me a list of helpful tips on how to achieve a certain task. The output should be an array. No more than 3 tips.'
	# 	},
	# 	{"role": "user", "content": prompt}
    # 	]


    