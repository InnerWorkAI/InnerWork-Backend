import random
from datetime import date, timedelta
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


def run_development_seed():
    db: Session = SessionLocal()
    try:
        print("Iniciando Development Seed...")

        if db.query(UserModel).count() > 0 or db.query(CompanyModel).count() > 0:
            print("Base de datos ya tiene datos, seed omitido.")
            return

        # ==========================
        # 1️⃣ Crear Empresa
        # ==========================
        company = CompanyModel(
            name="Tech Solutions Inc",
            address="Av. Innovación 123, Ciudad Tech"
        )
        db.add(company)
        db.commit()
        db.refresh(company)

        # ==========================
        # 2️⃣ Crear Admin Principal
        # ==========================
        primary_admin_user = UserModel(
            email="admin@tech.com",
            password=hash_password(settings.ADMIN_PASSWORD)
        )
        db.add(primary_admin_user)
        db.commit()
        db.refresh(primary_admin_user)

        primary_admin = CompanyAdminModel(
            user_id=primary_admin_user.id,
            company_id=company.id,
            is_primary_admin=True
        )
        db.add(primary_admin)

        # ==========================
        # 3️⃣ Crear Admin Secundario
        # ==========================
        secondary_admin_user = UserModel(
            email="hr@tech.com",
            password=hash_password(settings.ADMIN_PASSWORD)
        )
        db.add(secondary_admin_user)
        db.commit()
        db.refresh(secondary_admin_user)

        secondary_admin = CompanyAdminModel(
            user_id=secondary_admin_user.id,
            company_id=company.id,
            is_primary_admin=False
        )
        db.add(secondary_admin)
        db.commit()

        # ==========================
        # 4️⃣ Crear Empleados
        # ==========================
        employees = []

        genders = [GenderEnum.FEMALE, GenderEnum.MALE]
        departments = list(DepartmentEnum)
        job_roles = list(JobRoleEnum)
        job_levels = list(JobLevelEnum)
        educations = list(EducationEnum)
        education_fields = list(EducationFieldEnum)
        marital_statuses = list(MaritalStatusEnum)

        for i in range(1, 9):
            user = UserModel(
                email=f"employee{i}@tech.com",
                password=hash_password("1234")
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            employee = EmployeeModel(
                user_id=user.id,
                company_id=company.id,
                first_name=f"Empleado{i}",
                last_name="Test",
                birth_date=date(1990, 1, i),
                gender=random.choice(genders).value,
                marital_status=random.choice(marital_statuses).value,
                department=random.choice(departments).value,
                education=random.choice(educations).value,
                education_field=random.choice(education_fields).value,
                job_level=random.choice(job_levels).value,
                job_role=random.choice(job_roles).value,
                monthly_salary=3000 + i * 500,
                percent_salary_hike=random.randint(5, 15)
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)
            employees.append(employee)

        # ==========================
        # 5️⃣ Crear Formularios
        # ==========================
        for idx, employee in enumerate(employees):
            high_risk = idx == 0  # Solo un empleado con alto riesgo para simular "isolated employee burnout"

            for week in range(4):  # 4 semanas
                created_date = date.today() - timedelta(days=7 * week)
                burnout_score = (
                    round(random.uniform(85, 100), 2) if high_risk
                    else round(random.uniform(20, 60), 2)
                )

                form = WeeklyBurnoutFormModel(
                    employee_id=employee.id,
                    written_feedback="Mucho estrés reciente" if high_risk else "Semana normal",
                    environment_satisfaction=1 if high_risk else 4,
                    overtime=1 if high_risk else 0,
                    job_involvement=4,
                    performance_rating=3,
                    job_satisfaction=1 if high_risk else 4,
                    work_life_balance=1 if high_risk else 4,
                    business_travel=2 if high_risk else 0,
                    burnout_score=str(burnout_score),
                    final_burnout_score=burnout_score,
                    created_at=created_date
                )
                db.add(form)

        db.commit()

    except Exception as e:
        db.rollback()
        print("❌ Error en seed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    run_development_seed()