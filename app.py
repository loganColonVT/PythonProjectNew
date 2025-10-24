from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Home route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/confirmation-screens')
def confirmation_screens():
    return render_template('confirmation-screens.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle form submission - redirect to student dashboard
        return redirect(url_for('student_dashboard'))
    return render_template('login.html')

@app.route('/get-started', methods=['POST'])
def get_started():
    if request.method == 'POST':
        # Handle form submission - show success message
        flash('Account created successfully! You can now log in.', 'success')
        return render_template('get-started.html')
    return render_template('get-started.html')

@app.route('/peer-evaluation')
def peer_evaluation():
    return render_template('peer-evaluation.html')

#REMINDER - When access to SQL DB -> replace hardcoded choices. 
#Also ensure that you have the correct values to be added to database - 
#there could be more or less than what is provided. Consult Daria/Shriya!!
@app.route('/peer-evalsubmit', methods=['POST'])
def peer_evaluation_submit():
    error = False

    # Student evaluator
    fname = request.form["fname"]
    lname = request.form["lname"]

    if not fname:
        error = True
        flash("Please provide your first name")
    if not lname:
        error = True
        flash("Please provide your last name")

    # Student evaluatee
    fname2 = request.form["fname2"]
    lname2 = request.form["lname2"]

    if not fname2:
        error = True
        flash("Please provide your evaluatee's first name")
    if not lname2:
        error = True
        flash("Please provide your evaluatee's last name")

    # Course ID
    courseID = request.form["courseID"]
    if not courseID:
        error = True
        flash("Please select valid course ID")

    # Completion date Month, Day, Year (Respectively)
    month = request.form["month"]
    day = request.form["day"]
    year = request.form["year"]

    if not month or not day or not year:
        error = True
        flash("Please enter a valid month, day and year for completion date")
    else:
        month = int(month)
        day = int(day)
        year = int(year)

    # Evaluation due date month, day, year (respectively)
    month2 = request.form["month2"]
    day2 = request.form["day2"]
    year2 = request.form["year2"]

    if not month2 or not day2 or not year2:
        error = True
        flash("Please enter a valid month, day and year for due date")
    else:
        month2 = int(month2)
        day2 = int(day2)
        year2 = int(year2)

    #Radio is not included in error checking
    #Values are marked as required -> this is just simpler

    #participation score
    pscore = int(request.form["field1"])
   

    #skillful score
    sscore = int(request.form["field2"])
    

    #feedback score
    fscore = int(request.form["field3"])
    

    #communication score
    cscore = int(request.form["field4"])
    

    #encouragement score
    escore = int(request.form["field5"])

    #integration score 
    iscore = int(request.form["field6"])

    #role score
    rscore = int(request.form["field7"])

    #goals score
    gscore = int(request.form["field8"])

    #reporting score
    rescore = int(request.form["field9"])

    #consistency score
    coscore = int(request.form["field10"])
    
    #optimism score
    oscore = int(request.form["field11"])

    #appropriate assertiveness score
    ascore = int(request.form["field12"])

    #healthy debate score
    dscore = int(request.form["field13"])

    #response to conflict score
    rtcscore = int(request.form["field14"])

    #overall score
    ovscore = int(request.form["field15"])


    #reminders:
    #Log in functionality (Vital) - hardcode if you need to but include this.
    #Do rest of radio forms. ensure conversions to ints
    #Attempt Zappier addition? Do last though.
    if error:
        return render_template('peer-evaluation.html', fname=fname, lname=lname, fname2=fname2, lname2=lname2, courseID=courseID, month=month, day=day, year=year, month2=month2, day2=day2, year2=year2, pscore=pscore, 
                               sscore=sscore, fscore=fscore, cscore=cscore, escore=escore, iscore=rscore, gscore=gscore, rescore=rescore, coscore=coscore, oscore=oscore, ascore=ascore, dscore=dscore, rtcscore=rtcscore, ovscore=ovscore)
    else:
        return render_template('confirmation-screens.html')
    

@app.route('/student-dashboard')
def student_dashboard():
    return render_template('student-dashboard.html')

@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
