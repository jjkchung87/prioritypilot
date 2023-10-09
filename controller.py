import os
import openai
import json
from datetime import datetime
from models import Conversation, Project, db


# Load your API key from an environment variable or secret management service
openai.api_key = "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"

#Create new project plan

def create_new_project(project_name, 
                       description, 
                       start_date, 
                       end_date, 
                       user_id, 
                       prompt=""
                       ):
    """Create new project"""
		
    project = Project.create_new_project(
	    project_name=project_name,
	    description=description,
	    start_date=start_date,
	    end_date=end_date,
	    user_id=user_id
    )

    
    conversation = Conversation.create_new_conversation(user_id,
                                                        type='New Project',
                                                        task_id=None,
                                                        project_id=project.id
                                                        )

    db.session.add(conversation)
    db.session.commit()

    messages = create_new_project_conversation(prompt)
    conversation.set_messages(messages)
    

def create_new_project_conversation(prompt):
    """Create new project conversation"""
	
    messages = [
	    {"role": "system", 
		"content": "You will be asked to recommend an array of tasks and meetings to complete a project. The response should be an array consisting of task and meeting objects. DO NOT RETURN a string data type. Task objects should have this shape {'type':'task', 'description', 'date'}. Meeting objects should have this shape {'type':'meeting', 'description','date_time','department'}. 'date_time' should have 'MM-DD-YYYY HH:MM' format. The first task should be on today's date. No more than 3 tasks. The departments are Product Management, Finance, R&D, Operations, Supply Chain, Senior Leadership, Marketing."
		},
		{"role": "user", "content": prompt}
    	]
    
    response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=messages
	)
    
    response_list = response.choices[0].message.content
    
    # response_list = json.loads(response_string.replace("'", "\""))
    messages.append(
        {"role":"assistant",
         "content":response_list}
    )

    return messages
    