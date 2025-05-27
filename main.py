import numpy as np
import pickle
from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import mysql.connector

model = pickle.load(open('model.pkl', 'rb'))

# Create application
app = Flask(__name__)

mydb = mysql.connector.connect(host="localhost", user="root", password="", database="heart")
mycursor = mydb.cursor()

# Bind home function to URL
@app.route('/')
def home():
    return render_template('login.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/loginpost', methods=['POST', 'GET'])
def userloginpost():
    global data1
    if request.method == 'POST':
        data1 = request.form.get('uname')
        data2 = request.form.get('password')
        
        print("Username:", data1)  # Debug statement
        print("Password:", data2)  # Debug statement

        if data2 is None:
            return render_template('login.html', msg='Password not provided')

        sql = "SELECT * FROM `users` WHERE `uname` = %s AND `password` = %s"
        val = (data1, data2)

        try:
            mycursor.execute(sql, val)
            account = mycursor.fetchone()  # Fetch one row

            if account:
                # Consume remaining results
                mycursor.fetchall()
                mydb.commit()
                return render_template('index1.html')
            else:
                return render_template('login.html', msg='Invalid username or password')
        except mysql.connector.Error as err:
            print("Error:", err)  # Debug statement
            return render_template('login.html', msg='An error occurred. Please try again.')
@app.route('/NewUser')
def newuser():
    return render_template('NewUser2.html')

@app.route('/reg', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        uname = request.form.get('uname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        password = request.form.get('psw')
        gender = request.form.get('gender')
        sql = "INSERT INTO users (name, uname, email , phone, age, password, gender) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (name, uname, email, phone, age, password, gender)
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('login.html')
    else:
        return render_template('NewUser2.html')

# Bind predict function to URL
@app.route('/showrf')
def showrf():
    return render_template('predict.html')

@app.route('/predictrf', methods=['POST'])
def predictrf():
    # Put all form entries values in a list
    features = [float(i) for i in request.form.values()]
    # Convert features to array
    array_features = [np.array(features)]
    # Predict features
    prediction = model.predict(array_features)

    x = model.predict_proba(array_features)
    pos = x[0][1]
    pos = pos * 100

    # Prepare data for pie chart
    values = [('Positive', pos), ('Negative', 100 - pos)]

    # Generate pie chart
    plt.figure(figsize=(8, 8))
    plt.pie([x[1] for x in values], labels=[x[0] for x in values], autopct='%1.1f%%')
    plt.title('Input Details')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.savefig('static/input_pie_chart.png')  # Save the pie chart as a static file

    # Check the output values and retrieve the result with html tag based on the value
    if pos > 70:
        result_text = 'Probability of having heart disease: '
        risk_text = 'Risk is HIGH'
    elif pos > 40:
        result_text = 'Probability of having heart disease: '
        risk_text = 'Risk is MEDIUM'
    else:
        result_text = 'Probability of having heart disease: '
        risk_text = 'Risk is LOW'

    return render_template('predict1.html', result=result_text, positive=pos, res2=risk_text, plot_image='static/input_pie_chart.png')

if __name__ == '__main__':
    # Run the application
    app.run(debug=True, port=9860)
