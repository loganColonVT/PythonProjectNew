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

@app.route('/get-started', methods=['GET', 'POST'])
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
def peer_evaluation():
    # Student evaluator
    fname = request.args["fname"]
    lname = request.args["lname"]

    # Student evaluatee
    fname2 = request.args["fname2"]
    lname2 = request.args["lname2"]

    # Course ID
    courseID = request.args["courseID"]

    # Completion date Month, Day, Year (Respectively)
    month = request.args["month"]
    day = request.args["day"]
    year = request.args["year"]

    # Evaluation due date month, day, year (respectively)
    month2 = request.args["month2"]
    day2 = request.args["day2"]
    year2 = request.args["year2"]

    
    return render_template('confirmation-screens.html')
    

@app.route('/student-dashboard')
def student_dashboard():
    return render_template('student-dashboard.html')

@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
