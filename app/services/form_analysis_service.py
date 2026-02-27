import os
import joblib
import xgboost
import numpy as np
from datetime import date
from app.schemas.weekly_burnout_form_schema import WeeklyBurnoutFormCreateBase
from app.models.employee_model import EmployeeModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "employee_attrition.joblib")

class FormAnalysisService:
    _model = None

    @classmethod
    def _load_model(cls):
        if cls._model is None:
            if not os.path.exists(MODEL_PATH):
                print(f"[ERROR] Model not found at {MODEL_PATH}")
                return
            print("[INFO] Loading IBM Attrition XGBoost model...")
            cls._model = joblib.load(MODEL_PATH)
            
    @staticmethod
    def _calculate_years(start_date: date) -> int:
        if not start_date:
            return 0
        today = date.today()
        return today.year - start_date.year - ((today.month, today.day) < (start_date.month, start_date.day))

    @staticmethod
    def _get_enum_value(field, default_value):
        if field is None:
            return default_value
        return field.value if hasattr(field, "value") else field

    @classmethod
    def predict_burnout(cls, form_data: WeeklyBurnoutFormCreateBase, employee: EmployeeModel = None) -> float:
        cls._load_model()
        
        age = cls._calculate_years(employee.birth_date) if employee and employee.birth_date else 30
        distance = 10 
        
        education = cls._get_enum_value(employee.education if employee else None, 3)
        gender_val = cls._get_enum_value(employee.gender if employee else None, 1)
        job_level = cls._get_enum_value(employee.job_level if employee else None, 1)
        
        monthly_income = float(employee.monthly_salary) if employee and employee.monthly_salary else 5000.0
        num_companies = employee.number_of_companies_worked if employee and employee.number_of_companies_worked else 1
        pct_hike = float(employee.percent_salary_hike) if employee and employee.percent_salary_hike else 10.0
        
        total_working_years = age - 20 if age > 20 else 1
        years_at_company = cls._calculate_years(employee.contract_start_date) if employee else 2
        years_in_role = cls._calculate_years(employee.current_role_start_date) if employee else 2
        years_since_promo = cls._calculate_years(employee.last_promotion_date) if employee else 1
        years_with_manager = cls._calculate_years(employee.last_manager_date) if employee else 2

        dept = cls._get_enum_value(employee.department if employee else None, -1)
        ed_field = cls._get_enum_value(employee.education_field if employee else None, -1)
        role = cls._get_enum_value(employee.job_role if employee else None, -1)
        marital = cls._get_enum_value(employee.marital_status if employee else None, -1)

        def map_to_ibm_4(val):
            val = val or 3
            if val <= 1: return 1
            if val == 2: return 2
            if val == 3 or val == 4: return 3
            return 4 

        env_sat = map_to_ibm_4(form_data.environment_satisfaction)
        job_sat = map_to_ibm_4(form_data.job_satisfaction)
        job_inv = map_to_ibm_4(form_data.job_involvement)
        wl_balance = map_to_ibm_4(form_data.work_life_balance)

        perf_val = form_data.performance_rating or 3
        ibm_perf = 4 if perf_val >= 4 else 3
        ibm_overtime = 1 if (form_data.overtime or 0) >= 4 else 0
        travel_val = form_data.business_travel or 1
        
        if travel_val >= 5: ibm_travel = 2
        elif travel_val >= 2: ibm_travel = 1
        else: ibm_travel = 0

        features = [
            age, ibm_travel, distance, education, env_sat, gender_val, job_inv, 
            job_level, job_sat, monthly_income, num_companies, ibm_overtime, pct_hike, 
            ibm_perf, total_working_years, wl_balance, years_at_company, years_in_role, 
            years_since_promo, years_with_manager,
            
            1 if dept == 0 else 0, 1 if dept == 1 else 0,                           
            1 if ed_field == 0 else 0, 1 if ed_field == 2 else 0, 1 if ed_field == 1 else 0, 
            1 if ed_field == 5 else 0, 1 if ed_field == 3 else 0,                       
            1 if role == 8 else 0, 1 if role == 2 else 0, 1 if role == 5 else 0, 
            1 if role == 3 else 0, 1 if role == 7 else 0, 1 if role == 1 else 0, 
            1 if role == 0 else 0, 1 if role == 6 else 0,                           
            1 if marital == 1 else 0, 1 if marital == 0 else 0                         
        ]

        features_array = np.array([features])
        
        probabilities = cls._model.predict_proba(features_array)
        
        raw_probability = float(probabilities[0][1])
        
        min_expected = 0.0100
        max_expected = 0.1500
        scaled_score = (raw_probability - min_expected) / (max_expected - min_expected)
        base_ml_score = max(0.0, min(1.0, scaled_score))
        
        stress_env = 6 - (form_data.environment_satisfaction or 3)
        stress_job = 6 - (form_data.job_satisfaction or 3)
        stress_inv = 6 - (form_data.job_involvement or 3)
        stress_wlb = 6 - (form_data.work_life_balance or 3)
        stress_perf = 6 - (form_data.performance_rating or 3)
        
        stress_ot = form_data.overtime or 1
        stress_travel = form_data.business_travel or 1
        
        total_stress_points = stress_env + stress_job + stress_inv + stress_wlb + stress_perf + stress_ot + stress_travel
        
        normalized_form_stress = (total_stress_points - 7) / 28.0 
        
        normalized_form_stress = max(0.0, min(1.0, normalized_form_stress))
        
        weight_ml = 0.40
        weight_form = 0.60
        
        final_burnout_score = (base_ml_score * weight_ml) + (normalized_form_stress * weight_form)
        
        print(f"[INFO] ML Base: {base_ml_score:.4f} (40%) | Form Stress: {normalized_form_stress:.4f} (60%) -> Final Score: {final_burnout_score:.4f}")
        return round(final_burnout_score, 4)