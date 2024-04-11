# Diabetes Prediction and Diet Recommendation Backend Server

This project implements a backend server for a machine learning (ML) model-powered system that predicts diabetes and recommends diets. 
It provides functionalities for patient login, registration, diabetes prediction, and diet recommendations.

## Features:

### Patient Management:
* User registration for new patients.
* Secure login for existing patients.

### Diabetes Prediction:
* Accepts patient data (e.g., blood sugar levels, weight, height, family history) as input.
* Utilizes a trained ML model (Random forect classier,... three models was trained for this task) to predict the likelihood of diabetes.
* Returns the prediction results (probability of having diabetes) to the client application.
### Diet Recommendation
* Based on the diabetes prediction and potentially other factors (e.g., age, activity level), recommends personalized diet plans.

## Technology Stack:
* Programming Language: Python
* Framework: Flask
* Database: SQL
* Machine Learning Library: Scikit-learn

## Project Setup
### 1. Prerequisites:
* Python version 3.7 (or higher)
* Xamp SQL database or sql-workbench
### 2. Installation:
1. Clone this repository:
``` git clone https://github.com/Gershonbest/backend-server-ml-diabetes-prediction.git ```
2. Create a virtual environment (recommended) and activate it.
3. Install dependencies:
```pip install -r requirements.txt```
4. Configure the sql database connection
