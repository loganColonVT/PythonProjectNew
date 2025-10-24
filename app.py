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
@app.route('/peer-evalsubmit', methods=['GET', 'POST'])
def peer_evaluation_submit():
    # Student evaluator
    fname = request.form["fname"]
    lname = request.form["lname"]

    # Student evaluatee
    fname2 = request.form["fname2"]
    lname2 = request.form["lname2"]

    # Course ID
    courseID = request.form["courseID"]

    # Completion date Month, Day, Year (Respectively)
    month = request.form["month"]
    day = request.form["day"]
    year = request.form["year"]

    # Evaluation due date month, day, year (respectively)
    month2 = request.form["month2"]
    day2 = request.form["day2"]
    year2 = request.form["year2"]

    #participation score IMPORTANT REMINDER - ENSURE USER SELECTS
    #A VALUE AND THAT THE VALUE IS CONVERTED TO INT
    pscore = request.form["field1"]

    #skillful score
    sscore = request.form["field2"]

    #feedback score
    fscore = request.form["field3"]

    #communication score
    cscore = request.form["field4"]

    #encouragement score
    escore = request.form["field5"]

    #integration score 
    iscore = request.form["field6"]

    #role score
    rscore = request.form["field7"]

    #goals score
    gscore = request.form["field8"]

    #reporting score
    rescore = request.form["field9"]

    #consistency score
    coscore = request.form["field10"]
    
    #optimism score
    oscore = request.form["field11"]

    #appropriate assertiveness score
    ascore = request.form["field12"]

    #healthy debate score
    dscore = request.form["field13"]

    #response to conflict score
    rtcscore = request.form["field14"]

    #overall score
    ovscore = request.form["field15"]


    #reminders:
    #Log in functionality (Vital) - hardcode if you need to but include this.
    #Do rest of radio forms. ensure conversions to ints
    #Attempt Zappier addition? Do last though.
    return ovscore
    #return render_template('confirmation-screens.html')
    

@app.route('/student-dashboard')
def student_dashboard():
    return render_template('student-dashboard.html')

@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
