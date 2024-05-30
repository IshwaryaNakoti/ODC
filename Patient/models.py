from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from typing import List

class Patient(BaseModel):
    p_id : int
    p_name : str
    p_email : EmailStr
    p_password : str
    p_phone : str
    p_dob : date
    p_city : str
    p_state : str
    p_country : str 

class LoginCredentials(BaseModel):
    email : EmailStr
    password : str

class Prescription(BaseModel):
    patient_id : int
    doctor_id : int
    prescription_id : int
    prescription_date : date
    prescription_details : str

class MedicalHistory(BaseModel):
    patient_id: int
    patient_complaints: str
    medical_conditions: List[str] = []
    allergies: List[str] = []
    surgeries: List[str] = []
    medications: List[str] = []



