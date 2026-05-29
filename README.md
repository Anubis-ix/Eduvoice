EduVoice Kenya 🎓
A multi-tenant school feedback and CRM platform aligned to Kenya's Competency-Based Curriculum (CBC). Students reflect on their learning, teachers receive anonymous aggregated feedback, parents track their child's engagement, and school admins get a CRM analytics dashboard — all scoped per school for SaaS deployment.

What It Does
For Students (Grades 1–9)

End-of-term review for each subject and teacher (5 dimensions, fully anonymous to teachers)
Values & skills self-rating: reading for pleasure, asking why, public speaking, adult interaction, teamwork, environmental care
Positive CBC framing — reviews ask "what did you love?" and "what made you curious?" rather than complaint forms
For Teachers

Aggregated anonymous feedback per subject/class (no individual student names ever shown)
Open-text student comments collected and displayed thematically
Self-assessment form: syllabus coverage, student engagement, values integration, next-term goals
For Parents

Per-child report showing subject ratings and soft skill self-ratings
View child's open-text reflections ("what they found interesting")
Leave an encouraging note for the child
For School Admins (CRM Dashboard)

School-wide participation rates and review counts
Subject enjoyment rankings across classes
Soft skill averages across the school
Teacher clarity ratings (only visible to admin, never to other teachers)
Semester management with review period open/close toggle
Tech Stack
Backend: Python 3.12, Django 6
Database: SQLite (dev) — swap to PostgreSQL for production
Frontend: Vanilla HTML/CSS, no JS framework required
Auth: Django's built-in auth with a custom User model (4 roles)
Multi-tenancy: Every query scoped by School — ready to sell to multiple schools
CBC Alignment
Subjects seeded from the KICD Basic Education Curriculum Framework (2019) and the KICD Senior School development documents:

Primary (Grades 1–6): English, Kiswahili, Mathematics, Environmental Activities, Creative Activities, Science & Technology, Agriculture, Social Studies, Home Science, Physical Education, Religious Education

Junior School (Grades 7–9): English, Kiswahili/KSL, Mathematics, Integrated Science, Pre-Technical Studies, Social Studies, Religious Education, Agriculture, Creative Arts & Sports, Business Studies, Health Education

Project Structure
educrm/
├── core/               Django project settings + root URLs
├── accounts/           Custom User model (student/teacher/parent/admin roles)
├── schools/            School, ClassRoom, Enrollment, TeacherAssignment, ParentStudentLink
├── curriculum/         Subject (CBC-aligned), SoftSkill
├── reviews/            Semester, Review, SoftSkillRating, TeacherSelfAssessment, ParentAcknowledgement
├── dashboard/          Role-routed dashboard views + admin CRM analytics
├── templates/          All HTML templates (base layout + per-role pages)
├── static/             CSS + JS assets
├── seed.py             Demo data: 2 schools, 22 subjects, 6 soft skills, users, classrooms
└── manage.py
Quick Start
git clone https://github.com/Anubis-ix/EduVoice-Kenya.git
cd EduVoice-Kenya

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python seed.py
python manage.py runserver
Open http://127.0.0.1:8000

Demo Credentials
Role	Username	Password
Superadmin	superadmin	Admin1234!
School Admin	admin.nairobi	Pass1234!
Teacher	ms.wanjiku	Pass1234!
Teacher	mr.odhiambo	Pass1234!
Student (Grade 5A)	jane.mwangi	Pass1234!
Student (Grade 7B)	amina.hassan	Pass1234!
Parent	parent.mwangi	Pass1234!
Key Design Decisions
Anonymity is enforced at the view layer. Teachers only see aggregated averages and anonymous quotes — never individual student identities. School admins see individual data for safeguarding purposes only.

Review period is admin-controlled. The Semester.review_open flag is toggled by the school admin (via Django admin or future UI). Students can only submit when a semester is open.

Multi-tenant from day one. Every model is scoped to a School. Adding a new school is a single record — no code changes. subscription_plan (free/basic/pro) is the CRM monetisation hook.

Soft skills are a first-class feature. The six skills — reading for pleasure, asking why, public speaking, adult interaction, teamwork, environmental care — are tracked as SoftSkill records, separately from academic subject reviews. These feed directly into the parent report and admin dashboard.

Roadmap
 Email notifications when review period opens
 PDF report export for parents
 School admin semester management UI (currently via Django admin)
 Multi-language support (English + Kiswahili)
 Progressive Web App (PWA) for mobile-first student experience
 API endpoints for school management system integrations
License
MIT
