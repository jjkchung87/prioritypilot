
base_url= 'prioritypilot/api'

#***********************************************************************************************************************
# USER
# /users/<id>
# /users (would be a list of user objects)
# /users/signup
# /users/login
# access token provided only at signup and login

{
    "user": {
        "id": 1,
        "email": "barry@company.com",
        "first_name": "Barry",
        "last_name": "Dunderwerk",
        "team_id": 1,
        "role": "Product Manager",
        "projects": [
            {
                "id": 1,
                "project_name": "Q1 2024 New Burger Launch",
                "description": "Limited time only launch of new burger",
                "created_at": "10-09-2023 20:24:56 GMT",
                "modified_at": "10-09-2023 20:24:56 GMT",
                "end_date": "10-09-2023 20:24:56 GMT",
                "user_id": 1,
                "status": "In Progress",
                "tasks":[
                    {
                        "id": 1,
                        "description": "Develop drink concept",
                        "notes": "",
                        "type": "Task",
                        "priority": "Moderate",
                        "status": "Not Started",
                        "created_at": "10-09-2023 20:24:56 GMT",
                        "modified_at": "10-09-2023 20:24:56 GMT",
                        "end_date": "10-09-2023 20:24:56 GMT",
                        "user_id": 1,
                        "meeting_user_id": None,
                        "project_id": 1
                    },
                    {
                        "id": 2,
                        "description": "Meet with Supply Chain to determine ingredient timelines",
                        "notes": "",
                        "type": "meeting",
                        "priority": "moderate",
                        "status": "Not Started",
                        "created_at": "10-09-2023 20:24:56 GMT",
                        "modified_at": "10-09-2023 20:24:56 GMT",
                        "end_date": "10-09-2023 20:24:56 GMT",
                        "user_id": 1,
                        "meeting_user_id": 2,
                        "project_id": 1
                    }
                ]
            }
        ]
    },
    "access_token": "your-access-token",
    "token_type": "bearer",
    "expires_in": 3600
}    
    

#***********************************************************************************************************************
# PROJECT
# /projects/<id>
# /projects would be a list of project objects

{
    "project": {
                "id": 1,
                "project_name": "Q1 2024 New Burger Launch",
                "description": "Limited time only launch of new burger",
                "created_at": "10-09-2023 20:24:56 GMT",
                "modified_at": "10-09-2023 20:24:56 GMT",
                "end_date": "10-09-2023 20:24:56 GMT",
                "user_id": 1,
                "status": "In Progress",
                "tasks":[
                    {
                        "id": 1,
                        "description": "Develop drink concept",
                        "notes": "",
                        "type": "Task",
                        "priority": "Moderate",
                        "status": "Not Started",
                        "created_at": "10-09-2023 20:24:56 GMT",
                        "modified_at": "10-09-2023 20:24:56 GMT",
                        "end_date": "10-09-2023 20:24:56 GMT",
                        "user_id": 1,
                        "meeting_user_id": None,
                        "project_id": 1
                    },
                    {
                        "id": 2,
                        "description": "Meet with Supply Chain to determine ingredient timelines",
                        "notes": "",
                        "type": "meeting",
                        "priority": "moderate",
                        "status": "Not Started",
                        "created_at": "10-09-2023 20:24:56 GMT",
                        "modified_at": "10-09-2023 20:24:56 GMT",
                        "end_date": "10-09-2023 20:24:56 GMT",
                        "user_id": 1,
                        "meeting_user_id": 2,
                        "project_id": 1
                    }
                ]
            }
}


#***********************************************************************************************************************
# TASK
# /tasks/<id>
# /tasks would be a list of task objects

{"task":
    {
       "id": 1,
        "description": "Develop drink concept",
        "notes": "",
        "type": "Task",
        "priority": "Moderate",
        "status": "Not Started",
        "created_at": "10-09-2023 20:24:56 GMT",
        "modified_at": "10-09-2023 20:24:56 GMT",
        "end_date": "10-09-2023 20:24:56 GMT",
        "user_id": 1,
        "meeting_user_id": None,
        "project_id": 1
    }
}
