# Group-E Healthcheck

A Django-based web platform for **engineering team health assessments**—gather real-time feedback, visualize team health trends, and drive improvement. Built for engineering teams, line managers, and department leaders.

![Group-E Healthcheck Dashboard Screenshot](screenshots/dashboard.png) <!-- Replace with actual screenshot path if desired -->

---

## Features

- **User Registration & Login**: Secure signup, role-based authentication (Engineer, Team Leader, Department Leader, Senior Manager).
- **Health Check Voting**: Submit and track votes across 10 team health dimensions (e.g., Code Quality, Collaboration, Stakeholder Communication, etc.).
- **Interactive Dashboards**: View aggregated team and department health metrics. Analyze results with tables and charts.
- **Admin Management**: Django admin for managing users, teams, sessions, votes, and departments.
- **Password Reset**: Secure workflow for forgotten passwords.
- **Responsive Design**: Modern, mobile-friendly UI using custom CSS and FontAwesome icons.

---

## Quick Start

### 1. Clone the repository:

```bash
git clone https://github.com/<IBwarsame>/Group-E-Healthcheck.git
cd Group-E-Healthcheck
```

### 2. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Django (and any other required packages):

```bash
pip install django
# pip install -r requirements.txt   # If you create one
```

### 4. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (for `/admin`):

```bash
python manage.py createsuperuser
```

### 6. Run the development server:

```bash
python manage.py runserver
```

App is available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Screenshots

*(Add your own screenshots in a `/screenshots` folder and display them here)*

- ![Login Page](login%20page.png)
- ![Home Page](home%20page.png)
- ![Profile Page](profile%20page.png)
- ![Health Check](health%20check%20page.png)
- ![Dashboard](dashbaord%20page.png)

---

## Project Structure

```plaintext
Group-E-Healthcheck/
├── GroupEHealthcheck/         # Django project settings
├── healthcheck/               # Main Django app
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   └── ...
├── manage.py
├── db.sqlite3                 # (Created after migrate)
├── venv/                      # Virtual environment (do NOT commit!)
└── screenshots/               # (Your screenshots here)
```

---

## Main Technologies

- **Python 3.11**
- **Django 5.x**
- SQLite (dev, easy setup)
- Custom CSS & FontAwesome Icons

---

## How to Add Data

- Access the admin at `/admin` using your superuser to create Departments, Teams, Sessions, and Users.
- Or use the web UI’s **Register** page to create new users (with automatic UserProfile setup).
- Sample data can be scripted with included `populate` scripts if provided.

---

## Credits

- Developed by Oliver Bryan, Smaran Holkar, Aaron Madhok, Michael Robinson, Ibrahim Warsame
- FontAwesome Icons, Select2 (where applicable)
- Demo logo/images: © Sky

---

## License

This project is licensed under the MIT License.  
See `LICENSE` files for third-party tools (Select2, FontAwesome SVGs, etc).

---

## Contact

Want to see more? Reach out on [LinkedIn](https://www.linkedin.com/) or by email!  
**Portfolio/brochure/demo available on request.**

---
