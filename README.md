# PetMatch Backend - A Pet Adoption Platform

This repository contains the backend of the PetMatch application, a platform designed to connect potential pet adopters with pets in need of a home. The backend is built using Flask and MySQL, handling user authentication, pet management, and adoption processes.

## Features
- User authentication and registration
- Pet listing and management
- Adoption request processing
- RESTful API for frontend integration

## Technologies Used
- Flask
- MySQL
- SQLAlchemy

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/PetMatch.git
   cd petmatch-backend
Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install dependencies:
pip install -r requirements.txt
Set up the database:

Create the database in MySQL.
Set up the environment variables for your database configuration as described below.
Run migrations or initialize the database.
flask db init
flask db migrate
flask db upgrade
Run the application:
flask run
Configuration
Note: For security reasons, the config.py file is not included in this repository. However, here is the structure of the config.py file that you can use:

import os

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'your_default_password')
MYSQL_DB = os.getenv('MYSQL_DB', 'petmatch')

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(24))
Before running the application, ensure you set up the following environment variables:

MYSQL_HOST: The MySQL host (default: localhost).
MYSQL_USER: The MySQL user (default: root).
MYSQL_PASSWORD: The MySQL password.
MYSQL_DB: The MySQL database name (default: petmatch).
JWT_SECRET_KEY: The secret key for JWT (can be generated using os.urandom(24)).
You can set these variables in your environment, or place them in a .env file and use python-dotenv to load them.


