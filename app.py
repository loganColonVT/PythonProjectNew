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
    pscore = request.form["field1"]
    if not pscore:
        error = True
   

    #skillful score
    sscore = request.form["field2"]
    if not sscore:
        error = True    

    #feedback score
    fscore = request.form["field3"]
    if not fscore:
        error = True 

    #communication score
    cscore = request.form["field4"]
    if not cscore:
        error = True

    #encouragement score
    escore = request.form["field5"]
    if not escore:
        error = True

    #integration score 
    iscore = request.form["field6"]
    if not iscore:
        error = True

    #role score
    rscore = request.form["field7"]
    if not rscore:
        error = True

    #goals score
    gscore = request.form["field8"]
    if not gscore:
        error = True

    #reporting score
    rescore = request.form["field9"]
    if not rescore:
        error = True

    #consistency score
    coscore = request.form["field10"]
    if not coscore:
        error = True
    
    #optimism score
    oscore = request.form["field11"]
    if not oscore:
        error = True

    #appropriate assertiveness score
    ascore = request.form["field12"]
    if not ascore:
        error = True

    #healthy debate score
    dscore = request.form["field13"]
    if not dscore:
        error = True

    #response to conflict score
    rtcscore = request.form["field14"]
    if not rtcscore:
        error = True

    #overall score
    ovscore = request.form["field15"]
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

if __name__ == '__main__':
    app.run(debug=True, port=5002)
