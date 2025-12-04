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

# Context processor to make authentication state available to all templates
@app.context_processor
def inject_user_data():
    is_authenticated = 'professor_id' in session or 'student_id' in session
    user_role = session.get('role')
    return dict(is_authenticated=is_authenticated, user_role=user_role)

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

    # Check professor credentials
    cursor.execute("SELECT ProfessorID, Password FROM professor WHERE Email = %s", (email,))
    professor_result = cursor.fetchone()

    if professor_result:
        professor_id, db_password = professor_result
        if password == db_password:
            session['professor_id'] = professor_id
            session['role'] = 'professor'
            flash("Logged in as Professor!", "success")
            cursor.close()
            conn.close()
            return redirect(url_for('professor_dashboard'))

    # Check student credentials
    cursor.execute("SELECT StudentID, Password FROM student WHERE Email = %s", (email,))
    student_result = cursor.fetchone()

    if student_result:
        student_id, db_password = student_result
        if password == db_password:
            session['student_id'] = student_id
            session['role'] = 'student'
            flash("Logged in as Student!", "success")
            cursor.close()
            conn.close()
            return redirect(url_for('student_dashboard'))

    cursor.close()
    conn.close()
    flash("Invalid email or password", "error")
    return redirect(url_for('login'))
    

@app.route('/get-started', methods=['POST'])
def get_started():
    if request.method == 'POST':
        # Handle form submission - show success message
        flash('Account created successfully! You can now log in.', 'success')
        return render_template('get-started.html')
    return render_template('get-started.html')

@app.route('/peer-evaluation')
def peer_evaluation():
    # Get parameters from URL
    group_id = request.args.get('groupID')
    course_id = request.args.get('courseID')
    peereval_id = request.args.get('peerevalID')
    
    # Check if student is logged in
    student_id = session.get('student_id')
    
    if not student_id:
        flash("You must log in first.")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    group_students = []
    
    # If groupID is provided, get all students in that group
    if group_id:
        try:
            # Query to get all students in the group (excluding the current student)
            query = """
                SELECT s.StudentID, s.Name
                FROM student s
                INNER JOIN groupmembers gm ON s.StudentID = gm.StudentID
                WHERE gm.GroupID = %s AND s.StudentID != %s
                ORDER BY s.Name
            """
            cursor.execute(query, (group_id, student_id))
            results = cursor.fetchall()
            
            # Convert to list of dictionaries for the template
            for row in results:
                group_students.append({
                    'studentID': row[0],
                    'name': row[1]
                })
        except Exception as e:
            flash(f"Error loading group members: {str(e)}", "error")
            group_students = []
    
    # Get course codes for dropdown (if still needed)
    cursor.execute('SELECT CourseCode FROM course;')
    courseIDs = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('peer-evaluation.html', courseIDs=courseIDs, groupStudents=group_students, 
                         groupID=group_id, courseID=course_id, peerevalID=peereval_id)

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
    # Check if student is logged in
    student_id = session.get('student_id')
    
    if not student_id:
        flash("You must log in first.")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    evaluations = []
    
    # Query to get groups the student is in with course information
    # This will show all groups/courses the student is part of for peer evaluation
    query = """
        SELECT DISTINCT
            c.CourseCode,
            sg.GroupName,
            sg.GroupID,
            sg.CourseID
        FROM groupmembers gm
        INNER JOIN studentgroup sg ON gm.GroupID = sg.GroupID
        INNER JOIN course c ON sg.CourseID = c.CourseID
        WHERE gm.StudentID = %s
    """
    
    try:
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        
        # Convert to list of dictionaries for the template
        # Use GroupID as peerevalID if there's no separate peer evaluation assignment table
        for row in results:
            course_code, group_name, group_id, course_id = row
            
            # Try to get peer evaluation ID if there's a peer evaluation assignment table
            peereval_id = group_id  # Default to group_id
            
            # Try different possible table names for peer evaluation assignments
            try:
                # Try common table name variations
                pe_query = """
                    SELECT PeerEvalID FROM peerevaluationassignment 
                    WHERE GroupID = %s AND CourseID = %s
                    LIMIT 1
                """
                cursor.execute(pe_query, (group_id, course_id))
                pe_result = cursor.fetchone()
                if pe_result:
                    peereval_id = pe_result[0]
            except:
                # If that table doesn't exist or has different name, try alternatives
                try:
                    pe_query = """
                        SELECT PeerEvalID FROM peerevaluation 
                        WHERE GroupID = %s AND CourseID = %s
                        LIMIT 1
                    """
                    cursor.execute(pe_query, (group_id, course_id))
                    pe_result = cursor.fetchone()
                    if pe_result:
                        peereval_id = pe_result[0]
                except:
                    # Use group_id as default
                    pass
            
            evaluations.append({
                'courseCode': course_code,
                'groupName': group_name,
                'groupID': group_id,
                'courseID': course_id,
                'peerevalID': peereval_id
            })
            
    except Exception as e:
        flash(f"Error loading evaluations: {str(e)}", "error")
        evaluations = []
    
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
        
        # Verify course exists and get CourseID (using CourseCode, not CourseID)
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
        elif enrollments_added > 0:
            flash(f'Successfully created {enrollments_added} enrollment(s) for existing students', 'success')
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
    
    # Get ALL students enrolled in this course (not just those in groups)
    cursor.execute("""
        SELECT DISTINCT s.StudentID, s.Name
        FROM student s
        INNER JOIN enrollment e ON s.StudentID = e.StudentID
        WHERE e.CourseID = %s
        ORDER BY s.Name
    """, (course_id,))
    
    students = [{'studentID': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    # Get existing groups for this course (for editing) - limit to 4 groups
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
    
    # Get existing groups for this course (ordered by GroupID, limit to 4)
    cursor.execute("""
        SELECT GroupID, GroupName
        FROM studentgroup
        WHERE CourseID = %s
        ORDER BY GroupID
        LIMIT 4
    """, (course_id,))
    
    existing_groups_list = cursor.fetchall()
    
    groups_updated = 0
    groups_created = 0
    groups_deleted = 0
    errors = []
    
    try:
        # Process each of the 4 groups
        for group_num in range(1, 5):
            group_name = request.form.get(f'groupName{group_num}', '').strip()
            student_ids = request.form.getlist(f'group{group_num}Students')
            
            # Check if there's an existing group at this position
            existing_group = None
            if group_num - 1 < len(existing_groups_list):
                existing_group = existing_groups_list[group_num - 1]
            
            if group_name:
                # Group name provided - update or create
                if existing_group:
                    # Update existing group
                    existing_group_id = existing_group[0]
                    try:
                        # Update group name if it changed
                        if existing_group[1] != group_name:
                            cursor.execute("""
                                UPDATE studentgroup 
                                SET GroupName = %s 
                                WHERE GroupID = %s
                            """, (group_name, existing_group_id))
                        
                        # Remove all existing members
                        cursor.execute("DELETE FROM groupmembers WHERE GroupID = %s", (existing_group_id,))
                        
                        # Add selected students
                        for student_id in student_ids:
                            if student_id:
                                try:
                                    cursor.execute("""
                                        INSERT INTO groupmembers (GroupID, StudentID) 
                                        VALUES (%s, %s)
                                    """, (existing_group_id, student_id))
                                except mysql.connector.IntegrityError:
                                    # Student already in group, skip
                                    pass
                        
                        groups_updated += 1
                    except Exception as e:
                        errors.append(f"Error updating group {group_num}: {str(e)}")
                else:
                    # Create new group
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
            else:
                # No group name provided - delete existing group if it exists
                if existing_group:
                    existing_group_id = existing_group[0]
                    try:
                        # Delete group members first
                        cursor.execute("DELETE FROM groupmembers WHERE GroupID = %s", (existing_group_id,))
                        # Delete the group
                        cursor.execute("DELETE FROM studentgroup WHERE GroupID = %s", (existing_group_id,))
                        groups_deleted += 1
                    except Exception as e:
                        errors.append(f"Error deleting group {group_num}: {str(e)}")
        
        conn.commit()
        
        # Show success message
        messages = []
        if groups_updated > 0:
            messages.append(f'Updated {groups_updated} group(s)')
        if groups_created > 0:
            messages.append(f'Created {groups_created} new group(s)')
        if groups_deleted > 0:
            messages.append(f'Deleted {groups_deleted} group(s)')
        
        if messages:
            flash('; '.join(messages), 'success')
        if errors:
            flash(f'Some errors occurred: {"; ".join(errors[:5])}', 'warning')
        
        # Redirect to view groups for this course
        return redirect(url_for('seeGroups', courseID=course_id))
        
    except Exception as e:
        conn.rollback()
        flash(f'Error updating groups: {str(e)}', 'error')
        return redirect(url_for('createGroups', courseID=course_id))
    finally:
        cursor.close()
        conn.close()

@app.route('/logout', methods=['GET', 'POST'])
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
