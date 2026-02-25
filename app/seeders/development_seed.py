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
    if settings.ENV != "development":
        print("Seeder solo permitido en entorno development")
        return

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
            password=hash_password("1234")
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
            password=hash_password("1234")
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
                gender=random.choice(genders).name,
                marital_status=random.choice(marital_statuses).name,
                department=random.choice(departments).name,
                education=random.choice(educations).name,
                education_field=random.choice(education_fields).name,
                job_level=random.choice(job_levels).name,
                job_role=random.choice(job_roles).name,
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
            high_risk = idx >= 5  # últimos 3 empleados con alto riesgo

            for week in range(4):  # 4 semanas
                created_date = date.today() - timedelta(days=7 * week)
                burnout_score = (
                    round(random.uniform(75, 95), 2) if high_risk
                    else round(random.uniform(20, 60), 2)
                )

                form = WeeklyBurnoutFormModel(
                    employee_id=employee.id,
                    written_feedback="Mucho estrés reciente" if high_risk else "Semana normal",
                    environment_satisfaction="Low" if high_risk else "High",
                    overtime="Yes" if high_risk else "No",
                    job_involvement="High",
                    performance_rating="Medium",
                    job_satisfaction="Low" if high_risk else "High",
                    work_life_balance="Poor" if high_risk else "Good",
                    business_travel="Frequent" if high_risk else "Rare",
                    burnout_score=burnout_score,
                    created_at=created_date
                )
                db.add(form)

        db.commit()

        print("✅ Development Seed completado correctamente.")
        print("📌 Admin principal: admin@tech.com / Admin123")
        print("📌 Admin secundario: hr@tech.com / Admin123")
        print("📌 Empleados: employee1@tech.com - Employee123")

    except Exception as e:
        db.rollback()
        print("❌ Error en seed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    run_development_seed()