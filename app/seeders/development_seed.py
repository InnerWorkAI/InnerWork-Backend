import random
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import hash_password

from app.models.company_model import CompanyModel
from app.models.user_model import UserModel
from app.models.employee_model import EmployeeModel
from app.models.company_admin_model import CompanyAdminModel
from app.models.weekly_burnout_form_model import WeeklyBurnoutFormModel

from app.enums.department import DepartmentEnum
from app.enums.education import EducationEnum
from app.enums.education_field import EducationFieldEnum
from app.enums.gender import GenderEnum
from app.enums.job_level import JobLevelEnum
from app.enums.job_role import JobRoleEnum
from app.enums.marital_status import MaritalStatusEnum


FIRST_NAMES = ["Carlos", "Lucía", "Miguel", "Sofía", "Javier",
               "Elena", "Andrés", "Marta", "David", "Paula"]

LAST_NAMES = ["García", "Martínez", "López", "Fernández",
              "Rodríguez", "Sánchez", "Pérez", "Gómez"]

CITIES = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao"]

STREETS = [
    "Calle Gran Vía 45, Madrid",
    "Av. Diagonal 640, Barcelona",
    "Calle Colón 12, Valencia",
    "Av. de la Constitución 18, Sevilla",
    "Calle Larios 7, Málaga"
]


# ==========================
# SCORE GENERATOR
# ==========================

def generate_realistic_scores(high_risk=False, progression_factor=0):

    if high_risk:
        base = 60 + progression_factor * 35
    else:
        base = 25 + progression_factor * 20

    image_score = max(5, min(100, int(random.gauss(base, 5))))
    text_score = max(5, min(100, int(random.gauss(base, 7))))
    form_score = max(5, min(100, int(random.gauss(base, 6))))

    final_score = round((image_score + text_score + form_score) / 3, 2)
    burnout_score = f"{image_score}, {text_score}, {form_score}"

    return image_score, text_score, form_score, burnout_score, final_score


# ==========================
# MAIN SEED
# ==========================

def run_development_seed():
    db: Session = SessionLocal()

    try:
        print("🚀 Iniciando Development Seed...")

        if db.query(UserModel).count() > 0:
            print("⚠ Base de datos ya tiene datos, seed omitido.")
            return

        # ==========================
        # 1️⃣ Empresa
        # ==========================
        company = CompanyModel(
            name="NovaTech Solutions SL",
            address=random.choice(STREETS)
        )
        db.add(company)
        db.commit()
        db.refresh(company)

        # ==========================
        # 2️⃣ Admin Principal
        # ==========================
        admin_user = UserModel(
            email="admin@tech.com",
            password=hash_password(settings.ADMIN_PASSWORD)
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        db.add(CompanyAdminModel(
            user_id=admin_user.id,
            company_id=company.id,
            is_primary_admin=True
        ))

        # ==========================
        # 3️⃣ Admin RRHH
        # ==========================
        hr_user = UserModel(
            email="rrhh@tech.com",
            password=hash_password(settings.ADMIN_PASSWORD)
        )
        db.add(hr_user)
        db.commit()
        db.refresh(hr_user)

        db.add(CompanyAdminModel(
            user_id=hr_user.id,
            company_id=company.id,
            is_primary_admin=False
        ))

        db.commit()

        # ==========================
        # 4️⃣ Empleados FULL DATA
        # ==========================
        employees = []

        for i in range(8):

            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)

            # Edad realista
            age = random.randint(26, 45)
            birth_year = datetime.now().year - age

            birth_date = date(
                birth_year,
                random.randint(1, 12),
                random.randint(1, 28)
            )

            # Antigüedad empresa
            years_in_company = random.randint(1, 10)
            contract_start_date = date(
                datetime.now().year - years_in_company,
                random.randint(1, 12),
                random.randint(1, 28)
            )

            current_role_start_date = contract_start_date + timedelta(days=random.randint(180, 900))

            last_promotion_date = current_role_start_date + timedelta(days=random.randint(200, 700))
            if last_promotion_date > datetime.now().date():
                last_promotion_date = None

            last_manager_date = contract_start_date + timedelta(days=random.randint(200, 1200))
            if last_manager_date > datetime.now().date():
                last_manager_date = None

            # Género coherente con imagen
            gender_value = random.choice(list(GenderEnum)).value

            user = UserModel(
                email=f"{first_name.lower()}.{last_name.lower()}{i}@tech.com",
                password=hash_password("1234")
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            employee = EmployeeModel(
                user_id=user.id,
                company_id=company.id,

                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,

                gender=gender_value,
                marital_status=random.choice(list(MaritalStatusEnum)).value,

                home_address=f"Calle {last_name} {random.randint(1, 120)}, {random.choice(CITIES)}",
                phone=f"+34 6{random.randint(10000000, 99999999)}",
                profile_image_url="",

                department=random.choice(list(DepartmentEnum)).value,
                education=random.choice(list(EducationEnum)).value,
                education_field=random.choice(list(EducationFieldEnum)).value,
                job_level=random.choice(list(JobLevelEnum)).value,
                job_role=random.choice(list(JobRoleEnum)).value,

                number_of_companies_worked=random.randint(1, 4),

                contract_start_date=contract_start_date,
                current_role_start_date=current_role_start_date,
                last_promotion_date=last_promotion_date,
                last_manager_date=last_manager_date,

                monthly_salary=random.randint(2800, 6500),
                percent_salary_hike=round(random.uniform(5, 18), 2),

                created_at=contract_start_date
            )

            db.add(employee)
            db.commit()
            db.refresh(employee)
            employees.append(employee)

        # ==========================
        # 5️⃣ Formularios (16 semanas)
        # ==========================
        weeks_history = 16

        for idx, employee in enumerate(employees):

            high_risk = idx == 0

            for week in range(weeks_history):

                progression = week / weeks_history

                image_score, text_score, form_score, burnout_score, final_score = \
                    generate_realistic_scores(high_risk, progression)

                created_date = datetime.now() - timedelta(days=7 * (weeks_history - week))

                form = WeeklyBurnoutFormModel(
                    employee_id=employee.id,

                    written_feedback=(
                        "Estoy agotado y me cuesta desconectar del trabajo."
                        if high_risk and progression > 0.6
                        else "Semana productiva con carga manejable."
                    ),

                    environment_satisfaction=random.randint(1, 5),
                    overtime=random.randint(0, 1),
                    job_involvement=random.randint(2, 4),
                    performance_rating=random.randint(2, 4),
                    job_satisfaction=random.randint(1, 5),
                    work_life_balance=random.randint(1, 5),
                    business_travel=random.randint(0, 2),

                    image_score=image_score,
                    text_score=text_score,
                    form_score=form_score,

                    burnout_score=burnout_score,
                    final_burnout_score=final_score,

                    created_at=created_date
                )

                db.add(form)

        db.commit()
        print("✅ Seed completado correctamente.")

    except Exception as e:
        db.rollback()
        print("❌ Error en seed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    run_development_seed()