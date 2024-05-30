from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from typing import List

class Doctor(BaseModel):
    d_id : int
    d_name : str
    d_email : EmailStr
    d_password : str
    d_experience : int
    d_specialist : str
    d_phone : str
    d_city : str
    d_state : str
    d_country : str

class DoctorSchedule(BaseModel):
    doctor_id : int
    available_time_slot : List[datetime] = []
    booked_appointments :List[datetime] = []
