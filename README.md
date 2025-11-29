# Group-E Healthcheck

A Django-based web platform for **team health assessments**. Collect, visualize, and analyze team feedback to understand and improve engineering culture.

---

## Features

- User registration and authentication (roles: Engineer, Team Leader, Department Leader, Senior Manager)
- Submit health check votes across multiple team health metrics
- Interactive dashboards for team and department summaries
- Admin panel for managing all data
- Password reset via secure email workflow
- Responsive, modern UI (custom CSS + Font Awesome icons)

---

## Screenshots

| Login Page                            | Home Page                            |
|:--------------------------------------:|:-------------------------------------:|
| ![Login Page](screenshots/login%20page.png) | ![Home Page](screenshots/home%20page.png) |

| Profile Page                          | Health Check Voting                   |
|:--------------------------------------:|:-------------------------------------:|
| ![Profile Page](screenshots/profile%20page.png) | ![Health Check](screenshots/health%20check%20page.png) |

| Dashboard Page                        |
|:--------------------------------------:|
| ![Dashboard](screenshots/dashbaord%20page.png) |

---

## Quick Start

**1. Clone the repository:**

```bash
git clone https://github.com/<your-username>/Group-E-Healthcheck.git
cd Group-E-Healthcheck
```

**2. Set up a virtual environment and install Django:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install django
```

**3. Initialize the database:**

```bash
python manage.py makemigrations
python manage.py migrate
```

**4. Create a superuser (for /admin access):**

```bash
python manage.py createsuperuser
```

**5. Run the server:**

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## How to Use

- Use **/register** to sign up as a new user.
- Log in, view the dashboard, submit or view health checks.
- Visit **/admin** (as superuser) to manage users, teams, sessions, votes, and more.

---

## Tech Stack

- Python 3.11+
- Django 5.x
- SQLite (for development)
- HTML, CSS, Font Awesome for UI

---

## Contributors

- Oliver Bryan
- Smaran Holkar
- Aaron Madhok
- Michael Robinson
- Ibrahim Warsame

---

## License

MIT License for project code.
See included LICENSE files for third-party assets (Font Awesome, Select2, etc).

---

**Screenshots and code available for portfolio or recruiter review.**