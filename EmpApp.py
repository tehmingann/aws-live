from flask import Flask, render_template, request, redirect, url_for, flash
from pymysql import connections
import os
import boto3
import pymysql
from config import *
from flaskext.mysql import MySQL

app = Flask(__name__)
app.secret_key = "nning00"

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
mysql = MySQL()
   
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'aws_user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Bait3273'
app.config['MYSQL_DATABASE_DB'] = 'employee'
app.config['MYSQL_DATABASE_HOST'] = 'employee.crhpyun5diaf.us-east-1.rds.amazonaws.com'
mysql.init_app(app)

output = {}
table = 'employee'


@app.route("/")
def Index():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
 
    cur.execute('SELECT * FROM employee')
    data = cur.fetchall()
  
    cur.close()
    return render_template('AddEmp.html', employee = data)


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, ContentType= "image/jpeg", Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    flash('Employee Added successfully')
    return redirect(url_for('Index'))

@app.route('/edit/<emp_id>', methods = ['POST', 'GET'])
def get_employee(emp_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
  
    cur.execute('SELECT * FROM employee WHERE emp_id = %s', (emp_id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', employee = data[0])
 
@app.route('/update/<emp_id>', methods=['POST'])
def update_employee(emp_id):
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            UPDATE employee
            SET first_name = %s,
                last_name = %s,
                pri_skill = %s,
                location = %s
            WHERE emp_id = %s
        """, (first_name, last_name, pri_skill, location, emp_id))
        flash('Employee Updated Successfully')
        conn.commit()
        return redirect(url_for('Index'))
 
@app.route('/delete/<string:emp_id>', methods = ['POST','GET'])
def delete_employee(emp_id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
  
    cur.execute('DELETE FROM employee WHERE emp_id = {0}'.format(emp_id))
    conn.commit()
    flash('Employee Removed Successfully')
    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
