from this import d
from flask import Flask, render_template, request, url_for, flash, redirect
import os
import json
import pendulum
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AH6aSr3q2d5Zf9imZw8N'

user_dict = {}
user_dict['total_points'] = 0
user_dict['transaction_history'] = []
user_dict['payers'] = {}

def generate_random_payers(num_payers=10):
    payer_list = ['DANNON', 'APPLE', 'MICROSOFT', 'JETBLUE', 'DELTA', 'MILLER COORS']
    lower_points = 100
    upper_points = 1000

    time_now = pendulum.now("America/New_York")

    while num_payers > 0:
        num_payers -= 1

        payer = random.choice(payer_list)
        points = random.randint(lower_points, upper_points)
        timestamp = time_now.subtract(seconds=random.randint(60, 5256000)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        output = update_payer(payer, points, timestamp)
    
    return output

def update_payer(payer, points, timestamp):
    # Add to the points total
    user_dict['total_points'] += points
    one_transaction = {}
    one_transaction['payer'] = payer
    one_transaction['points'] = points
    one_transaction['timestamp'] = timestamp
    one_transaction['spent'] = 0

    user_dict['transaction_history'].append(one_transaction)

    # Sort transaction history by the timestamp
    sorted(user_dict['transaction_history'], key = lambda i: i['timestamp'])

    if payer not in user_dict['payers'].keys():
        user_dict['payers'][payer] = 0
    user_dict['payers'][payer] += points

    return json.dumps(user_dict, indent=4)

def spend_payer(points):
    # Test for negative points values
    if points < 0:
        return "Error: Cannot have negative points spend."

    # Test if there are enough points to pay for this spend
    if user_dict['total_points'] < points:
        return "Error: Insufficient points."
    
    # Subtracat from user balance
    user_dict['total_points'] -= points

    # Go through the transactions in chronological order to update the 'spent' values.
    output = {}
    for i in range(len(user_dict['transaction_history'])):
        # Test if the transaction has been consumed.
        one_transaction = user_dict['transaction_history'][i]
        if one_transaction['spent'] < one_transaction['points']:
            # Create the payer if it doesn't exist in the spend report
            if user_dict['transaction_history'][i]['payer'] not in output.keys():
                one_payer = {}
                one_payer['payer'] = one_transaction['payer']
                one_payer['points'] = 0
                output[one_transaction['payer']] = one_payer
            
            # Subtract up to the maximum
            difference = min(points, one_transaction['points'] - one_transaction['spent'])

            points -= difference
            
            # Update what was consumed from the transaction history
            user_dict['transaction_history'][i]['spent'] += difference

            # Update the output
            output[one_transaction['payer']]['points'] -= difference

            # Subtract from the payer balance
            user_dict['payers'][one_transaction['payer']] -= difference

        if points == 0:
            break
    return json.dumps(list(output.values()), indent=4)

def get_balance():
    return json.dumps(user_dict['payers'], indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/balance', methods=['GET'])
def balance():
    return get_balance()

@app.route('/transaction/create', methods=['GET', 'POST'])
def create():
    if request.method == "POST":
        # Test if the inputs are good. 
        output = ""
        if isinstance(request.form['payer'], str):
            # This is a string
            pass
        else:
            output += "The payer value is not a string."
        
        try:
            if isinstance(int(request.form['points']), int):
                # This is an integer number
                pass
            else:
                output += "The points value is not an integer."
        except:
            output += "Cannot coerce points to an integer."

        if isinstance(request.form['timestamp'], str):
            # This is a string
            pass
        else:
            output += "The payer value is not a string."

        if output == "":
            # Inputs passed validation.
            return update_payer(request.form['payer'], int(request.form['points']), request.form['timestamp'])
        else:
            # Something is wrong
            return output
    if request.method == "GET":
        # Check for the test amount
        if "randomize" in request.args:
            return generate_random_payers()

        return render_template('create_transaction.html')
        
@app.route('/transaction/spend', methods=['GET', 'POST'])
def spend():
    if request.method == "GET":
        return render_template('create_spend.html')
    if request.method == "POST":
        # Test if this is an int
        output = ""
        try:
            if isinstance(int(request.form['points']), int):
                # This is an integer number
                pass
            else:
                output += "The points value is not an integer."
        except:
            output += "Cannot coerce points to an integer."

        if output == "":
            # Apply the spending and return the deductions
            return spend_payer(int(request.form['points']))
        else:
            return output

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)