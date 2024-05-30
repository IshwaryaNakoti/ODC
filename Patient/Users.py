from flask import Flask, render_template, request, flash, Blueprint, redirect, url_for, jsonify
from config import SNOWFLAKE_CONNECTOR
from controller import execute_query, requires_auth
from werkzeug.security import generate_password_hash, check_password_hash

users_api = Blueprint('users_api', __name__)

@users_api.route('/option/<option>')
def handle_option(option):
    if option == 'Patient':
        return render_template('patientLogin.html')
    elif option == 'Doctor':
        return render_template('doctorLogin.html')
    elif option == 'patientSignup':
        return render_template('patientSignup.html')
    elif option == 'doctorSignup':
        return render_template('doctorSignup.html')
    else:
        return "Invalid option"

@users_api.route('/userSignup', methods = ["GET",'POST'])
def get_patient_signup_details():
    name = request.form.get('patientName')
    email = request.form.get('patientEmail')
    password = request.form.get('patientPassword')
    dob = request.form.get('patientDob')
    phone = request.form.get('patientPhone')
    city = request.form.get('patientCity')
    state = request.form.get('patientState')
    country = request.form.get('patientCountry')
    # patient = {
    #     "p_name" : name, "p_email" :email, "p_password": password, "p_dob":dob, "p_phone":phone, "p_city":city, "p_state": state, "p_country":country
    # }
    inserted_patient_data = execute_query("""INSERT INTO ODC.PUBLIC.PATIENT 
                            (P_NAME, P_EMAIL, P_PASSWORD, P_PHONE, P_DOB, P_CITY, P_STATE, P_COUNTRY) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                            (name, email, password, phone, dob, city, state, country))
    if isinstance(inserted_patient_data, Exception):
        return f"Error occured - {inserted_patient_data}"
    print(f"Data inserted into Patient Table\nPatient={inserted_patient_data}")
    return render_template('patientLogin.html')

@users_api.route('/login', methods = ['GET', 'POST'])
def check_patient_login():
    email = request.form.get('patientEmail')
    password = request.form.get('patientPassword')
    get_details = execute_query('''SELECT P_ID, P_EMAIL, P_Password, P_NAME FROM ODC.PUBLIC.PATIENT WHERE P_EMAIL = %s''',(email))
    if isinstance(get_details, Exception):
        return f"Error occured - {get_details}"
    if len(get_details) and get_details[0][2] == password:
        # return redirect(url_for('users_api.get_patient', Patient = get_details))
        return render_template('patientDashboard.html', Patient = get_details)
    else:
        return render_template('loginFail.html', type = "Patient")

@users_api.route('/getData', methods = ['GET'])
def print_patient_data():
    values = execute_query("""Select * from ODC.PUBLIC.PATIENT """, fetchall=True)
    if isinstance(values, Exception):
        return f"Error occured - {values}"
    print("Data collected from Patient Table")
    return jsonify(values)

@users_api.route('/dashboard/<Patient>')
def get_patient(Patient):
    return f"my details= {Patient}"

@users_api.route('/findDoctor', methods=['Post'])
def find_doctor_from_location_speacialization():
    location = request.form.get("location")
    specialization = request.form.get("specialization")
    patient_id = request.form.get("patient_id")
    print(type(patient_id))
    get_patient_details = execute_query('SELECT P_ID, P_EMAIL, P_PHONE, P_NAME FROM ODC.PUBLIC.PATIENT WHERE P_ID = %s', str(patient_id))
    if isinstance(get_patient_details, Exception):
        return f"Error occured - {get_patient_details}"
    if location and specialization:
        query = '''
            SELECT 
            D.D_ID,
            D.D_NAME,
            D.D_EMAIL,
            D.D_PHONE,
            D.D_EXPERIENCE,
            D.D_CITY,
            D.D_STATE,
            D.D_COUNTRY
            FROM 
                ODC.PUBLIC.DOCTOR D
            JOIN 
                ODC.PUBLIC.DOCTOR_SPECIALITY DS ON D.D_ID = DS.DOCTOR_ID
            JOIN 
                ODC.PUBLIC.SPECIALITY S ON DS.SPECIALITY_ID = S.SPECIALITY_ID
            WHERE 
                D.D_CITY = %s AND
                S.SPECIALITY_NAME = %s;

        '''
        listOfDoctors = execute_query(query, (location, specialization), fetchall=True)

    elif location:
        query = '''
            SELECT 
            D.D_ID,
            D.D_NAME,
            D.D_EMAIL,
            D.D_PHONE,
            D.D_EXPERIENCE,
            D.D_CITY,
            D.D_STATE,
            D.D_COUNTRY
            FROM 
                ODC.PUBLIC.DOCTOR D
            JOIN 
                ODC.PUBLIC.DOCTOR_SPECIALITY DS ON D.D_ID = DS.DOCTOR_ID
            JOIN 
                ODC.PUBLIC.SPECIALITY S ON DS.SPECIALITY_ID = S.SPECIALITY_ID
            WHERE 
                D.D_CITY = %s;

        '''
        listOfDoctors = execute_query(query, (location), fetchall=True)
    
    elif location == None and specialization == None:
        return "Location and specialization should be mentioned."

    else:
        query = '''
            SELECT 
            D.D_ID,
            D.D_NAME,
            D.D_EMAIL,
            D.D_PHONE,
            D.D_EXPERIENCE,
            D.D_CITY,
            D.D_STATE,
            D.D_COUNTRY
            FROM 
                ODC.PUBLIC.DOCTOR D
            JOIN 
                ODC.PUBLIC.DOCTOR_SPECIALITY DS ON D.D_ID = DS.DOCTOR_ID
            JOIN 
                ODC.PUBLIC.SPECIALITY S ON DS.SPECIALITY_ID = S.SPECIALITY_ID
            WHERE
                S.SPECIALITY_NAME = %s;
        '''
        listOfDoctors = execute_query(query, (specialization), fetchall=True)
    print(listOfDoctors)
    return render_template('doctorList.html', location = location, specialization = specialization, Patient = get_patient_details, listOfDoctors = listOfDoctors)

@users_api.route('/bookAppointment/<Doctor_id>', methods = ['GET'])
def book_appointment(Doctor_id):
    doctor_details = ('''SELECT * FROM ODC.PUBLIC.DOCTOR WHERE D_ID = %s''', Doctor_id)
    doctor_status = ('''SELECT STATUS FROM ODC.PUBLIC.DOCTOR_STATUS WHERE D_ID = %s ''', Doctor_id)
    if isinstance(doctor_status, Exception) or isinstance(doctor_details, Exception):
        return f"Error occured in book appointment - \n1.{doctor_status} or \n2.{doctor_details}  "
    return render_template('bookAppointment.html',doctor_details=doctor_details, doctor_status=doctor_status)

@users_api.route('/myBookings', methods = ['POST'])
def my_booking():
    doctor_id = request.form.get("doctor_id")
    patient_id = request.form.get("patient_id")
    date = request.form.get('date')
    timeslot = request.form.get('timeslot')
    comment = request.form.get('comment')
    print(patient_id)
    print(doctor_id)
    print(date, timeslot,comment)
    insert_new = execute_query('INSERT INTO ODC.PUBLIC.BOOKING (DOCTOR_ID, PATIENT_ID, DATE, TIMESLOT, COMMENT) VALUES (%s, %s, %s, %s, %s) ', (doctor_id, patient_id, date, timeslot, comment))
    get_details = execute_query('''SELECT P_ID, P_EMAIL, P_Password, P_NAME FROM ODC.PUBLIC.PATIENT WHERE P_ID = %s''',patient_id)
    all_bookings = execute_query('SELECT * FROM ODC.PUBLIC.BOOKING WHERE PATIENT_ID = %s', patient_id)
    print("p=", get_details)
    print("prev =",all_bookings)
    all_bookings = execute_query('SELECT * FROM ODC.PUBLIC.BOOKING WHERE PATIENT_ID = %s', patient_id)
    print("after=",all_bookings)
    return render_template('patientDashboard.html', Patient = get_details, Bookings = all_bookings)

