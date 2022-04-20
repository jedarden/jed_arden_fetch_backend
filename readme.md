# Jed Arden Points Backend

Here is a single-user Flask-based API implementing the specs found [here](https://fetch-hiring.s3.us-east-1.amazonaws.com/points.pdf) 

# Quickstart

## Prerequisites

* Docker Runtime environment installed
* Web browser
* The test server runs on port 5000, if that is not available, adjust the run command to open a different port. 

## Commands

All commands should be executed in the same folder as the `Dockerfile` file. 

Windows Powershell
```docker image build -t fetch_backend .; docker run -p 5000:5000 fetch_backend;```

OSx / Unix / Linux
```docker image build -t fetch_backend . && docker run -p 5000:5000 fetch_backend```

Once the command is run, navigate to any of the endpoints listed below and enjoy creating and spending points. 

# Schema

This entire platform assumes only one user, and assumes it's in a trusted, secure environment. In practice I'd want to add authentication and more robust logging (IP, user agent, etc) to allow for an audit trail of points being added and subtracted. 

### User
```
user_dict = {}
user_dict['total_points'] = 0
user_dict['transaction_history'] = []
user_dict['payers'] = {}
```

### Transaction
```
one_transaction = {}
one_transaction['payer'] = payer
one_transaction['points'] = points
one_transaction['timestamp'] = timestamp
one_transaction['spent'] = 0
```

### Payer
```
one_payer = {}
one_payer['payer'] = payer
one_payer['points'] = points
```

# Endpoints

## /transactions/create

### GET

A GET request will show a dummy page where points can be added along with a payer and timestamp.

Setting the value "randomize" (E.g. /transactions/create?randomize) will populate 10 random transactions in to the user's points balance. I do want to acknowledge this is not appropriate for sending to production as a user could continue to add transactions without a payer authorizing them. This function / feature is put in more for convenience than anything else. 

### POST

A POST request needs these fields:
* **payer (string)** The name of the payer who is contributing this points.
* **points (integer)** A positive integer representing the number of points to be added to the user's balance
* **timestamp (string)** A string-based timestamp which will be used to sort the transactions for later deduction.

There is some basic type-checking to see if each field has the correct type. It is possible to submit negative points in the event that a payer wants a refund from the user. 



## /transactions/spend

### GET

A GET request will show a dummy page where points can be deducated from a user. 

### POST

A POST request will:
1) Test to see if the value is positive (Prevent potential 'hack' where a user spends negative points effectively inflating their balance)
2) Check to see if the user has sufficient points for the transaction as a whole
3) Iterate through the transactions to deduct points in a First-In-First-Out (FIFO) way. 
4) Generate a list of dicts representing each payer's contribution to the spend


## /balance

### GET

A GET request will respond with the points balance attributed to each payer for this user. 