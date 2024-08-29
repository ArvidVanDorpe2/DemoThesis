from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import mysql.connector

app = Flask(__name__)

db_config = {
    'user': 'root',
    'password': '************',
    'host': 'localhost',
    'database': 'ehr_db'  # replace with your actual database name
}

# Configure the API to point to your locally running LM Studio server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Database schema to provide context for the model
schema = """
-- Create Patients Table
CREATE TABLE Patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    blood_type ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'),
    phone_number VARCHAR(15),
    email VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    emergency_contact_name VARCHAR(100),
    emergency_contact_relationship VARCHAR(50),
    emergency_contact_phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Medical Conditions Table
CREATE TABLE MedicalConditions (
    condition_id INT PRIMARY KEY AUTO_INCREMENT,
    condition_name VARCHAR(100),
    description TEXT
);

-- Create Diagnoses Table
CREATE TABLE Diagnoses (
    diagnosis_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    condition_id INT,
    diagnosis_date DATE,
    diagnosed_by VARCHAR(100),
    severity ENUM('Mild', 'Moderate', 'Severe'),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (condition_id) REFERENCES MedicalConditions(condition_id)
);

-- Create Medications Table
CREATE TABLE Medications (
    medication_id INT PRIMARY KEY AUTO_INCREMENT,
    medication_name VARCHAR(100),
    description TEXT,
    dosage VARCHAR(50),
    side_effects TEXT
);

-- Create Prescriptions Table
CREATE TABLE Prescriptions (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    medication_id INT,
    prescribed_by VARCHAR(100),
    dosage_instructions VARCHAR(255),
    start_date DATE,
    end_date DATE,
    refillable BOOLEAN,
    refills_left INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (medication_id) REFERENCES Medications(medication_id)
);

-- Create Allergies Table
CREATE TABLE Allergies (
    allergy_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    substance VARCHAR(100),
    reaction VARCHAR(100),
    severity ENUM('Mild', 'Moderate', 'Severe'),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Create Surgeries Table
CREATE TABLE Surgeries (
    surgery_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    surgery_name VARCHAR(100),
    surgeon_name VARCHAR(100),
    surgery_date DATE,
    outcome ENUM('Successful', 'Complications', 'Failed'),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Create Immunizations Table
CREATE TABLE Immunizations (
    immunization_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    vaccine_name VARCHAR(100),
    vaccine_date DATE,
    administered_by VARCHAR(100),
    dosage VARCHAR(50),
    booster_required BOOLEAN,
    booster_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Create Lab Tests Table
CREATE TABLE LabTests (
    lab_test_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    test_name VARCHAR(100),
    test_date DATE,
    ordered_by VARCHAR(100),
    results TEXT,
    result_date DATE,
    status ENUM('Pending', 'Completed', 'Abnormal'),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Create Visits Table
CREATE TABLE Visits (
    visit_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    visit_date DATE,
    reason_for_visit VARCHAR(255),
    doctor_seen VARCHAR(100),
    diagnosis_id INT,
    notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (diagnosis_id) REFERENCES Diagnoses(diagnosis_id)
);

-- Create Health Insurance Table
CREATE TABLE HealthInsurance (
    insurance_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    provider_name VARCHAR(100),
    policy_number VARCHAR(50),
    group_number VARCHAR(50),
    plan_type ENUM('HMO', 'PPO', 'EPO', 'POS'),
    coverage_start_date DATE,
    coverage_end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Create Billing Table
CREATE TABLE Billing (
    billing_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    visit_id INT,
    insurance_id INT,
    amount DECIMAL(10, 2),
    billing_date DATE,
    due_date DATE,
    status ENUM('Paid', 'Pending', 'Overdue'),
    payment_method ENUM('Credit Card', 'Debit Card', 'Cash', 'Insurance', 'Bank Transfer'),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (visit_id) REFERENCES Visits(visit_id),
    FOREIGN KEY (insurance_id) REFERENCES HealthInsurance(insurance_id)
);

-- Create Doctors Table
CREATE TABLE Doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    specialty VARCHAR(100),
    phone_number VARCHAR(15),
    email VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create Doctor Assignments Table
CREATE TABLE DoctorAssignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    doctor_id INT,
    assigned_date DATE,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)
);

-- Create Family History Table
CREATE TABLE FamilyHistory (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    relationship VARCHAR(50),
    condition_id INT,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (condition_id) REFERENCES MedicalConditions(condition_id)
);

-- Create Lifestyle Table
CREATE TABLE Lifestyle (
    lifestyle_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    smoking_status ENUM('Never', 'Former', 'Current'),
    alcohol_use ENUM('Never', 'Occasional', 'Regular'),
    exercise_frequency ENUM('None', 'Rarely', 'Weekly', 'Daily'),
    diet VARCHAR(255),
    occupation VARCHAR(100),
    stress_level ENUM('Low', 'Moderate', 'High'),
    sleep_hours_per_night DECIMAL(3,1),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);

-- Create Patient Documents Table
CREATE TABLE PatientDocuments (
    document_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    document_type VARCHAR(50),
    document_path VARCHAR(255),
    upload_date DATE,
    uploaded_by VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
);
"""


# Function to generate SQL queries based on user input
def generate_sql_query(user_question):
    prompt = f"""
### Task
Generate a SQL query only using the Database Schema provided to answer the following question. **You must use only the tables and columns listed in the schema. Do not invent or assume any additional tables, columns, or relationships.** to answer [QUESTION]{user_question}[/QUESTION] If the schema does not provide the necessary information to answer the question, state that it cannot be answered with the given schema.


### Database Schema
The query will run on a database with the following schema, **DO NOT INVENT NEW TABLES**
Given the database schema, here is the SQL query that answers the following question: [QUESTION]{user_question}[/QUESTION]. Make sure to use only the tables and columns listed above and provide a valid SQL query. If the question cannot be answered with the given schema, respond with "The question cannot be answered with the provided schema.":
{schema}

### Answer
Given the database schema, here is the SQL query that [QUESTION]{user_question}[/QUESTION]
[SQL]
"""

    history = [{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model="MaziyarPanahi/sqlcoder-7b-2-GGUF",
        messages=history,
        temperature=0.1
    )

    return response.choices[0].message.content


def execute_sql_query(sql_query):
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute the SQL query
        cursor.execute(sql_query)
        if cursor.with_rows:
            results = cursor.fetchall()
            # Prepare the results in a readable format
            result_data = [list(row) for row in results]
        else:
            connection.commit()
            result_data = "Query executed successfully, but there is no output."

        cursor.close()
        connection.close()

        return result_data

    except mysql.connector.Error as err:
        return f"Error: {err}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.form['question']
    sql_query = generate_sql_query(user_question)

    # Execute the generated SQL query
    if sql_query.strip().lower().startswith("the question cannot be answered"):
        result = sql_query
    else:
        result = execute_sql_query(sql_query)

    return jsonify({'sql_query': sql_query, 'result': result})


if __name__ == '__main__':
    app.run(debug=True)