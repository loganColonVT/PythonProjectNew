from flask import Flask, render_template, request, redirect, url_for, flash
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

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
    #KEEP IN MIND - no DB connection. As of now, hard coded.
    error = False
    email = request.form.get("email")
    password = request.form.get("password")

    if email != 'logan@vt.edu':
        error = True
        
    if password != 'pass':
        error = True

    if error:
        flash("Invalid email or password")
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Handle form submission - redirect to student dashboard
        return redirect(url_for('student_dashboard'))
    

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

@app.route('/professor-dashboard')
def professor_dashboard():
    return render_template('professor-dashboard.html')

@app.route('/roster-completion')
def roster_completion():
    return render_template('roster-completion.html')

@app.route('/eval-creation', methods=['POST'])
def eval_creation():
    courseCode = request.form.get('courseCode')

    return render_template('eval-creation.html', courseCode=courseCode)

@app.route('/viewtest')
def proftest():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT courseCode, courseTime FROM course;")
    rows = cursor.fetchall()

    # Convert tuples to dictionaries
    courses = []
    for row in rows:
        courses.append({
            'courseCode': row[0],
            'courseTime': row[1]
        })

    conn.close()
    cursor.close()


    return render_template('professor-dashboard copy.html', courses=courses)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
