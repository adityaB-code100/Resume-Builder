# insert_dummy_data.py

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random

# --- SQLAlchemy Setup ---
Base = declarative_base()

class ResumeAnalysis(Base):
    __tablename__ = 'resume_analysis'
    id = Column(Integer, primary_key=True)
    job_title = Column(String(100))
    company_name = Column(String(100))
    location = Column(String(100))
    company_address = Column(String(200))
    salary = Column(String(50))
    experience = Column(String(50))
    skills_required = Column(Text)
    resume_skills = Column(Text)
    match_score = Column(String(10))
    profile_summary = Column(Text)

# --- Database ---
engine = create_engine("sqlite:///resume_ats.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# --- Dummy Data ---
job_titles = ["Software Engineer", "Data Analyst", "Web Developer", "AI Engineer", "Backend Developer"]
companies = ["TechNova", "InnoWave", "DataSense", "CodeCraft", "NextGenSoft"]
locations = ["Mumbai", "Pune", "Bangalore", "Delhi", "Hyderabad"]
skills_pool = ["Python", "SQL", "Java", "Machine Learning", "HTML", "CSS", "React", "Flask"]

def generate_dummy_record(i):
    return ResumeAnalysis(
        job_title=random.choice(job_titles),
        company_name=f"{random.choice(companies)} {i}",
        location=random.choice(locations),
        company_address=f"{random.randint(101,999)} Main Street, {random.choice(locations)}",
        salary=f"{random.randint(5, 20)} LPA",
        experience=f"{random.randint(1, 5)}+ years",
        skills_required=", ".join(random.sample(skills_pool, 4)),
        resume_skills="",
        match_score="",
        profile_summary=""
    )

# --- Insert 100 Records ---
def insert_dummy_data():
    db = SessionLocal()
    dummy_records = [generate_dummy_record(i) for i in range(100)]
    db.bulk_save_objects(dummy_records)
    db.commit()
    db.close()
    print("✅ Inserted 100 dummy job entries into the database.")

if __name__ == "__main__":
    insert_dummy_data()
