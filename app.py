from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
import csv
import io

app = Flask(__name__)
app.secret_key = 'fdshj3838aslenddk232bnhdfs'  # Required for flash messages

# DB connection
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        port=os.environ.get('DB_PORT')
    )
    return connection

# Home route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/testsql')
def tester():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('select courseID from course;')
    courseIDs = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('liveDemoTest.html', courseIDs=courseIDs)

@app.route('/testSubmit', methods=['POST'])
def testSubmit():
    courseId = request.form.get("courseID")
    groupName = request.form.get("groupName")

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = 'INSERT INTO studentgroup (GroupID, CourseID, GroupName) VALUES (22, %s, %s)'
    values = (courseId, groupName)

    cursor.execute(sql, values)
    conn.commit()

    return 'Successful submission'


@app.route('/confirmation-screens')
def confirmation_screens():
    return render_template('confirmation-screens.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginSubmit', methods=['POST'])
def loginSubmit():

    conn = get_db_connection()
    cursor = conn.cursor()

    email = request.form.get("email")
    password = request.form.get("password")

    # Check credentials
    cursor.execute("SELECT ProfessorID, Password FROM professor WHERE Email = %s", (email,))
    result = cursor.fetchone()

    error = False
    if result is None:
        error = True
    else:
        professor_id, db_password = result
        if password != db_password:
            error = True

    cursor.close()
    conn.close()

    if error:
        flash("Invalid email or password", "error")
        return redirect(url_for('login'))
    else:
        #Store the professor's ID in the session
        session['professor_id'] = professor_id
        return redirect(url_for('professor_dashboard'))
    

@app.route('/get-started', methods=['POST'])
def get_started():
    if request.method == 'POST':
        # Handle form submission - show success message
        flash('Account created successfully! You can now log in.', 'success')
        return render_template('get-started.html')
    return render_template('get-started.html')

@app.route('/peer-evaluation')
def peer_evaluation():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('select courseCode from course;')
    courseIDs = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('peer-evaluation.html', courseIDs=courseIDs)

#REMINDER - When access to SQL DB -> replace hardcoded choices. 
#Also ensure that you have the correct values to be added to database - 
#there could be more or less than what is provided. Consult Daria/Shriya!!
@app.route('/peer-evalsubmit', methods=['POST'])
def peer_evaluation_submit():
    def safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    error = False

    # Student evaluator
    fname = request.form.get("fname")
    lname = request.form.get("lname")

    if not fname:
        error = True
        flash("Please provide your first name")
    if not lname:
        error = True
        flash("Please provide your last name")

    # Student evaluatee
    fname2 = request.form.get("fname2")
    lname2 = request.form.get("lname2")

    if not fname2:
        error = True
        flash("Please provide your evaluatee's first name")
    if not lname2:
        error = True
        flash("Please provide your evaluatee's last name")

    # Course ID
    courseID = request.form.get("courseID")
    if not courseID:
        error = True
        flash("Please select valid course ID")

    # Completion date Month, Day, Year (Respectively)
    month = safe_int(request.form.get("month"))
    day = safe_int(request.form.get("day"))
    year = safe_int(request.form.get("year"))

    if not all([month, day, year]):
        error = True
        flash("Please enter a valid numeric completion date.")
    
    # Evaluation due date month, day, year (respectively)
    month2 = safe_int(request.form.get("month2"))
    day2 = safe_int(request.form.get("day2"))
    year2 = safe_int(request.form.get("year2"))

    if not all([month2, day2, year2]):
        error = True
        flash("Please enter a valid numeric due date.")

    #Radio is not included in error checking
    #Values are marked as required -> this is just simpler

    #participation score
    pscore = request.form.get("field1")
    if not pscore:
        error = True
   

    #skillful score
    sscore = request.form.get("field2")
    if not sscore:
        error = True    

    #feedback score
    fscore = request.form.get("field3")
    if not fscore:
        error = True 

    #communication score
    cscore = request.form.get("field4")
    if not cscore:
        error = True

    #encouragement score
    escore = request.form.get("field5")
    if not escore:
        error = True

    #integration score 
    iscore = request.form.get("field6")
    if not iscore:
        error = True

    #role score
    rscore = request.form.get("field7")
    if not rscore:
        error = True

    #goals score
    gscore = request.form.get("field8")
    if not gscore:
        error = True

    #reporting score
    rescore = request.form.get("field9")
    if not rescore:
        error = True

    #consistency score
    coscore = request.form.get("field10")
    if not coscore:
        error = True
    
    #optimism score
    oscore = request.form.get("field11")
    if not oscore:
        error = True

    #appropriate assertiveness score
    ascore = request.form.get("field12")
    if not ascore:
        error = True

    #healthy debate score
    dscore = request.form.get("field13")
    if not dscore:
        error = True

    #response to conflict score
    rtcscore = request.form.get("field14")
    if not rtcscore:
        error = True

    #overall score
    ovscore = request.form.get("field15")
    if not ovscore:
        error = True

    if error:
        flash("Ensure all parts of form are answered.")
        return redirect(url_for('peer_evaluation'))
    else:
        pscore=int(pscore)
        sscore=int(sscore)
        fscore=int(fscore)
        cscore=int(cscore)
        escore=int(escore)
        iscore=int(iscore)
        rscore=int(rscore)
        gscore=int(gscore)
        rescore=int(rescore)
        coscore=int(coscore)
        oscore=int(oscore)
        ascore=int(ascore)
        dscore=int(dscore)
        rtcscore=int(rtcscore)
        ovscore=int(ovscore)

        return render_template('confirmation-screens.html')
    

@app.route('/student-dashboard')
def student_dashboard():
    return render_template('student-dashboard.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/roster-completion')
def roster_completion():
    return render_template('roster-completion.html')

@app.route('/eval-creation', methods=['POST'])
def eval_creation():
    courseCode = request.form.get('courseCode')

    return render_template('eval-creation.html', courseCode=courseCode)

@app.route('/evalCreationSubmit', methods=['POST'])
def eval_creation_submit():
    dueDate = request.form.get('due_date')
    courseCode = request.form.get('courseCode')

    conn = get_db_connection()
    cursor = conn.cursor()

    update_query = """
        UPDATE course
        SET EvalDueDate = %s
        WHERE CourseCode = %s
    """
    cursor.execute(update_query, (dueDate, courseCode))

    conn.commit()
    cursor.close()
    conn.close()

    return render_template('confirmation-screens.html')

@app.route('/professorDashboard')
def professor_dashboard():

    professor_id = session.get('professor_id')

    if not professor_id:
        flash("You must log in first.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT CourseID, CourseCode, CourseTime
        FROM course
        WHERE ProfessorID = %s
    """, (professor_id,))

    rows = cursor.fetchall()

    courses = [{'courseID': row[0], 'courseCode': row[1], 'courseTime': row[2]} for row in rows]

    cursor.close()
    conn.close()

    return render_template('professor-dashboard.html', courses=courses)

@app.route('/importCourseRoster')
def importRoster():
    return render_template('import-course-roster.html')

@app.route('/importCourseSubmit', methods=['POST'])
def importSubmit():
    try:
        # Get the uploaded file
        if 'rosterFile' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('importRoster'))
        
        file = request.files['rosterFile']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('importRoster'))
        
        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.reader(stream)
        
        # Skip header row if present (optional - you can remove this if CSV has no header)
        # next(csv_reader, None)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        students_added = 0
        errors = []
        
        # Process each row in the CSV
        for row_num, row in enumerate(csv_reader, start=1):
            # Skip empty rows
            if not row or len(row) < 3:
                continue
            
            try:
                # Extract data from CSV columns
                student_id = row[0].strip()
                name = row[1].strip()
                email = row[2].strip()
                # Column 4 (password) is ignored - we'll generate it
                
                # Extract first name from Name column
                first_name = name.split()[0] if name else ''
                password = first_name + '123'
                
                # Insert student into database
                sql = 'INSERT INTO student (StudentID, Name, Email, Password) VALUES (%s, %s, %s, %s)'
                values = (student_id, name, email, password)
                
                cursor.execute(sql, values)
                students_added += 1
                
            except mysql.connector.IntegrityError as e:
                # Handle duplicate entries or other integrity errors
                errors.append(f"Row {row_num}: Student ID {student_id} may already exist or invalid data")
            except Exception as e:
                errors.append(f"Row {row_num}: Error processing student - {str(e)}")
        
        # Commit all successful inserts
        conn.commit()
        cursor.close()
        conn.close()
        
        # Show success message
        if students_added > 0:
            flash(f'Successfully imported {students_added} student(s)', 'success')
        if errors:
            flash(f'Some errors occurred: {"; ".join(errors[:5])}', 'warning')
        
        return render_template('creating-groups.html')
        
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('importRoster'))

@app.route('/groupsInClass', methods=['GET', 'POST'])
def seeGroups():
    # Get courseID from request (either GET or POST)
    course_id = request.args.get('courseID') or request.form.get('courseID')
    
    if not course_id:
        flash('No course selected', 'error')
        return redirect(url_for('professor_dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get course information
    cursor.execute("SELECT CourseCode, CourseTime FROM course WHERE CourseID = %s", (course_id,))
    course_info = cursor.fetchone()
    
    if not course_info:
        cursor.close()
        conn.close()
        flash('Course not found', 'error')
        return redirect(url_for('professor_dashboard'))
    
    course_code, course_time = course_info
    
    # Get all groups for this course
    cursor.execute("""
        SELECT GroupID, GroupName
        FROM studentgroup
        WHERE CourseID = %s
        ORDER BY GroupName
    """, (course_id,))
    
    groups_data = cursor.fetchall()
    
    # For each group, get the students
    groups = []
    for group_id, group_name in groups_data:
        cursor.execute("""
            SELECT s.StudentID, s.Name
            FROM student s
            INNER JOIN groupmembers gm ON s.StudentID = gm.StudentID
            WHERE gm.GroupID = %s
            ORDER BY s.Name
        """, (group_id,))
        
        students = [{'studentID': row[0], 'name': row[1]} for row in cursor.fetchall()]
        
        groups.append({
            'groupID': group_id,
            'groupName': group_name,
            'students': students
        })
    
    cursor.close()
    conn.close()
    
    return render_template('groups-in-your-class.html', 
                         courseID=course_id,
                         courseCode=course_code,
                         courseTime=course_time,
                         groups=groups)

@app.route('/createGroups')
def createGroups():
    return render_template('creating-groups.html')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
