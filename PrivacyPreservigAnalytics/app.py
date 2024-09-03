from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import os
import csv
import secrets 
import pandas as pd
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Create patient_details.csv file if not exists
if not os.path.exists('patient_details.csv'):
    with open('patient_details.csv', 'w', newline='') as csvfile:
        fieldnames = ['username', 'full_name', 'age', 'gender', 'phone_number', 'blood_group', 'address','disease']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

if not os.path.exists('doctor_details.csv'):
    with open('doctor_details.csv', 'w', newline='') as csvfile:
        fieldnames = ['username', 'full_name', 'age', 'specialization', 'experience', 'education']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def save_to_csv(data, filename):
    fieldnames = ['username', 'password', 'phoneNumber', 'role']  # Remove 'specialization' from fieldnames
    if data.get('role') == 'doctor':  # Add 'specialization' to fieldnames if provided in data
        fieldnames.append('specialization')
    
    # Ensure that data only contains serializable types
    data = {k: v for k, v in data.items() if isinstance(v, (int, float, str))}

    # Check if the file exists and is empty
    file_exists = os.path.exists(filename)
    file_empty = file_exists and os.path.getsize(filename) == 0

    # Open the CSV file in append mode and write the data
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file is empty
        if not file_exists or file_empty:
            writer.writeheader()

        # Check if the user is a doctor or patient and save accordingly
        if data.get('role') == 'doctor':
            filename = 'doctor.csv'
        elif data.get('role') == 'patient':
            filename = 'patient.csv'

        writer.writerow(data)

# Function to load user data from CSV files
def load_users():
    users = []
    filenames = ['patient.csv', 'doctor.csv', 'admin.csv']
    for filename in filenames:
        if os.path.exists(filename):
            with open(filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                users.extend([row for row in reader])
    return users

'''
# Function to save appointment data to CSV file
def save_appointment_to_csv(data):
    with open('appointments.csv', 'a', newline='') as csvfile:
        fieldnames = ['name', 'age', 'disease', 'gender', 'date', 'time', 'phone_number','doctor_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat('appointments.csv').st_size == 0:
            writer.writeheader()
        writer.writerow(data)
'''
def save_appointment_to_csv(appointment_data):
    fieldnames = ['name', 'age', 'disease', 'gender', 'date', 'time', 'phone_number', 'doctor_name']
    with open('appointments.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(appointment_data)

# Function to save personal details to CSV file
def save_personal_details_to_csv(data):
    with open('patient_details.csv', 'a', newline='') as csvfile:
        fieldnames = ['username', 'full_name', 'age', 'gender', 'phone_number', 'blood_group', 'address','disease']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat('patient_details.csv').st_size == 0:
            writer.writeheader()
        writer.writerow(data)

# Function to load personal details from CSV file
def load_personal_details(username):
    personal_details = []
    with open('patient_details.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username:
                personal_details.append(row)
    return personal_details

@app.route('/patient_personal_details', methods=['GET', 'POST'])
def patient_personal_details():
    if request.method == 'POST':
        if 'user' in session:
            user = session['user']
            full_name = request.form['full_name']
            age = request.form['age']
            gender = request.form['gender']
            phone_number = request.form['phone_number']
            blood_group = request.form['blood_group']
            address = request.form['address']
            disease = request.form['disease']
            
            # Save the personal details to CSV
            personal_data = {'username': user['username'], 'full_name': full_name, 'age': age, 'gender': gender,
                             'phone_number': phone_number, 'blood_group': blood_group, 'address': address, 'disease':disease}
            save_personal_details_to_csv(personal_data)
            
            # Redirect to success page
            return redirect(url_for('personal_details_success'))
        else:
            return redirect(url_for('login'))
    else:
        if 'user' in session:
            user = session['user']
            # Load personal details if available
            personal_details = load_personal_details(user['username'])
            if personal_details:
                # If personal details exist, render the view_personal_details template
                return render_template('view_personal_details.html', user=user, personal_details=personal_details[0])
            else:
                # If no personal details exist, render the patient_personal_details template
                return render_template('patient_personal_details.html', user=user)
        else:
            return redirect(url_for('login'))

@app.route('/personal_details_success')
def personal_details_success():
    return render_template('personal_details_success.html')

@app.route('/edit_personal_details', methods=['GET', 'POST'])
def edit_personal_details():
    if 'user' in session:
        user = session['user']
        personal_details = load_personal_details(user['username'])
        if request.method == 'POST':
            if personal_details:
                # Update personal details with form data
                personal_details = personal_details[0]  # Assuming there's only one entry for each user
                personal_details['full_name'] = request.form['full_name']
                personal_details['age'] = request.form['age']
                personal_details['gender'] = request.form['gender']
                personal_details['phone_number'] = request.form['phone_number']
                personal_details['blood_group'] = request.form['blood_group']
                personal_details['address'] = request.form['address']
                personal_details['disease'] = request.form['disease']
                
                # Save the updated personal details to CSV
                with open('patient_details.csv', 'w', newline='') as csvfile:
                    fieldnames = ['username', 'full_name', 'age', 'gender', 'phone_number', 'blood_group', 'address','disease']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(personal_details)
                
                # Render the personal_details_success template with a success message
                return render_template('personal_details_success.html', message="Personal Details Updated Successfully!")
            else:
                return "Personal details not found."
        else:
            if personal_details:
                return render_template('edit_personal_details.html', user=user, personal_details=personal_details)
            else:
                return "Personal details not found."
    else:
        return redirect(url_for('login'))
    
@app.route('/view_personal_details', methods=['GET'])
def view_personal_details():
    if 'user' in session:
        user = session['user']
        personal_details = load_personal_details(user['username'])
        if personal_details:
            return render_template('view_personal_details.html', user=user, personal_details=personal_details[0])
        else:
            return "Personal details not found."
    else:
        return redirect(url_for('login'))

# Function to save doctor details to CSV file
def save_doctor_details_to_csv(data):
    with open('doctor_details.csv', 'a', newline='') as csvfile:
        fieldnames = ['username', 'full_name', 'age', 'specialization', 'experience', 'education']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat('doctor_details.csv').st_size == 0:
            writer.writeheader()
        writer.writerow(data)

# Function to load doctor details from CSV file
def load_doctor_details(username=None):
    doctors = []
    with open('doctor_details.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if username and row['username'] == username:
                return [row]
            doctors.append(row)
    if username:
        return []
    return doctors

@app.route('/get_doctors', methods=['GET'])
def get_doctors():
    disease = request.args.get('disease')
    doctors = load_doctor_details()
    filtered_doctors = [doc for doc in doctors if doc['specialization'].lower() == disease.lower()]
    return jsonify(filtered_doctors)

@app.route('/doctor_personal_details', methods=['GET', 'POST'])
def doctor_personal_details():
    if request.method == 'POST':
        if 'user' in session:
            user = session['user']
            full_name = request.form['full_name']
            age = request.form['age']
            specialization = request.form['specialization']
            experience = request.form['experience']
            education = request.form['education']
            
            # Save the doctor details to CSV
            doctor_data = {'username': user['username'], 'full_name': full_name, 'age': age, 'specialization': specialization,
                           'experience': experience, 'education': education}
            save_doctor_details_to_csv(doctor_data)
            
            # Redirect to success page
            return redirect(url_for('doctor_details_success'))
        else:
            return redirect(url_for('login'))
    else:
        if 'user' in session:
            user = session['user']
            # Load doctor details if available
            doctor_details = load_doctor_details(user['username'])
            if doctor_details:
                # If doctor details exist, render the view_doctor_details template
                return render_template('view_doctor_details.html', user=user, doctor_details=doctor_details[0])
            else:
                # If no doctor details exist, render the doctor_personal_details template
                return render_template('doctor_personal_details.html', user=user)
        else:
            return redirect(url_for('login'))

@app.route('/doctor_details_success')
def doctor_details_success():
    return render_template('doctor_details_success.html')

@app.route('/edit_doctor_details', methods=['GET', 'POST'])
def edit_doctor_details():
    if 'user' in session:
        user = session['user']
        doctor_details = load_doctor_details(user['username'])
        if request.method == 'POST':
            if doctor_details:
                # Update doctor details with form data
                doctor_details = doctor_details[0]  # Assuming there's only one entry for each user
                doctor_details['full_name'] = request.form['full_name']
                doctor_details['age'] = request.form['age']
                doctor_details['specialization'] = request.form['specialization']
                doctor_details['experience'] = request.form['experience']
                doctor_details['education'] = request.form['education']
                
                # Save the updated doctor details to CSV
                updated_doctors = load_doctor_details()
                with open('doctor_details.csv', 'w', newline='') as csvfile:
                    fieldnames = ['username', 'full_name', 'age', 'specialization', 'experience', 'education']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for doc in updated_doctors:
                        if doc['username'] == user['username']:
                            writer.writerow(doctor_details)
                        else:
                            writer.writerow(doc)
                
                # Render the doctor_details_success template with a success message
                return render_template('doctor_details_success.html', message="Doctor Details Updated Successfully!")
            else:
                return "Doctor details not found."
        else:
            if doctor_details:
                return render_template('edit_doctor_details.html', user=user, doctor_details=doctor_details[0])
            else:
                return "Doctor details not found."
    else:
        return redirect(url_for('login'))

@app.route('/view_doctor_details', methods=['GET'])
def view_doctor_details():
    if 'user' in session:
        user = session['user']
        doctor_details = load_doctor_details(user['username'])
        if doctor_details:
            return render_template('view_doctor_details.html', user=user, doctor_details=doctor_details[0])
        else:
            return "Doctor details not found."
    else:
        return redirect(url_for('login'))

doctor_details_df = pd.read_csv('doctor_details.csv')
@app.route('/get_doctor_details', methods=['GET'])
def get_doctor_details():
    doctor_name = request.args.get('doctorName')
    print('Requested doctor name:', doctor_name)  # Log the requested doctor name
    doctor_row = doctor_details_df[doctor_details_df['full_name'] == doctor_name].to_dict(orient='records')
    if doctor_row:
        print('Found doctor details:', doctor_row[0])  # Log the found doctor details
        return jsonify(doctor_row[0]) 
    else:
        print('Doctor not found')  # Log if doctor is not found
        return jsonify({"error": "Doctor not found"}), 404

@app.route('/new_appointment', methods=['GET', 'POST'])
def new_appointment():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        disease = request.form['disease']
        gender = request.form['gender']
        date = request.form['date']
        time = request.form['time']
        phone_number = request.form['phone_number']
        doctor_name = request.form['doctor_name']
        # Save the appointment details to CSV
        appointment_data = {'name': name, 'age': age, 'disease': disease, 'gender': gender, 'date': date, 'time': time, 'phone_number': phone_number, 'doctor_name': doctor_name}
        save_appointment_to_csv(appointment_data)
        
        # Redirect to the view appointments page
        return redirect(url_for('view_appointments'))
    
    return render_template('new_appointment.html')

@app.route('/')
def index():
    return render_template('index.html')

def load_appointments(name):
    appointments = []
    with open('appointments.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['name'] == name:
                appointments.append(row)
    return appointments

@app.route('/view_appointments')
def view_appointments():
    if 'user' in session:
        user = session['user']
        username = user['username']
        
        # Pass the username to load_appointments function
        user_appointments = load_appointments(username)
        
        return render_template('view_appointments.html', appointments=user_appointments)
    else:
        return redirect(url_for('login'))

@app.route('/cancel_appointment', methods=['GET', 'POST'])
def cancel_appointment():
    if request.method == 'POST':
        appointment_name = request.form['appointment_name']
        appointment_date = request.form['appointment_date']
        
        appointments = load_appointments(appointment_name)  # Pass appointment_name to load_appointments
        for appointment in appointments:
            if appointment['name'] == appointment_name and appointment['date'] == appointment_date:
                appointments.remove(appointment)
                with open('appointments.csv', 'w', newline='') as csvfile:
                    fieldnames = ['name', 'age', 'disease', 'gender', 'date', 'time', 'phone_number', 'doctor_name']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(appointments)
                return render_template('cancel_success.html', message='Appointment canceled successfully')
        return render_template('cancel_failed.html', error='Appointment not found')
    else:
        return render_template('cancel_appointment.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # print(request.form)
    # print(request.method)
    if request.method == 'POST':
        print(request.method)

        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phoneNumber']
        role = request.form['role']
        specialization = request.form.get('specialization')  # Get the specialization if provided
        
        # Save user details to the appropriate CSV file based on the role
        user = {'username': username, 'password': password, 'phoneNumber': phone_number, 'role': role}
        if role == 'doctor':
            user['specialization'] = specialization
        print(user)
        save_to_csv(user, f'{role}.csv')
        return render_template('register_success.html')
    
    return render_template('register.html')

def user_exists(username):
    # Check if the username exists in any of the CSV files
    filenames = ['doctor.csv', 'patient.csv']  # Add more filenames if needed
    for filename in filenames:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['username'] == username:
                    return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = request.args.get('message')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        users = load_users()  # You need to implement this function to load users from your database or file
        user = next((u for u in users if u['username'] == username and u['password'] == password and u['role'] == role), None)
        if user:
            session['user'] = user
            if role == 'doctor':
                specialization = request.form['specialization']
                if specialization:
                    return redirect(url_for('specialized_dashboard', specialization=specialization))
            else:
                return redirect(url_for('general_dashboard'))
        else:
            message = 'Invalid credentials.'
    return render_template('login.html', message=message)

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = session['user']
        role = user['role']
        specialization = user.get('specialization')
        if role == 'patient':
            return render_template('dashboard_patient.html', user=user)
        elif role == 'admin':
            return render_template('dashboard_admin.html', user=user)
        elif role == 'doctor':
            if specialization:
                return render_template(f'templates/doctor_dashboards/{specialization}_dashboard.html', user=user)        
                # Redirect to the login page if no specialization is set
            else:
                return redirect(url_for('login'))
    return redirect(url_for('login'))


@app.route('/dashboard')
def general_dashboard():
    # Render the general dashboard template
    return render_template('doctor_dashboard.html')

@app.route('/specialized_dashboard/<specialization>')
def specialized_dashboard(specialization):
    # Assuming the CSV file has a column named 'username'
    with open('doctor.csv', 'r') as file:
        reader = csv.DictReader(file)
        # For simplicity, let's assume there's only one row in the CSV file
        row = next(reader)
        username = row['username']

    # Pass the username variable to the template context
    return render_template(f'specialized_dashboards/{specialization}_dashboard.html', username=username)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            return render_template('reset_password.html', error='Passwords do not match')

        users = load_users()
        user_index = next((i for i, u in enumerate(users) if u['username'] == username), None)
        if user_index is not None:
            users[user_index]['password'] = new_password
            # Remove the 'specialization' field if it exists
            if 'specialization' in users[user_index]:
                del users[user_index]['specialization']
            with open('user.csv', 'w', newline='') as csvfile:
                fieldnames = ['username', 'password', 'phoneNumber', 'role']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for user in users:
                    # Remove 'specialization' field if it exists
                    if 'specialization' in user:
                        del user['specialization']
                    writer.writerow(user)
            return render_template('login.html', message='Password reset successful. Please log in with your new password.')
        else:
            return render_template('reset_password.html', error='User not found')

    return render_template('reset_password.html')

# Dictionary mapping diseases to example reports
disease_reports = {
    'Dental': "This is a dental report for the patient.",
    'Anesthesia': "This is an anesthesia report for the patient.",
    'Dermatology': "This is a dermatology report for the patient.",
    'Gynecology': "This is a gynecology report for the patient.",
    'Neurologist': "This is a neurology report for the patient.",
    'Medicine': "This is a medicine report for the patient.",
    'Surgery': "This is a surgery report for the patient."
}

def generate_report(disease):
    if disease == 'Dental':
        return "Patient underwent a dental examination. No major issues detected. Advised to maintain oral hygiene and schedule regular check-ups."
    elif disease == 'Anesthesia':
        return "Patient underwent a procedure under anesthesia. The procedure went smoothly with no complications. Recovery is expected to be quick."
    elif disease == 'Dermatology':
        return "Patient consulted for a skin condition. Diagnosis revealed a mild dermatological issue. Prescribed medication for treatment and advised to follow up if symptoms persist."
    elif disease == 'Gynecology':
        return "Patient visited for a routine gynecological examination. No abnormalities detected. Recommended follow-up visit in six months."
    elif disease == 'Neurologist':
        return "Patient presented with symptoms of a neurological disorder. Further diagnostic tests recommended to determine the cause. Referral to a neurologist for detailed evaluation."
    elif disease == 'Medicine':
        return "Patient visited for a general medical consultation. Overall health assessment indicates good health. Advised on lifestyle modifications to maintain well-being."
    elif disease == 'Surgery':
        return "Patient underwent a surgical procedure. Surgery was successful, and patient is currently recovering in stable condition. Post-operative care instructions provided."
    else:
        return "No specific report available for the selected disease."

@app.route('/view_reports')
def view_report():
    if 'user' in session:
        username = session['user']['username']

        # Load appointments from the CSV file
        appointments = load_appointments_from_csv()

        if username in appointments:
            chosen_disease = appointments[username]['disease']

            # Generate a report based on the chosen disease
            report = generate_report(chosen_disease)

            # Render the report template with the provided data
            return render_template('view_reports.html', username=username, report=report)
        else:
            return render_template('view_reports.html', username=username, report="No appointment data found.")
    else:
        return redirect(url_for('login'))

def load_appointments_from_csv():
    appointments = {}
    with open('appointments.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']  # Assuming 'name' corresponds to 'username' in your CSV
            appointments[name] = {'disease': row['disease']}
    return appointments

# Define the dictionary to map diseases to treatment costs
treatment_costs = {
    'Dental': 600,
    'Anesthesia': 600,
    'Dermatology': 600,
    'Gynecology': 600,
    'Neurology': 600,
    'Medicine': 400,
    'Surgery': 600
}

# Define the dictionary to map diseases to sample medicines and their costs
medicine_costs = {
    'Dental': [('Medicine 1', 100), ('Medicine 2', 100)],
    'Anesthesia': [('Medicine 3', 100), ('Medicine 4', 100)],
    'Dermatology': [('Medicine 5', 100), ('Medicine 6', 100)],
    'Gynecology': [('Medicine 7', 100), ('Medicine 8', 100)],
    'Neurology': [('Medicine 9', 100), ('Medicine 10', 100)],
    'Medicine': [('Medicine 11', 100), ('Medicine 12', 100)],
    'Surgery': [('Medicine 13', 100), ('Medicine 14', 100)]
}

# Define the route for generating bills
@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    if request.method == 'POST':
        if 'user' in session:
            patient_name = request.form['patient_name']
            disease = request.form['disease']

            # Calculate total treatment cost
            treatment_cost = treatment_costs[disease]

            # Calculate total medicine cost
            total_medicine_cost = sum([medicine[1] for medicine in medicine_costs[disease]])

            # Calculate total bill
            total_bill = treatment_cost + total_medicine_cost

            # Render the bill template with the provided data
            return render_template('bill.html', patient_name=patient_name, disease=disease, 
                                   treatment_cost=treatment_cost, medicine_costs=medicine_costs[disease], 
                                   total_bill=total_bill)
        else:
            return redirect(url_for('login'))
    return render_template('generate_bill.html')

# Function to generate a private key
def generate_private_key():
    # Generate a random token for the private key
    return secrets.token_urlsafe(16)

# Function to write private key to CSV file
def write_private_key_to_csv(username, private_key):
    with open('user_private_keys.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([username, private_key])

# Function to read private key from CSV file
def read_private_key_from_csv(username):
    with open('user_private_keys.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == username:
                return row[1]
    return None

# Function to verify username and password
def verify_password_function(username, password):
    # Load user details from the doctor.csv file
    with open('doctor.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return row['specialization']  # Return doctor's specialization
    return None

def verify_admin_password(username, password):
    # Load admin details from the admin.csv file
    with open('admin.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return True  # Return True if username and password match
    return False 

# Route to verify password and generate private key
@app.route('/verify_password', methods=['POST'])
def verify_password():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        specialization = verify_password_function(username, password)
        if specialization:
            # Check if the user already has a private key
            user_private_key = read_private_key_from_csv(username)
            if user_private_key:
                # If user already has a private key, return it
                session['private_key'] = user_private_key
                session['username'] = username  # Store username in session
                session['specialization'] = specialization  # Store specialization in session
                print(f"Logged in user: {username}, Specialization: {specialization}")  # Debug print
                return jsonify({'status': 'success', 'private_key': user_private_key})
            else:
                # Generate private key for the user
                private_key = generate_private_key()
                # Store private key in CSV file
                write_private_key_to_csv(username, private_key)
                session['private_key'] = private_key
                session['username'] = username  # Store username in session
                session['specialization'] = specialization  # Store specialization in session
                print(f"Logged in user: {username}, Specialization: {specialization}")  # Debug print
                return jsonify({'status': 'success', 'private_key': private_key})
        else:
            # Check if the user is an admin
            if verify_admin_password(username, password):
                # Generate private key for the admin
                private_key = generate_private_key()
                # Store private key in CSV file
                write_private_key_to_csv(username, private_key)
                session['private_key'] = private_key
                session['username'] = username  # Store username in session
                print(f"Logged in admin: {username}")  # Debug print
                return jsonify({'status': 'success', 'private_key': private_key})
            # If the user is neither a doctor nor an admin, return error
            return jsonify({'status': 'error', 'message': 'Incorrect username or password'})

# Route to retrieve private key for logged-in user
@app.route('/get_private_key', methods=['GET'])
def get_private_key():
    if 'username' in session and 'private_key' in session:
        username = session['username']
        print(f"Retrieving private key for user: {username}")  # Debug print
        private_key = read_private_key_from_csv(username)
        if private_key:
            return jsonify({'status': 'success', 'private_key': private_key , 'username' : username  })
        else:
            return jsonify({'status': 'error', 'message': 'Private key not found'})
    else:
        return jsonify({'status': 'error', 'message': 'User not logged in or private key not found'})

# Load the encrypted data
encrypted_data = pd.read_csv('encrypted_data.csv')

# Load the user private keys
user_private_keys = pd.read_csv('user_private_keys.csv')

# Function to decrypt patient details
def decrypt_patient_details(data, key):
    cipher_suite = Fernet(key)
    decrypted_data = {}
    for column in data.columns:
        if column == 'username':
            decrypted_data[column] = data[column]
        else:
            decrypted_data[column] = [cipher_suite.decrypt(value.encode()).decode() for value in data[column]]
    return pd.DataFrame(decrypted_data)

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Columns to encrypt (indexing starts from 0)
columns_to_encrypt = [1, 4, 6, 7]

# Function to encrypt data
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode()).decode()

# Function to decrypt data
def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

# Read the patient_details.csv file and encrypt sensitive columns
encrypted_patient_details = []
with open('patient_details.csv', 'r') as csvfile:
    csv_reader = csv.reader(csvfile)
    header = next(csv_reader)  # Read the header
    encrypted_patient_details.append(header)
    
    for row in csv_reader:
        encrypted_row = []
        for i, col in enumerate(row):
            if i in columns_to_encrypt:
                encrypted_row.append(encrypt_data(col))
            else:
                encrypted_row.append(col)
        encrypted_patient_details.append(encrypted_row)

# Write the encrypted data to encrypted_data.csv
with open('encrypted_data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerows(encrypted_patient_details)

print("Data encrypted and saved to encrypted_data.csv")
print("Encryption Key:", key.decode())

# Route to retrieve and decrypt patient details
@app.route('/get_patient_details', methods=['GET'])
def get_patient_details():
    if request.args.get('private_key'):
    # if 'username' in session and 'private_key' in session:
        print('kook1')
        username = session['username']
        print(username)
        print(request.args.get('username'))
        private_key = session['private_key']
        entered_private_key = request.args.get('private_key')
        #print('here', entered_private_key)
        

        # Check if the entered private key matches the user's private key
        if entered_private_key != private_key:
            decrypted_patient_details = []
            with open('encrypted_data.csv', 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                header = next(csv_reader)  # Skip the header
                for row in csv_reader:
                    decrypted_row = []
                    for i, col in enumerate(row):
                        if i in columns_to_encrypt:
                            decrypted_row.append('******')
                        else:
                            decrypted_row.append(col)
                    decrypted_patient_details.append(decrypted_row)
            return jsonify({'status': 'error', 'patient_details': decrypted_patient_details , 'message': 'Private key does not match the logged-in user\'s key.'})

            # return jsonify({'status': 'error', 'message': 'Private key does not match the logged-in user\'s key.'})

        # Read patient details from encrypted_data.csv
        decrypted_patient_details = []
        with open('encrypted_data.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)  # Skip the header
            for row in csv_reader:
                decrypted_row = []
                for i, col in enumerate(row):
                    if i in columns_to_encrypt:
                        decrypted_row.append(decrypt_data(col))
                    else:
                        decrypted_row.append(col)
                decrypted_patient_details.append(decrypted_row)

        return jsonify({'status': 'success', 'patient_details': decrypted_patient_details})
    else:
        print("##")
        decrypted_patient_details = []
        with open('encrypted_data.csv', 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)  # Skip the header
            for row in csv_reader:
                decrypted_row = []
                for i, col in enumerate(row):
                    if i in columns_to_encrypt:
                        decrypted_row.append('***********')
                    else:
                        decrypted_row.append(col)
                decrypted_patient_details.append(decrypted_row)
        return jsonify({'status': 'success', 'patient_details': decrypted_patient_details})

        # return jsonify({'status': 'success', 'message': 'User not logged in or private key not found,'patient_details': decrypted_patient_details })

'''
def get_doctor_specialization(username):
    with open('doctor.csv', 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            if row['username'] == username:
                return row['specialization']
    return None  # Return None if the doctor's specialization is not found
'''

# Route to check if the entered private key matches the user's private key
@app.route('/check_private_key', methods=['GET'])
def check_private_key():
    if 'username' in session and 'private_key' in session:
        entered_private_key = request.args.get('private_key')
        username = session['username']
        user_private_key = read_private_key_from_csv(username)  # Read the private key associated with the username

        if entered_private_key == user_private_key:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Private key does not match the logged-in user\'s key.'})
    else:
        return jsonify({'status': 'error', 'message': 'User not logged in or private key not found'})

if __name__ == '__main__':
    app.run(debug=True)