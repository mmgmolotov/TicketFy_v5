from flask import Flask, render_template, request, send_file, redirect, url_for, make_response
from fpdf import FPDF
import os
from gunicorn.app.base import BaseApplication
from logging_config import configure_logging
import logging
from pdf2docx import Converter

app = Flask(__name__)

# Removed html_to_pdf function to reduce memory usage and replaced with direct template rendering

@app.route("/", methods=["GET"])
def root_route():
    return render_template('register_user.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form.get('full_name', '')
        phone_number = request.form.get('phone_number', '')
        gender = request.form.get('gender', '')
        # Ensure we always work with a dictionary
        users = load_users() or {}
        if username in users or email in [user['email'] for user in users.values()]:
            return render_template('register_user.html', message="Username or Email already exists"), 409
        # Save all the new information
        users[username] = {'password': password, 'email': email, 'full_name': full_name, 'phone_number': phone_number, 'gender': gender}
        save_users(users)
        # Redirect to login page after successful registration
        return redirect(url_for('login'))
    else:
        # If not POST, show the registration form again
        return render_template('register_user.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        users = load_users()  # Load users from the environment variable
        user = users.get(username)
        if user and user['password'] == password:
            message = "Login successful. Redirecting to ticket page..."
            response = make_response(redirect(url_for('ticket_route')))
            response.set_cookie('username', username)
            return response
        else:
            message = "Invalid username or password"
            return render_template('register_user.html', message=message), 401
    elif request.method == "GET":
        return render_template('register_user.html')
    else:
        return "Method Not Allowed", 405

@app.route("/logout", methods=["POST"])
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('username', '', expires=0)
    return response

@app.route("/register_user", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form.get('full_name', '')
        phone_number = request.form.get('phone_number', '')
        gender = request.form.get('gender', '')
        # Ensure we always work with a dictionary
        users = load_users() or {}
        if username in users or email in [user['email'] for user in users.values()]:
            return render_template('register_user.html', message="Username or Email already exists"), 409
        # Save all the new information
        users[username] = {'password': password, 'email': email, 'full_name': full_name, 'phone_number': phone_number, 'gender': gender}
        save_users(users)
        # Redirect to login page after successful registration
        return redirect(url_for('login'))
    else:
        # If not POST, show the registration form again
        return render_template('register_user.html')

@app.route("/admin", methods=["GET"])
def admin():
    if not request.cookies.get('username') == 'admin':
        return "Access Denied", 403
    users = load_users()
    return render_template('admin.html', users=users)

@app.route("/admin/edit", methods=["GET", "POST"])
def admin_edit():
    if request.method == "POST":
        username = request.form['username']
        new_name = request.form['new_name']
        new_email = request.form['new_email']
        new_password = request.form['new_password']
        users = load_users()
        if username in users:
            users[username]['name'] = new_name
            users[username]['email'] = new_email
            users[username]['password'] = new_password
            save_users(users)
            return "User details updated successfully", 200
        else:
            return "User not found", 404
    elif request.method == "GET":
        username = request.args.get('username')
        if username:
            return render_template('admin_edit_user.html', username=username)
        else:
            return "User not specified", 400
    else:
        return "Method Not Allowed", 405

@app.route("/admin/delete", methods=["GET"])
def admin_delete():
    if not request.cookies.get('username') == 'admin':
        return "Access Denied", 403
    username = request.args.get('username')
    users = load_users()
    if username in users:
        user_email = users[username]['email']  # Capture user email before deletion
        del users[username]
        save_users(users)
        # Delete user's purchase history
        tickets = load_tickets()
        tickets = [ticket for ticket in tickets if ticket['email'] != user_email]
        save_tickets(tickets)
        return redirect(url_for('admin'))
    else:
        app.logger.error(f"Attempted to delete non-existent user: {username}")
        return "User not found", 404

@app.route("/purchase_history", methods=["GET", "POST"])
def purchase_history():
    username = request.cookies.get('username')
    if username != 'admin':
        return "Access Denied", 403
    # Retrieve user's purchase history
    tickets = load_tickets()
    return render_template('purchase_history.html', tickets=tickets)

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

import json

# from abilities import key_value_storage
# The 'abilities' package is a special set of functions provided in the environment where your app runs.
# It's already available and can be used directly in your code without any additional import statements.
# The 'abilities' package is a special set of functions provided in the environment where your app runs.
# It's already available and can be used directly in your code without any additional import statements.

# Example Python native approach for load_users and save_users functions
# These functions need to be adapted to work with your specific environment and requirements

def load_users():
    try:
        with open('users_data.json', 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}
    return users

def save_users(users):
    with open('users_data.json', 'w') as file:
        json.dump(users, file)

# Example Python native approach for load_tickets and save_tickets functions
# These functions need to be adapted to work with your specific environment and requirements

def load_tickets():
    try:
        with open('tickets_data.json', 'r') as file:
            tickets = json.load(file)
    except FileNotFoundError:
        tickets = []
    return tickets

def save_tickets(tickets):
    with open('tickets_data.json', 'w') as file:
        json.dump(tickets, file)

users = load_users()

@app.route("/ticket", methods=["GET", "POST"])
def ticket_route():
    if not request.cookies.get('username'):
        return redirect(url_for('login'))
    return render_template('ticket.html')

if __name__ == "__main__":
    configure_logging()
    options = {"bind": "%s:%s" % ("0.0.0.0", "8080"), "workers": 4, "loglevel": "info"}
    StandaloneApplication(app, options).run()
