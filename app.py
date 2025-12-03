from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
import os
import mysql.connector
import csv
import io

app = Flask(__name__)
app.secret_key = 'fdshj3838aslenddk232bnhdfs'  # Required for flash messages

# Context processor to expose authentication state to all templates
@app.context_processor
def inject_auth_state():
    is_authenticated = bool(session.get('professor_id') or session.get('student_id'))
    user_role = None
    if session.get('professor_id'):
        user_role = 'professor'
    elif session.get('student_id'):
        user_role = 'student'
    return dict(is_authenticated=is_authenticated, user_role=user_role)

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
    response = make_response(render_template('index.html'))
    # Prevent caching of the home page to ensure fresh session state
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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

    # First check if it's a professor
    cursor.execute("SELECT ProfessorID, Password FROM professor WHERE Email = %s", (email,))
    professor_result = cursor.fetchone()

    if professor_result:
        professor_id, db_password = professor_result
        if password == db_password:
            # Clear any existing student session
            session.pop('student_id', None)
            # Store the professor's ID and role in the session
            session['professor_id'] = professor_id
            session['role'] = 'professor'
            cursor.close()
            conn.close()
            return redirect(url_for('professor_dashboard'))
    
    # If not a professor, check if it's a student
    cursor.execute("SELECT StudentID, Password FROM student WHERE Email = %s", (email,))
    student_result = cursor.fetchone()

    if student_result:
        student_id, db_password = student_result
        if password == db_password:
            # Clear any existing professor session
            session.pop('professor_id', None)
            # Store the student's ID and role in the session
            session['student_id'] = student_id
            session['role'] = 'student'
            cursor.close()
            conn.close()
            return redirect(url_for('student_dashboard'))

    cursor.close()
    conn.close()

    # If we get here, credentials were invalid
    flash("Invalid email or password", "error")
    return redirect(url_for('login'))
    

@app.route('/get-started', methods=['GET', 'POST'])
def get_started():
    if request.method == 'POST':
        # Handle form submission - show success message
        flash('Account created successfully! You can now log in.', 'success')
        return render_template('get-started.html')
    return render_template('get-started.html')

@app.route('/peer-evaluation')
def peer_evaluation():
    student_id = session.get('student_id')
    
    if not student_id:
        flash("You must log in first.", "error")
        return redirect(url_for('login'))
    
    # Get peerevalID and groupID from query parameters
    peereval_id = request.args.get('peerevalID')
    group_id = request.args.get('groupID')
    course_id = request.args.get('courseID')
    
    if not peereval_id or not group_id or not course_id:
        flash("Missing required parameters.", "error")
        return redirect(url_for('student_dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify the peer evaluation belongs to the logged-in student
    cursor.execute("""
        SELECT StudentEvaluator, CourseID 
        FROM peerevaluation 
        WHERE PeerEvalID = %s
    """, (peereval_id,))
    
    eval_check = cursor.fetchone()
    if not eval_check or eval_check[0] != student_id:
        cursor.close()
        conn.close()
        flash("You don't have permission to access this evaluation.", "error")
        return redirect(url_for('student_dashboard'))
    
    # Get all students in the specified group (excluding the evaluator)
    cursor.execute("""
        SELECT s.StudentID, s.Name
        FROM student s
        INNER JOIN groupmembers gm ON s.StudentID = gm.StudentID
        WHERE gm.GroupID = %s AND s.StudentID != %s
        ORDER BY s.Name
    """, (group_id, student_id))
    
    group_students = [{'studentID': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    # Get course code for display
    cursor.execute("SELECT CourseCode FROM course WHERE CourseID = %s", (course_id,))
    course_result = cursor.fetchone()
    course_code = course_result[0] if course_result else None

    cursor.close()
    conn.close()

    return render_template('peer-evaluation.html', 
                         peerevalID=peereval_id,
                         groupID=group_id,
                         courseID=course_id,
                         courseCode=course_code,
                         groupStudents=group_students)

@app.route('/peer-evalsubmit', methods=['POST'])
def peer_evaluation_submit():
    student_id = session.get('student_id')
    
    if not student_id:
        flash("You must log in first.", "error")
        return redirect(url_for('login'))

    error = False

    # Get form data
    peereval_id = request.form.get("peerevalID")
    evaluatee_id = request.form.get("evaluateeID")  # From dropdown
    course_id = request.form.get("courseID")

    if not evaluatee_id:
        error = True
        flash("Please select a student to evaluate.")
    if not course_id:
        error = True
        flash("Missing course information.")

    # Get all score fields
    contribution = request.form.get("field1")
    collaboration = request.form.get("field2")
    communication = request.form.get("field3")
    planning = request.form.get("field4")
    inclusivity = request.form.get("field5")
    overall = request.form.get("field6")

    # Validate all scores are provided
    if not all([contribution, collaboration, communication, planning, inclusivity, overall]):
        error = True
        flash("Please provide all evaluation scores.")

    if error:
        # Redirect back to peer evaluation with parameters
        return redirect(url_for('peer_evaluation', 
                               peerevalID=peereval_id,
                               groupID=request.form.get("groupID"),
                               courseID=course_id))
    
    # Convert scores to integers
    contribution = int(contribution)
    collaboration = int(collaboration)
    communication = int(communication)
    planning = int(planning)
    inclusivity = int(inclusivity)
    overall = int(overall)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if evaluation exists with this evaluator and evaluatee
    cursor.execute("""
        SELECT PeerEvalID 
        FROM peerevaluation 
        WHERE StudentEvaluator = %s AND StudentEvaluatee = %s AND CourseID = %s
    """, (student_id, evaluatee_id, course_id))
    
    existing_eval = cursor.fetchone()
    
    if existing_eval:
        # Update existing evaluation
        cursor.execute("""
            UPDATE peerevaluation 
            SET Contribution = %s, Collaboration = %s, Communication = %s, 
                Planning = %s, Inclusivity = %s, Overall = %s
            WHERE PeerEvalID = %s
        """, (contribution, collaboration, communication, planning, inclusivity, overall, existing_eval[0]))
        flash("Peer evaluation updated successfully!", "success")
    else:
        # Insert new evaluation
        if peereval_id:
            # Use the provided peerevalID
            cursor.execute("""
                INSERT INTO peerevaluation 
                (PeerEvalID, StudentEvaluator, StudentEvaluatee, CourseID, 
                 Contribution, Collaboration, Communication, Planning, Inclusivity, Overall)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (peereval_id, student_id, evaluatee_id, course_id, 
                  contribution, collaboration, communication, planning, inclusivity, overall))
        else:
            # Let database auto-generate PeerEvalID
            cursor.execute("""
                INSERT INTO peerevaluation 
                (StudentEvaluator, StudentEvaluatee, CourseID, 
                 Contribution, Collaboration, Communication, Planning, Inclusivity, Overall)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (student_id, evaluatee_id, course_id, 
                  contribution, collaboration, communication, planning, inclusivity, overall))
        flash("Peer evaluation submitted successfully!", "success")
    
    conn.commit()
    cursor.close()
    conn.close()

    return render_template('confirmation-screens.html')
    

@app.route('/student-dashboard')
def student_dashboard():
    student_id = session.get('student_id')
    
    if not student_id:
        flash("You must log in first.", "error")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query peer evaluations for this student, including course code and group info
    # Get all peer evaluations where student is evaluator, and find their group for each course
    cursor.execute("""
        SELECT DISTINCT 
            pe.PeerEvalID,
            pe.CourseID,
            c.CourseCode,
            sg.GroupID,
            sg.GroupName
        FROM peerevaluation pe
        INNER JOIN course c ON pe.CourseID = c.CourseID
        INNER JOIN groupmembers gm ON pe.StudentEvaluator = gm.StudentID
        INNER JOIN studentgroup sg ON gm.GroupID = sg.GroupID AND sg.CourseID = pe.CourseID
        WHERE pe.StudentEvaluator = %s
        ORDER BY c.CourseCode, sg.GroupName
    """, (student_id,))
    
    evaluations = []
    for row in cursor.fetchall():
        peereval_id, course_id, course_code, group_id, group_name = row
        evaluations.append({
            'peerevalID': peereval_id,
            'courseID': course_id,
            'courseCode': course_code,
            'groupID': group_id,
            'groupName': group_name or 'No Group'
        })
    
    cursor.close()
    conn.close()
    
    return render_template('student-dashboard.html', evaluations=evaluations)

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
        professor_id = session.get('professor_id')
        if not professor_id:
            flash('You must log in first.', 'error')
            return redirect(url_for('login'))
        
        # Get course code from form
        course_code = request.form.get('courseCode', '').strip()
        if not course_code:
            flash('Course code is required', 'error')
            return redirect(url_for('importRoster'))
        
        # Get the uploaded file
        if 'rosterFile' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('importRoster'))
        
        file = request.files['rosterFile']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('importRoster'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify course exists and get CourseID
        cursor.execute("SELECT CourseID FROM course WHERE CourseCode = %s AND ProfessorID = %s", 
                      (course_code, professor_id))
        course_result = cursor.fetchone()
        
        if not course_result:
            cursor.close()
            conn.close()
            flash(f'Course code "{course_code}" not found or you do not have access to it.', 'error')
            return redirect(url_for('importRoster'))
        
        course_id = course_result[0]
        
        # Get current date and time for enrollment
        from datetime import datetime
        enrollment_date = datetime.now().date()
        enrollment_time = datetime.now().time()
        
        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.reader(stream)
        
        students_added = 0
        enrollments_added = 0
        errors = []
        student_ids = []  # Track student IDs for enrollment
        
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
                
                # Check if studentID already exists
                cursor.execute("SELECT StudentID FROM student WHERE StudentID = %s", (student_id,))
                student_exists = cursor.fetchone()
                
                if not student_exists:
                    # Student doesn't exist - create new student with password
                # Extract first name from Name column
                first_name = name.split()[0] if name else ''
                password = first_name + '123'
                
                    try:
                sql = 'INSERT INTO student (StudentID, Name, Email, Password) VALUES (%s, %s, %s, %s)'
                values = (student_id, name, email, password)
                        cursor.execute(sql, values)
                        students_added += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error creating student {student_id} - {str(e)}")
                        continue  # Skip enrollment if student creation failed
                # If student exists, skip student creation and just create enrollment
                
                student_ids.append(student_id)
                
            except Exception as e:
                errors.append(f"Row {row_num}: Error processing student - {str(e)}")
        
        # Create enrollments for all imported students
        for student_id in student_ids:
            try:
                # Check if enrollment already exists
                cursor.execute("SELECT EnrollmentID FROM enrollment WHERE CourseID = %s AND StudentID = %s", 
                             (course_id, student_id))
                if not cursor.fetchone():
                    # Insert enrollment
                    cursor.execute("""
                        INSERT INTO enrollment (CourseID, StudentID, EnrollmentDate, EnrollmentTime) 
                        VALUES (%s, %s, %s, %s)
                    """, (course_id, student_id, enrollment_date, enrollment_time))
                    enrollments_added += 1
            except Exception as e:
                errors.append(f"Error creating enrollment for student {student_id}: {str(e)}")
        
        # Commit all successful inserts
        conn.commit()
        cursor.close()
        conn.close()
        
        # Show success message
        if students_added > 0:
            flash(f'Successfully imported {students_added} student(s) and created {enrollments_added} enrollment(s)', 'success')
        if errors:
            flash(f'Some errors occurred: {"; ".join(errors[:5])}', 'warning')
        
        # Redirect to creating groups page with courseID
        return redirect(url_for('createGroups', courseID=course_id))
        
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
    professor_id = session.get('professor_id')
    if not professor_id:
        flash('You must log in first.', 'error')
        return redirect(url_for('login'))
    
    # Get courseID from query parameters
    course_id = request.args.get('courseID')
    if not course_id:
        flash('No course selected', 'error')
        return redirect(url_for('professor_dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify course belongs to professor
    cursor.execute("SELECT CourseCode FROM course WHERE CourseID = %s AND ProfessorID = %s", 
                  (course_id, professor_id))
    course_result = cursor.fetchone()
    
    if not course_result:
        cursor.close()
        conn.close()
        flash('Course not found or you do not have access to it.', 'error')
        return redirect(url_for('professor_dashboard'))
    
    course_code = course_result[0]
    
    # Get all students enrolled in this course
    cursor.execute("""
        SELECT DISTINCT s.StudentID, s.Name
        FROM student s
        INNER JOIN enrollment e ON s.StudentID = e.StudentID
        WHERE e.CourseID = %s
        ORDER BY s.Name
    """, (course_id,))
    
    students = [{'studentID': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    # Get existing groups for this course (for editing)
    cursor.execute("""
        SELECT GroupID, GroupName
        FROM studentgroup
        WHERE CourseID = %s
        ORDER BY GroupID
        LIMIT 4
    """, (course_id,))
    
    existing_groups = []
    for group_row in cursor.fetchall():
        group_id, group_name = group_row
        
        # Get students in this group
        cursor.execute("""
            SELECT StudentID
            FROM groupmembers
            WHERE GroupID = %s
        """, (group_id,))
        
        student_ids_in_group = [row[0] for row in cursor.fetchall()]
        existing_groups.append({
            'groupID': group_id,
            'groupName': group_name,
            'studentIDs': student_ids_in_group
        })
    
    cursor.close()
    conn.close()
    
    return render_template('creating-groups.html', 
                         courseID=course_id, 
                         courseCode=course_code, 
                         students=students,
                         existingGroups=existing_groups)

@app.route('/createGroupsSubmit', methods=['POST'])
def createGroupsSubmit():
    professor_id = session.get('professor_id')
    if not professor_id:
        flash('You must log in first.', 'error')
        return redirect(url_for('login'))
    
    course_id = request.form.get('courseID')
    if not course_id:
        flash('No course selected', 'error')
        return redirect(url_for('professor_dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify course belongs to professor
    cursor.execute("SELECT CourseID FROM course WHERE CourseID = %s AND ProfessorID = %s", 
                  (course_id, professor_id))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        flash('Course not found or you do not have access to it.', 'error')
        return redirect(url_for('professor_dashboard'))
    
    # Delete existing groups and group members for this course (for editing)
    cursor.execute("""
        DELETE gm FROM groupmembers gm
        INNER JOIN studentgroup sg ON gm.GroupID = sg.GroupID
        WHERE sg.CourseID = %s
    """, (course_id,))
    
    cursor.execute("DELETE FROM studentgroup WHERE CourseID = %s", (course_id,))
    
    groups_created = 0
    errors = []
    
    try:
        # Process each of the 4 groups
        for group_num in range(1, 5):
            group_name = request.form.get(f'groupName{group_num}', '').strip()
            student_ids = request.form.getlist(f'group{group_num}Students')
            
            # Skip if no group name provided
            if not group_name:
                continue
            
            # Create the group
            try:
                cursor.execute("""
                    INSERT INTO studentgroup (CourseID, GroupName) 
                    VALUES (%s, %s)
                """, (course_id, group_name))
                group_id = cursor.lastrowid
                
                # Add students to the group
                for student_id in student_ids:
                    if student_id:
                        try:
                            cursor.execute("""
                                INSERT INTO groupmembers (GroupID, StudentID) 
                                VALUES (%s, %s)
                            """, (group_id, student_id))
                        except mysql.connector.IntegrityError:
                            # Student already in group, skip
                            pass
                
                groups_created += 1
            except Exception as e:
                errors.append(f"Error creating group {group_num}: {str(e)}")
        
        conn.commit()
        
        if groups_created > 0:
            flash(f'Successfully created {groups_created} group(s)', 'success')
        if errors:
            flash(f'Some errors occurred: {"; ".join(errors[:5])}', 'warning')
        
        # Redirect to view groups for this course
        return redirect(url_for('seeGroups', courseID=course_id))
        
    except Exception as e:
        conn.rollback()
        flash(f'Error creating groups: {str(e)}', 'error')
        return redirect(url_for('createGroups', courseID=course_id))
    finally:
        cursor.close()
        conn.close()

@app.route('/logout')
def logout():
    # Explicitly clear all session keys
    session.pop('professor_id', None)
    session.pop('student_id', None)
    session.pop('role', None)
    session.clear()  # Clear any remaining session data
    session.modified = True  # Ensure Flask knows the session was modified
    flash("You have been logged out successfully.", "success")
    # Use redirect with no_cache to prevent caching
    response = redirect(url_for('home'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5002)
