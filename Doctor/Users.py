from config import SNOWFLAKE_CONNECTOR
from controller import execute_query
from datetime import datetime
from flask import Flask, render_template, request, current_app, Blueprint, redirect, jsonify, url_for

doctors_api = Blueprint('doctors_api', __name__)

@doctors_api.route('/doctorSignup')
def doctorSignupTemplate():
    return render_template('doctorSignup.html')

@doctors_api.route('/doctorSignupDetails', methods = ['GET', 'POST'])
def get_doctor_signup_details():
    name = request.form.get('doctorName')
    email = request.form.get('doctorEmail')
    password = request.form.get('doctorPassword')
    experience = request.form.get('doctorExperience')
    specialization = request.form.get('doctorSpecialization')
    phone = request.form.get('doctorPhone')
    city = request.form.get('doctorCity')
    state = request.form.get('doctorState')
    country = request.form.get('doctorCountry')
    inserted_data_doctor = execute_query('''INSERT INTO ODC.PUBLIC.DOCTOR (D_NAME, D_EMAIL, D_PASSWORD, D_PHONE, D_EXPERIENCE, D_CITY, D_STATE, D_COUNTRY) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',(name, email, password, phone, experience, city, state, country))
    get_doctor_id = execute_query('SELECT D_ID FROM ODC.PUBLIC.DOCTOR WHERE D_EMAIL = %s', email, fetchall=False)
    get_speciality_id = execute_query('SELECT SPECIALITY_ID FROM ODC.PUBLIC.SPECIAlITY WHERE SPECIALITY_NAME = %s', specialization, fetchall=False)
    inserted_data_speciality = execute_query('INSERT INTO ODC.PUBLIC.DOCTOR_SPECIALITY VALUES (%s, %s)', (get_doctor_id,get_speciality_id))
    if isinstance(inserted_data_doctor,Exception) and isinstance(get_doctor_id, Exception) and isinstance(get_speciality_id, Exception) and isinstance(inserted_data_speciality, Exception):
        return "error occured in get_doctor_signup_details"
    print(f"Data inserted into Doctor Table-\nDoctor={inserted_data_doctor}\nDoctor-spciality={inserted_data_speciality}")
    return render_template('doctorLogin.html')

@doctors_api.route('/checkDoctorLogin', methods = ['GET', 'POST'])
def check_doctor_login():
    email = request.form.get('doctorEmail')
    password = request.form.get('doctorPassword')
    query = "SELECT D_ID, D_EMAIL, D_PASSWORD, D_NAME FROM ODC.PUBLIC.DOCTOR WHERE D_EMAIL = %s"
    get_details = execute_query(query, email)
    if isinstance(get_details, Exception):
        return f"Error occured - {get_details}"
    if len(get_details) and get_details[0][2] == password:
         return render_template('doctorDashboard.html', Doctor = get_details)
    else:
        return render_template('loginFail.html', type = "Doctor")

@doctors_api.route('/checkAppointmentRequest', methods = ['POST'])
def check_appointment_request():
    doctor_id = request.form.get('doctor_id')
    get_details = execute_query("SELECT D_EMAIL, D_PASSWORD, D_NAME FROM ODC.PUBLIC.DOCTOR WHERE D_ID = %s", (doctor_id))
    get_requets = execute_query("SELECT * FROM ODC.PUBLIC.BOOKING WHERE DOCTOR_ID = %s", doctor_id)
    
    if isinstance(get_details, Exception):
        return f"Error occured - {get_details}"
    if isinstance(get_requets, Exception):
        return f"Error occured -{get_requets}"
    if len(get_requets):
        all_patient = []
        for i in range(len(get_requets)):
            get_patient = execute_query('SELECT P_ID, P_NAME, P_PHONE, P_EMAIL FROM ODC.PUBLIC.PATIENT WHERE P_ID = %s', get_requets[i][2], fetchall=False)
            all_patient.append(get_patient)
            print("patient=",all_patient)
            print("Get requets = ", get_requets)
        return render_template('checkAppointmentRequests.html', Doctor = get_details, Requests = get_requets, Patient = all_patient)
    else:
        return render_template('checkAppointmentRequests.html', Doctor = get_details)

@doctors_api.route('/handleBookingResponse', methods = ['POST'])
def accept_reject_appointments():
    response = request.form.get('response')
    booking_id = request.form.get('booking_id')
    doctor_id = request.form.get('doctor_id')
    patient_id = request.form.get('patient_id')
    doctor_details = execute_query('SELECT D_ID, D_EMAIL, D_PASSWORD, D_NAME FROM ODC.PUBLIC.DOCTOR WHERE D_EMAIL = %s', doctor_id)
    if response == 'accept':
        accept = execute_query('UPDATE ODC.PUBLIC.BOOKING SET STATUS = %s WHERE BOOKING_ID = %s;', ("confirmed", booking_id))
    else:
        reject = execute_query('DELETE FROM ODC.PUBLIC.BOOKING WHERE BOOKING_ID = %s;', booking_id)
    return render_template('doctorDashboard.html', Doctor = doctor_details)

@doctors_api.route('/checkAcceptedAppointments', methods = ['POST'])
def check_accepted_appointments():
    doctor_id = request.form.get('doctor_id')
    doctor_details = execute_query('SELECT D_ID, D_EMAIL, D_PASSWORD, D_NAME FROM ODC.PUBLIC.DOCTOR WHERE D_ID = %s', doctor_id)
    all_bookings = execute_query('SELECT * FROM ODC.PUBLIC.BOOKING WHERE DOCTOR_ID = %s', doctor_id)
    get_patients = []
    if len(all_bookings):
        for i in range(len(all_bookings)):
            patient = execute_query("SELECT P_ID, P_NAME, P_PHONE, P_EMAIL FROM ODC.PUBLIC.PATIENT WHERE P_ID = %s", all_bookings[i][2], fetchall=False)
            get_patients.append(patient)   
        return render_template("acceptedAppointments.html", Doctor = doctor_details, Patient = get_patients, Requests = all_bookings)
    else:
        return render_template("acceptedAppointments.html", Doctor = doctor_details)
    
@doctors_api.route('/joinroom')
def join_room():
    booking_id  = request.form.get("booking_id")
    doctor_id = request.form.get("doctor_id")
    patient_id = request.form.get("patient_id")
