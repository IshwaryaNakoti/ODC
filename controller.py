from flask import current_app, request
from functools import wraps
from config import SNOWFLAKE_CONNECTOR

def execute_query(query, params=None, fetchall=True):
        try:
            connection = SNOWFLAKE_CONNECTOR
            cursor = connection.cursor()
            current_app.logger.info(f"Executing query: {query} with params: {params}")
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetchall:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
            
            current_app.logger.info(f"Query result: {result}")
            connection.commit()
            cursor.close()
            return result
        except Exception as e:
            current_app.logger.error(f"Database query failed: {e}")
            return e

def get_user_credentials(useremail):
    # This function will retrieve user credentials from both the doctor and patient tables.
    doctor_query = 'SELECT D_EMAIL, D_PASSWORD FROM ODC.PUBLIC.DOCTOR WHERE D_EMAIL = %s'
    patient_query = 'SELECT P_EMAIL, P_PASSWORD FROM ODC.PUBLIC.PATIENT WHERE P_EMAIL = %s'

    doctor_credentials = execute_query(doctor_query, (useremail,), fetchall=False)
    if doctor_credentials:
        return doctor_credentials

    patient_credentials = execute_query(patient_query, (useremail,), fetchall=False)
    return patient_credentials

def check_auth(email, password):
    user_credentials = get_user_credentials(email)
    if user_credentials:
        stored_email, stored_password = user_credentials
        if email == stored_email and password == stored_password:
            return True
    return False

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        print(auth)
        if not auth or not check_auth(auth.email, auth.password):
            return "unauthorized", 401
        return f(*args, **kwargs)
    return decorated

        
    
         
         
    