# PriorityPilot

## Project Overview

PriorityPilot is an AI-powered project management and task recommendation system designed to help users efficiently navigate their projects and tasks. 

## Video Demo

[Demo](https://vimeo.com/880364850?share=copy)


## Features

- **AI powered task generation** for projects
- **AI powered tip generation** for navigating tasks
- **Integration with user's organizational database** to assign tasks to appropriate team members and track progress
- **Automated task update reminders** to enable frictionless status updates

## Acknowledgment

This project was built as part of Springboard's 2023 Hackathon by the following team:

*Developers:*
- [Irina Dutterer](linkedin.com/in/irina-d-631a21242)
- [Justin Chung](linkedin.com/in/justinjkchung)

*UX/UI:*
- [Amanda Cornelius](linkedin.com/in/amandaux)
- [Analisa Esther](linkedin.com/in/analisaesther)
- [Priyadharshini Thirukonda Mohanlal](linkedin.com/in/priyadharshini-thirukonda-mohanlal)
  
*Cyber-Security:*
- [Courtney Ellington](linkedin.com/in/courtneyellington)


## Technologies Used

- **Frontend**: React.js, Semantic UI React, React Router, Axios
- **Backend**: Flask, Flask-RESTful, SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: Flask-JWT-Extended
- **Email Verification**: Flask-Mail
- **AI Task Recommendations**: (Specify the AI model/library used)
- **Version Control**: Git and GitHub

## Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- Node.js and npm (for the frontend)
- Python 3.x (for the backend)
- PostgreSQL database

### Installation

1. **Clone the GitHub repository:**

  ```bash
  git clone https://github.com/your-username/prioritypilot.git
  ```

3. **Navigate to the project's root directory:**
  
  ```bash
  cd prioritypilot
  ```

3. **Install the frontend dependencies:**

  ```bash
  cd Frontend
  npm install
  ```

4. **Install the backend dependencies (create a virtual environment first, if needed):**

  ```bash
  cd Backend
  pip install -r requirements.txt
  ```
### Running the app

1. **Start the frontend development server (in the 'Frontend' directory):**
  ```bash
  npm start
  ```
   
3. **Start the backend server (in the 'Backend' directory):**
  ```bash
  python app.py
  flask run
  ```
### Using the app
1. **Register** an account
2. **Create a new project** with "+ Create Project") button on main nav
3. **Generate tasks with AI** by selecting "PriorityPilot AI" on new project modal
4. **Generate tips for each task** using "AI Recommendation" button on each task card

### Licence
This project is licensed under the MIT License - see the LICENSE file for details.


  
