@echo off
cd C:\Users\Lucas Gabriel\Desktop\VirtualFlask\FLASK\
call venv\Scripts\activate
cd C:\Users\Lucas Gabriel\Desktop\VirtualFlask\FLASK\Python-Flask
start "" http://localhost:5000
flask --app app.py --debug run
