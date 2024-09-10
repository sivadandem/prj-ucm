from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = 'nothing'  # Replace with a secure, random key

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'SSSsss1@',
    'database': 'biher2024'
}

def create_connection():
    """Create a database connection."""
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/queryconfirmation')
def success():
    return render_template('queryconfirmation.html')

@app.route('/submit_query', methods=['POST'])
def submit_query():
    name = request.form['name']
    phonenumber = request.form['phonenumber']
    email = request.form['email']
    query = request.form['query']

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        sql = "INSERT INTO queries (name, phonenumber, email, query) VALUES (%s, %s, %s, %s)"
        val = (name, phonenumber, email, query)
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('success'))
    
    
#----------------------------------------------------------admin-----------------------------------------------------

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM admins WHERE email = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                session['username'] = user['username']  # Store the username in the session
                return redirect(url_for('adminportal'))
            else:
                return render_template('adminlogin.html', error="Invalid username or password.")

    return render_template('adminlogin.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('adminlogin'))  # Redirect to the admin login page

@app.route('/adminsignup', methods=['GET', 'POST'])
def adminsignup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        password = request.form['password']
        unicode = request.form['unicode']
        expected_unicode = 'biher2024admin'

        if unicode != expected_unicode:
            return render_template('adminsignup.html', error="Unicode does not match.")

        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO admins (username, email, phonenumber, password, unicode) VALUES (%s, %s, %s, %s, %s)",
                (username, email, phonenumber, password, unicode)
            )
            connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
            connection.close()
        
        return redirect(url_for('signupconfirmation'))
    
    return render_template('adminsignup.html')

@app.route('/signupconfirmation')
def signupconfirmation():
    return render_template('signupconfirmation.html')


@app.route('/adminportal')
def adminportal():
    username = session.get('username')  # Get the username from the session

    if not username:
        return redirect(url_for('adminlogin'))  # Redirect to login if the username is not in the session

    connection = create_connection()
    queries = []
    teacher_count = 0
    student_count = 0
    announcements_count=0
    queries_count=0
    

    if connection:
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM announcements")
        announcements_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM queries")
        queries_count = cursor.fetchone()[0]

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM queries")
        
        queries = cursor.fetchall()


        cursor.close()
        connection.close()

    return render_template('adminportal.html', 
                           queries=queries, 
                           teacher_count=teacher_count, 
                           student_count=student_count, 
                           username=username,announcements_count=announcements_count,queries_count=queries_count)


@app.route('/queriestable')
def queriestable():
    connection = create_connection()
    queries = []
    announcements = []


    if connection:
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM queries")
        
        queries = cursor.fetchall()

        # Fetch the announcements
        cursor.execute("SELECT title, message, timestamp FROM announcements ORDER BY timestamp DESC")
        announcements = cursor.fetchall()

        cursor.close()
        connection.close()

    return render_template('queriestable.html', 
                           queries=queries,announcements=announcements)
    
@app.route('/update_status/<int:query_id>', methods=['POST'])
def update_status(query_id):
    status = request.form['status']
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE queries SET status = %s WHERE slno = %s", (status, query_id))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('queriestable'))
    
    
@app.route('/delete_query/<query_id>', methods=['POST'])
def delete_query(query_id):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM queries WHERE slno = %s", (query_id,))
            connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()
    return redirect(url_for('queriestable'))
    
    
@app.route('/placementsportal')
def placementsportal():
    return render_template('placementsportal.html')

@app.route('/post_placement', methods=['POST'])
def post_placement():
    if 'username' in session:
        company_name = request.form['company_name']
        registration_link = request.form['registration_link']
        company_image = request.form['company_image']
        
        connection = create_connection()
        cursor = connection.cursor()

        # Ensure table exists
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS placements2024 (
            slno INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            registration_link TEXT NOT NULL,
            company_image TEXT NOT NULL
        )
        '''
        cursor.execute(create_table_query)

        # Insert the placement data
        insert_query = '''
        INSERT INTO placements2024 (company_name, registration_link, company_image)
        VALUES (%s, %s, %s)
        '''
        cursor.execute(insert_query, (company_name, registration_link, company_image))
        connection.commit()
        return redirect(url_for('view_placements'))
    else:
        return redirect(url_for('login'))
    
@app.route('/view_placements')
def view_placements():
    if 'username' in session:
        connection = create_connection()
        cursor = connection.cursor()

        # Fetch all placements
        select_query = 'SELECT * FROM placements2024'
        cursor.execute(select_query)
        placements = cursor.fetchall()

        return render_template('placementsportal.html', placements=placements)
    else:
        return redirect(url_for('adminlogin'))

  
@app.route('/post_announcement', methods=['POST'])
def post_announcement():
    title = request.form.get('title')
    message = request.form.get('message')
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO announcements (title, message) VALUES (%s, %s)", (title, message))
        connection.commit()
        cursor.close()
        connection.close()
    
    return redirect(url_for('adminportal'))

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    id = request.form['id']
    name = request.form['name']
    email = request.form['email']
    phonenumber = request.form['phonenumber']
    unicode = request.form['unicode']
    age = request.form.get('age')
    salary = request.form.get('salary')
    department = request.form.get('department')
    password = request.form.get('password')


    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        sql = """
        INSERT INTO teachers (id, name, email, phonenumber, unicode, age, salary, department, password) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (id, name, email, phonenumber, unicode, age, salary, department, password)
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('teacheraddedconfirmation'))
    return redirect(url_for('adminportal'))


    
@app.route('/teacheraddedconfirmation')
def teacheraddedconfirmation():
    return render_template('teacheraddedconfirmation.html')


@app.route('/delete_teacher/<string:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        sql = "DELETE FROM teachers WHERE id = %s"
        cursor.execute(sql, (teacher_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('view_teachers'))
    return redirect(url_for('adminportal'))



@app.route('/add_student', methods=['POST'])
def add_student():
    id = request.form['id']
    name = request.form['name']
    email = request.form['email']
    phonenumber = request.form['phonenumber']
    unicode = request.form['unicode']
    age = request.form.get('age')
    course = request.form.get('course')
    section = request.form.get('section')
    password = request.form.get('password')
    hostel=request.form.get('hostel')


    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        sql = """
        INSERT INTO students (id, name, email, phonenumber, unicode, age, course, section, password,hostel) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (id, name, email, phonenumber, unicode, age, course, section, password, hostel)
        cursor.execute(sql, val)
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('teacheraddedconfirmation'))
    return redirect(url_for('adminportal'))

@app.route('/view_teachers', methods=['GET', 'POST'])
def view_teachers():
    connection = create_connection()
    teachers = []
    if request.method == 'POST':
        filter_type = request.form['filter_type']
        filter_value = request.form['filter_value']
        
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            if filter_type == 'all':
                query = "SELECT * FROM teachers ORDER BY slno DESC"
                cursor.execute(query)
            elif filter_type == 'old data':
                query = "SELECT * FROM teachers ORDER BY slno ASC"
                cursor.execute(query)
            else:
                query = f"SELECT * FROM teachers WHERE {filter_type} LIKE %s"
                cursor.execute(query, ('%' + filter_value + '%',))
            
            teachers = cursor.fetchall()
            cursor.close()
            connection.close()

    return render_template('view_teachers.html', teachers=teachers)

@app.route('/view_students', methods=['GET', 'POST'])
def view_students():
    connection = create_connection()
    students = []
    if request.method == 'POST':
        # Get the filter criteria from the form
        filter_type = request.form['filter_type']
        filter_value = request.form['filter_value']
        
        # Query the database based on the filter
        if connection:
            cursor = connection.cursor(dictionary=True)
            if filter_type == 'all':
                query = "SELECT * FROM students ORDER BY slno DESC"
                cursor.execute(query)
                
            elif filter_type == 'old data':
                query = "SELECT * FROM students ORDER BY slno ASC"
                cursor.execute(query)
                
            elif filter_type == 'attendance':
                query = "SELECT * FROM students ORDER BY CAST(attendance AS UNSIGNED) ASC"
                cursor.execute(query)
            else:
                query = f"SELECT * FROM students WHERE {filter_type} LIKE %s"
                cursor.execute(query, ('%' + filter_value + '%',))

            students = cursor.fetchall()
            cursor.close()
            connection.close()

    return render_template('view_students.html', students=students)



@app.route('/view_teacher_leaves', methods=['GET', 'POST'])
def view_teacher_leaves():
    connection = create_connection()
    teachers = []

    if request.method == 'POST':
        filter_type = request.form['filter_type']
        filter_value = request.form['filter_value']
        cursor = connection.cursor(dictionary=True)
        if connection:
            cursor = connection.cursor(dictionary=True)
            if filter_type == 'all':
                query ='SELECT id, name, leave_status, leave_reason FROM teachers'
                cursor.execute(query)
            else:
                query = f"SELECT id, name, leave_status, leave_reason FROM teachers WHERE {filter_type} LIKE %s "
                cursor.execute(query, ('%' + filter_value + '%',))
        
        teachers = cursor.fetchall()
        cursor.close()
        connection.close()

    return render_template('teachersleave.html', teachers=teachers)



@app.route('/update_leave_status', methods=['POST'])
def update_leave_status():
    teacher_id = request.form['update']
    leave_status = request.form[f'leave_status_{teacher_id}']


    if leave_status == "Not Approved":
        leave_status = f"Not Approved"
    elif leave_status == "Approved":
        leave_status = f"Approved"

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE teachers SET leave_status = %s WHERE id = %s", (leave_status, teacher_id))
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('view_teacher_leaves'))

@app.route('/teacher/<string:teacher_id>')
def view_teacher_detail(teacher_id):
    connection = create_connection()
    teacher = None

    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teachers WHERE id = %s", (teacher_id,))
        teacher = cursor.fetchone()
        cursor.close()
        connection.close()

    if teacher:
        return render_template('teacher_details.html', teacher=teacher)
    else:
        return "Teacher not found", 404
    
@app.route('/student/<string:student_id>')
def view_student_detail(student_id):
    connection = create_connection()
    student = None

    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()  # Use student here, not teacher
        cursor.close()
        connection.close()

    if student:
        return render_template('student_details.html', student=student)
    else:
        return "Student not found", 404

        
#-----------------------------------------------------------------------------------------------------teacher-------------------------------------------------


@app.route('/teacherlogin', methods=['GET', 'POST'])
def teacherlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM teachers WHERE email = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                session['username'] = user['name']  # Store the username in the session
                return redirect(url_for('teacherportal'))
            else:
                return render_template('teacher_login.html', error="Invalid username or password.")

    return render_template('teacher_login.html')

@app.route('/teachersignup', methods=['GET', 'POST'])
def teachersignup():
    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        password = request.form['password']
        unicode = request.form['unicode']
        expected_unicode = 'biher2024admin'

        if unicode != expected_unicode:
            return render_template('teachersignup.html', error="Unicode does not match.")

        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute(
                "INSERT INTO teachers (id,name, email, phonenumber, password, unicode) VALUES (%s,%s, %s, %s, %s, %s)",
                (id,username, email, phonenumber, password, unicode)
            )
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('teachersignupconfirmation'))
    
    return render_template('teachersignup.html')

@app.route('/teachersignupconfirmation')
def teachersignupconfirmation():
    return render_template('teachersignupconfirmation.html')

@app.route("/teacherportal")
def teacherportal():
    
    username = session.get('username')  # Get the username from the session

    if not username:
        return redirect(url_for('teacherlogin'))

    connection = create_connection()

    student_count = 0
    announcements_count = 0
    announcements = []
    teacher_message = None
    message_timestamp = None

    if connection:
        cursor = connection.cursor()

        # Fetch student count
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]

        # Fetch announcements count
        cursor.execute("SELECT COUNT(*) FROM announcements")
        announcements_count = cursor.fetchone()[0]

        # Fetch announcements
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT title, message, timestamp FROM announcements ORDER BY timestamp DESC")
        announcements = cursor.fetchall()
        
        cursor.close()
        connection.close()

    return render_template("teacherportal.html",
                           student_count=student_count, 
                           username=username,
                           announcements=announcements,
                           announcements_count=announcements_count,
                           teacher_message=teacher_message,
                           message_timestamp=message_timestamp)
    
@app.route('/teacherlogout')
def teacherlogout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('teacherlogin'))  # Redirect to the admin login page


@app.route('/view_students_teacher', methods=['GET', 'POST'])
def view_students_teacher():
    connection = create_connection()
    students = []
    if request.method == 'POST':
        # Get the filter criteria from the form
        filter_type = request.form['filter_type']
        filter_value = request.form['filter_value']
        
        # Query the database based on the filter
        if connection:
            cursor = connection.cursor(dictionary=True)
            if filter_type == 'all':
                query = "SELECT * FROM students ORDER BY slno DESC"
                cursor.execute(query)
                
            elif filter_type == 'old data':
                query = "SELECT * FROM students ORDER BY slno ASC"
                cursor.execute(query)
                
            else:
                query = f"SELECT * FROM students WHERE {filter_type} LIKE %s"
                cursor.execute(query, ('%' + filter_value + '%',))

            students = cursor.fetchall()
            cursor.close()
            connection.close()

    return render_template('studentview_teacher.html', students=students)


@app.route("/todo_list")
def todo_list():
    username = session.get('username')
    if not username:
        return redirect(url_for('teacherlogin'))

    connection = create_connection()
    notes = []

    if connection:
        cursor = connection.cursor(dictionary=True)
        # Dynamically create the table if it doesn't exist
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{username}_notes` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `note` VARCHAR(255) NOT NULL,
                `date` DATE NOT NULL,
                `time_created` TIME NOT NULL
            )
        """)
        # Fetch notes
        cursor.execute(f"SELECT * FROM `{username}_notes` ORDER BY time_created DESC")
        notes = cursor.fetchall()
        cursor.close()
        connection.close()

    return render_template("todolist.html", notes=notes, username=username)

@app.route("/add_note", methods=["POST"])
def add_note():
    username = session.get('username')
    if not username:
        return redirect(url_for('teacherlogin'))

    note = request.form.get('note')
    date = datetime.now().strftime('%Y-%m-%d')
    time_created = datetime.now().strftime('%H:%M:%S')

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO `{username}_notes` (note, date, time_created) VALUES (%s, %s, %s)", (note, date, time_created))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('todo_list'))

@app.route("/delete_note/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('teacherlogin'))

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM `{username}_notes` WHERE id = %s", (note_id,))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('todo_list'))

@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    leave_reason = request.form['leave_reason']
    leave_start = request.form['leave_start']
    leave_end = request.form['leave_end']
    username = session.get('username')
    connection = create_connection()
    cursor = connection.cursor()
    query = """
        UPDATE teachers
        SET leave_reason = %s, leave_start = %s, leave_end = %s
        WHERE name = %s
        """
    cursor.execute(query, (leave_reason, leave_start, leave_end, username))
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('teacherportal'))



@app.route('/update_teacher', methods=['GET', 'POST'])
def update_teacher():
    if request.method == 'POST':
        teacher_id = request.form.get('id')
        name = request.form.get('name')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        age = request.form.get('age')
        department = request.form.get('department')
        password = request.form.get('password')
        
        # Fetch existing data
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM teachers WHERE id = %s", (teacher_id,))
            current_data = cursor.fetchone()
            cursor.close()
            
            # Prepare update data
            update_data = {}
            if name:
                update_data['name'] = name
            if email:
                update_data['email'] = email
            if phonenumber:
                update_data['phonenumber'] = phonenumber
            if age:
                update_data['age'] = age
            if department:
                update_data['department'] = department
            if password:
                update_data['password'] = password
            
            # Update only fields that were provided
            if update_data:
                update_query = "UPDATE teachers SET "
                update_query += ", ".join(f"{key} = %s" for key in update_data.keys())
                update_query += " WHERE id = %s"
                
                update_values = list(update_data.values()) + [teacher_id]
                
                try:
                    cursor = connection.cursor()
                    cursor.execute(update_query, update_values)
                    connection.commit()
                    
                    # Update the session with the new name (if updated)
                    if 'name' in update_data:
                        session['teacher_name'] = update_data['name']
                    
                except Error as e:
                    pass
                finally:
                    cursor.close()
                    connection.close()
        
        return redirect(url_for('teacherlogin'))
    return render_template('teacherlogin')



@app.route('/post_announcement_teacher', methods=['POST'])
def post_announcement_teacher():
    title = request.form['title']
    message = request.form['message']
    section_name = request.form['section_name']

    connection = create_connection()
    if connection is None:
        return redirect(url_for('teacherportal'))

    cursor = connection.cursor()
    try:
        table_name = f"{section_name}_announcements"
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()

        insert_query = f"""
        INSERT INTO `{table_name}` (title, message) 
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (title, message))
        connection.commit()
        
        
    except Error as e:
        pass
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('teacherportal'))



@app.route("/teacherannouncementtable")
def teacherannouncementtable():
    return render_template("teacherannouncements.html")

@app.route('/announcementtable', methods=['GET', 'POST'])
def announcementtable():
    connection = create_connection()

    announcements = []
    section_name = None

    if connection:
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'POST':
            section_name = request.form.get('section_name')
            if section_name:
                # Fetch the announcements from the specific section's table
                table_name = f"{section_name}_announcements"
                query = f"SELECT title, message, created_at FROM {table_name} ORDER BY created_at DESC"
                cursor.execute(query)
                announcements = cursor.fetchall()
        else:
            # Default query or handle GET request if needed
            pass

        cursor.close()
        connection.close()

    return render_template('teacherannouncements.html', announcements=announcements, section_name=section_name)



@app.route("/attendance")
def attendance():
    return render_template('mark_attendance.html')

@app.route('/get_students', methods=['POST'])
def get_students():
    section = request.form.get('section')
    date = request.form.get('date')
    
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT id, name, section FROM students WHERE section = %s"
    cursor.execute(query, (section,))
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('mark_attendance.html', students=students, date=date, section=section)

@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    date = request.form.get('date')
    section = request.form.get('section')

    # Format the table name based on section and year
    table_name = f"{section}_attendance2024"
    date_column = datetime.strptime(date, '%Y-%m-%d').strftime('%d%b%Y')  # Format the date for column name

    connection = create_connection()
    cursor = connection.cursor()

    # Create the table if it does not exist
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        student_id VARCHAR(50),
        PRIMARY KEY (student_id)
    )
    """
    cursor.execute(create_table_query)

    # Check if the column for the new date exists and add it if not
    check_column_query = f"""
    SHOW COLUMNS FROM {table_name} LIKE '{date_column}'
    """
    cursor.execute(check_column_query)
    column_exists = cursor.fetchone() is not None

    if not column_exists:
        add_column_query = f"""
        ALTER TABLE {table_name}
        ADD COLUMN `{date_column}` ENUM('present', 'absent')
        """
        cursor.execute(add_column_query)

    # Insert or update attendance records
    for student_id in request.form:
        if student_id.startswith('attendance_'):
            status = request.form.get(student_id)
            student_id = student_id.replace('attendance_', '')
            
            # Insert or update attendance in the attendance table
            update_query = f"""
                INSERT INTO {table_name} (student_id, {date_column})
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE {date_column} = VALUES({date_column})
            """
            cursor.execute(update_query, (student_id, status))

            # Fetch the current attendance percentage of the student
            cursor.execute("SELECT attendance FROM students WHERE id = %s", (student_id,))
            current_attendance = cursor.fetchone()[0]
            
            # Update the student's attendance percentage based on status
            if status == 'absent':
                new_attendance = max(0, int(current_attendance[:-1]) - 2)  # Reduce by 2%, but not below 0
            elif status == 'present' and current_attendance != '100%':
                new_attendance = min(100, int(current_attendance[:-1]) + 1)  # Increase by 1%, but not above 100
            else:
                new_attendance = int(current_attendance[:-1])  # If 100%, it stays 100%

            # Update the attendance percentage in the students table
            update_attendance_query = """
                UPDATE students
                SET attendance = %s
                WHERE id = %s
            """
            cursor.execute(update_attendance_query, (f"{new_attendance}%", student_id))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('mark_attendance'))





@app.route('/mark_attendance')
def mark_attendance():
    # Logic to fetch students or other data needed for the attendance page
    return render_template('mark_attendance.html')




#-------------------------------------------------------------------student -----------------------------------------------------------------------------------------------------------------

@app.route('/studentlogout')
def studentlogout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('studentlogin'))  # Redirect to the admin login page


@app.route('/studentlogin', methods=['GET', 'POST'])
def studentlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM students WHERE email = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                session['username'] = user['name']  # Store the username in the session
                return redirect(url_for('studentportal'))
            else:
                return render_template('studentlogin.html', error="Invalid username or password.")

    return render_template('studentlogin.html')


@app.route('/studentportal')
def studentportal():
    username = session.get('username')  # Get the username from the session

    if not username:
        return redirect(url_for('studentlogin'))  # Redirect to login if the username is not in the session

    connection = create_connection()
    
    announcements = []


    announcements_count=0


    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT title, message, timestamp FROM announcements ORDER BY timestamp DESC")
        announcements = cursor.fetchall()
        print(announcements)
        cursor.close()
        connection.close()

    return render_template('studentportal.html', 

                           username=username,announcements_count=announcements_count,announcements=announcements)
    
    
    
@app.route('/studentsignup', methods=['GET', 'POST'])
def studentsignup():
    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        password = request.form['password']
        unicode = request.form['unicode']
        expected_unicode = 'biher2024admin'

        if unicode != expected_unicode:
            return render_template('studnetsignup.html', error="Unicode does not match.")

        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute(
                "INSERT INTO students (id,name, email, phonenumber, password, unicode) VALUES (%s,%s, %s, %s, %s, %s)",
                (id,username, email, phonenumber, password, unicode)
            )
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('studentsignupconfirmation'))
    
    return render_template('studentsignup.html')

@app.route('/studentsignupconfirmation')
def studentsignupconfirmation():
    return render_template('studentsignupconfirmation.html')


@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':
        student_id = request.form.get('id')
        name = request.form.get('name')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        age = request.form.get('age')
        section = request.form.get('section')  # Updated section instead of department
        password = request.form.get('password')
        hostel = request.form.get('hostel')  # Added hostel field

        # Connect to the database
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Check if student exists
            cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            student = cursor.fetchone()
            cursor.close()
            
            if student:
                # Prepare update data
                update_data = {}
                if name:
                    update_data['name'] = name
                if email:
                    update_data['email'] = email
                if phonenumber:
                    update_data['phonenumber'] = phonenumber
                if age:
                    update_data['age'] = age
                if section:
                    update_data['section'] = section
                if password:
                    update_data['password'] = password
                if hostel:
                    update_data['hostel'] = hostel  # Handling hostel data

                if update_data:
                    update_query = "UPDATE students SET "
                    update_query += ", ".join(f"{key} = %s" for key in update_data.keys())
                    update_query += " WHERE id = %s"
                    
                    update_values = list(update_data.values()) + [student_id]
                    try:
                        cursor = connection.cursor()
                        cursor.execute(update_query, update_values)
                        connection.commit()
                    except Exception as e:
                        pass
                    finally:
                        cursor.close()
                        connection.close()

        # Redirect to the student portal after update
        return redirect(url_for('studentlogin'))

    return render_template('studentlogin')



@app.route('/studentdetails')
def studentdetails():
    username = session.get('username')  # Get the username from the session

    if not username:
        return redirect(url_for('studentlogin'))  # Redirect to login if the username is not in the session

    connection = create_connection()
    student_details = None  # To hold student data

    if connection:
        cursor = connection.cursor()

        try:
            # Fetch student details from the students table using the username (name)
            cursor.execute('''
                SELECT slno, id, name, email, phonenumber, unicode, age, course, section, password, fee_balance, date_time, attendance, hostel
                FROM students WHERE name = %s
            ''', (username,))  # Fetch student by name stored in session

            student_details = cursor.fetchone()  # Fetch one student record

            # Ensure there are no more unread results
            cursor.fetchall()  # Ensure that all results are processed

            if not student_details:
                return "No student details found", 404  # Handle case if no student is found

        except mysql.connector.errors.InternalError as e:
            # Handle specific error related to unread result
            connection.rollback()

        finally:
            # Always close the cursor and connection to avoid unread results
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    # Render the student details page with the fetched data
    return render_template(
        'mydetails_student.html',
        student_details=student_details
    )



@app.route("/mytodo_list")
def mytodo_list():
    username = session.get('username')
    if not username:
        return redirect(url_for('studentlogin'))

    connection = create_connection()
    notes = []

    if connection:
        cursor = connection.cursor(dictionary=True)
        # Dynamically create the table if it doesn't exist
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{username}_notes` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `note` VARCHAR(255) NOT NULL,
                `date` DATE NOT NULL,
                `time_created` TIME NOT NULL
            )
        """)
        # Fetch notes
        cursor.execute(f"SELECT * FROM `{username}_notes` ORDER BY time_created DESC")
        notes = cursor.fetchall()
        cursor.close()
        connection.close()

    return render_template("mytodolist.html", notes=notes, username=username)

@app.route("/myadd_note", methods=["POST"])
def myadd_note():
    username = session.get('username')
    if not username:
        return redirect(url_for('studentlogin'))

    note = request.form.get('note')
    date = datetime.now().strftime('%Y-%m-%d')
    time_created = datetime.now().strftime('%H:%M:%S')

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO `{username}_notes` (note, date, time_created) VALUES (%s, %s, %s)", (note, date, time_created))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('mytodo_list'))

@app.route("/mydelete_note/<int:note_id>", methods=["POST"])
def mydelete_note(note_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('studentlogin'))

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM `{username}_notes` WHERE id = %s", (note_id,))
        connection.commit()
        cursor.close()
        connection.close()
    return redirect(url_for('mytodo_list'))

@app.route("/announcementtablefromteacher", methods=['GET', 'POST'])
def announcementtablefromteacher():
    connection = create_connection()
    announcements = []
    section_name = None
    username = session.get('username')
    section_name1 = None

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Fetch section from the student table
            if username:
                query = "SELECT section FROM students WHERE name = %s"
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                if result:
                    section_name1 = result['section']
                cursor.fetchall()  # Ensure all results are fetched to avoid Unread result found error

            # Fetch announcements for the section if POST request
            if request.method == 'POST':
                section_name = request.form.get('section_name')
                if section_name == section_name1:
                    try:
                        table_name = f"{section_name}_announcements"
                        query = f"SELECT title, message, created_at FROM {table_name} ORDER BY created_at DESC"
                        cursor.execute(query)
                        announcements = cursor.fetchall()
                        print("Fetched announcements:", announcements)  # Debug print
                    except Exception as e:
                        print(f"Error fetching announcements: {e}")  # Log the error
        except Exception as e:
            print(f"Database error: {e}")  # Log the error
        finally:
            cursor.close()
            connection.close()

    return render_template('announcementsfromteachers.html', announcements=announcements, section_name=section_name)





@app.route('/view_placements_students')
def view_placements_students():
    if 'username' in session:
        connection = create_connection()
        cursor = connection.cursor()

        # Fetch all placements
        select_query = 'SELECT * FROM placements2024'
        cursor.execute(select_query)
        placements = cursor.fetchall()

        return render_template('studentsplacementportal.html', placements=placements)
    else:
        return redirect(url_for('studentlogin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


