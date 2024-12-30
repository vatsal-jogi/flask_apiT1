import csv
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# File to store data
DATA_FILE = 'data.csv'

# Load data from CSV file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='r', newline='') as f:
            reader = csv.DictReader(f)
            return [dict(record) for record in reader]
    return []

# Save data to CSV file
def save_data(data):
    with open(DATA_FILE, mode='w', newline='') as f:
        fieldnames = ['ID', 'Name', 'Email', 'Phone']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Load initial data
data = load_data()

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/add_record', methods=['POST'])
def add_record():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    new_record = {'ID': len(data) + 1, 'Name': name, 'Email': email, 'Phone': phone}
    data.append(new_record)
    save_data(data)  # Save data to file
    return redirect(url_for('index'))

@app.route('/edit_record/<int:id>', methods=['POST'])
def edit_record(id):
    for record in data:
        if record['ID'] == id:
            record['Name'] = request.form['name']
            record['Email'] = request.form['email']
            record['Phone'] = request.form['phone']
            break
    save_data(data)  # Save data to file
    return redirect(url_for('index'))

@app.route('/delete_record/<int:id>', methods=['POST'])
def delete_record(id):
    global data
    data = [record for record in data if record['ID'] != id]
    
    # Reassign IDs to maintain sequential order
    for index, record in enumerate(data):
        record['ID'] = index + 1  # IDs start from 1
    
    save_data(data)  # Save data to file
    return redirect(url_for('index'))

# API Endpoints
@app.route('/api/records', methods=['GET'])
def get_records():
    # Get the fields query parameter (comma-separated list of fields)
    fields = request.args.get('fields')

    if fields:
        # Split the comma-separated list of fields and strip any extra spaces
        fields = [field.strip() for field in fields.split(',')]
        
        # Only include the requested fields for each record
        filtered_data = []
        for record in data:
            filtered_record = {field: record[field] for field in fields if field in record}
            filtered_data.append(filtered_record)

        return jsonify(filtered_data)
    
    # If no 'fields' query parameter is provided, return all fields
    return jsonify(data)



@app.route('/api/records', methods=['POST'])
def api_add_record():
    new_record = request.json
    new_record['ID'] = len(data) + 1
    data.append(new_record)
    save_data(data)  # Save data to file
    return jsonify(new_record), 201

@app.route('/api/records/<int:id>', methods=['PUT'])
def api_edit_record(id):
    for record in data:
        if record['ID'] == id:
            record.update(request.json)
            save_data(data)  # Save data to file
            return jsonify(record)
    return jsonify({'error': 'Record not found'}), 404

@app.route('/api/records/<int:id>', methods=['DELETE'])
def api_delete_record(id):
    global data
    data = [record for record in data if record['ID'] != id]
    
    # Reassign IDs to maintain sequential order
    for index, record in enumerate(data):
        record['ID'] = index + 1  # IDs start from 1
    
    save_data(data)  # Save data to file
    return jsonify({'result': 'Record deleted'}), 204

if __name__ == '__main__':
    app.run(debug=True)