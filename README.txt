CIVICCONNECT - HACKATHON STARTER PROJECT

FEATURES
- Submit a community issue with an optional photo
- Store reports in SQLite
- Track a complaint using its ID
- Admin login and dashboard
- Admin can update complaint status

REQUIREMENTS
- Python 3.10 or newer
- Internet connection only if you want the optional Google Fonts styling

RUN ON WINDOWS
1. Extract the CivicConnect.zip file.
2. Open the CivicConnect folder in VS Code.
3. Open Terminal > New Terminal.
4. Create a virtual environment (recommended):
   python -m venv venv
5. Activate it:
   venv\Scripts\activate
6. Install Flask:
   pip install -r requirements.txt
7. Start the app:
   python app.py
8. Open this address in your browser:
   http://127.0.0.1:5000

ADMIN DEMO LOGIN
Username: admin
Password: civic123
Open: http://127.0.0.1:5000/admin/login

HOW TO TEST
1. Open the home page and submit a sample issue.
2. Note the complaint ID shown on the success page.
3. Open Track Complaint and enter that ID.
4. Open the Admin page and log in.
5. Change the complaint status and save.
6. Return to Track Complaint and check the updated status.

IMPORTANT
- This is a hackathon demonstration prototype, not a production service.
- Change the demo admin password and SECRET_KEY before deployment.
- Add stronger authentication, CSRF protection, privacy controls and
  deployment security before using real personal information.
- Do not upload sensitive personal information during testing.
- The database file civicconnect.db is created automatically the first
  time you run the app.
