import requests
import time
import os
from dotenv import load_dotenv
import json
load_dotenv()
# Constants

INVESTOR_ID = os.getenv("LEN_DEN_INVESTOR_ID")
URL_FETCH = "https://investor-api.lendenclub.com/api/ims/retail-investor/v5/web/available-loans"
URL_LEND = "https://investor-api.lendenclub.com/api/ims/retail-investor/v5/web/bulk-lending"
URL_BAL = f"https://investor-api.lendenclub.com/api/ios/retail-investor/v5/web/account-status?investor_id={INVESTOR_ID}&partner_code=LDC&partner_id="
HEADERS = {
    'Authorization': os.getenv("LEN_DEN_AUTH"),
    'x-ldc-key': os.getenv("LEN_DEN_KEY"),
    'Content-Type': 'application/json',
    'User-Agent': "PostmanRuntime/7.36.1 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
}
# Headers for authentication
GIT_KEY = os.getenv("LEN_DEN_GIT_ISSUE_KEY")
try:
    rate_str = os.getenv("LENDER_INTEREST_RATE", "40")
    if rate_str and rate_str.strip():
        LENDER_INTEREST_RATE_INNER = float(rate_str)
    else:
        LENDER_INTEREST_RATE_INNER = 40
except (TypeError, ValueError):
    print("Warning: Invalid LENDER_INTEREST_RATE, defaulting to 40.")
    LENDER_INTEREST_RATE_INNER = 40
try:
    rate_str = os.getenv("LENDER_CIBIL_RATE", "750")
    if rate_str and rate_str.strip():
        LENDER_CIBIL_RATE = float(rate_str)
    else:
        LENDER_CIBIL_RATE = 750
except (TypeError, ValueError):
    print("Warning: Invalid LENDER_CIBIL_RATE, defaulting to 750.")
    LENDER_CIBIL_RATE = 750
try:
    rate_str = os.getenv("LENDER_CIBIL_REPEATED_RATE", "770")
    if rate_str and rate_str.strip():
        LENDER_CIBIL_REPEATED_RATE = float(rate_str)
    else:
        LENDER_CIBIL_REPEATED_RATE = 770
except (TypeError, ValueError):
    print("Warning: Invalid LENDER_CIBIL_REPEATED_RATE, defaulting to 770.")
    LENDER_CIBIL_REPEATED_RATE = 770
try:
    rate_str = os.getenv("LENDING_LOAN_AMOUNT", "250")
    if rate_str and rate_str.strip():
        LENDING_LOAN_AMOUNT = float(rate_str)
    else:
        LENDING_LOAN_AMOUNT = 250
except (TypeError, ValueError):
    print("Warning: Invalid LENDING_LOAN_AMOUNT, defaulting to 250.")
    LENDING_LOAN_AMOUNT = 250
try:
    rate_str = os.getenv("LENDING_LOAN_REPEATED_AMOUNT", "1000")
    if rate_str and rate_str.strip():
        LENDING_LOAN_REPEATED_AMOUNT = float(rate_str)
    else:
        LENDING_LOAN_REPEATED_AMOUNT = 1000
except (TypeError, ValueError):
    print("Warning: Invalid LENDING_LOAN_REPEATED_AMOUNT, defaulting to 1000.")
    LENDING_LOAN_REPEATED_AMOUNT = 1000
try:
    rate_str = os.getenv("LENDING_LOANS_SEARCH_LIMIT", "10")
    if rate_str and rate_str.strip():
        LENDING_LOANS_SEARCH_LIMIT = float(rate_str)
    else:
        LENDING_LOANS_SEARCH_LIMIT = 10
except (TypeError, ValueError):
    print("Warning: Invalid LENDING_LOANS_SEARCH_LIMIT, defaulting to 10.")
    LENDING_LOANS_SEARCH_LIMIT = 10

lending_to_repeated = os.getenv("LENDING_TO_REPEATED_PEOPLE", "NO")
LENDING_TO_REPEATED_PEOPLE = lending_to_repeated if lending_to_repeated and lending_to_repeated.strip() else "NO"

check_loans = os.getenv("CHECK_LOANS_IF_BALANCE_IS_ZERO", "NO")
CHECK_LOANS_IF_BALANCE_IS_ZERO = check_loans if check_loans and check_loans.strip() else "NO"

GITHUB_HEADERS = {
    "Authorization": f"token {GIT_KEY}",
    "Accept": "application/vnd.github.v3+json"
}

BODY_FETCH = {
  "filters": ["tenure_2M"
  ],
  "sort_by": [
    "roi_high_low",
    "tenure_low_high"
  ],
  "partner_code": "LDC",
  "investor_id": INVESTOR_ID,
  "partner_id": "",
  "limit": LENDING_LOANS_SEARCH_LIMIT,
  "offset": 0,
  "loan_ids": []
}

BODY_FETCH_REP_LOANS = {
  "filters": [
    "repeated_loans_yes"
  ],
  "sort_by": [
    "roi_high_low",
    "tenure_low_high"
  ],
  "partner_code": "LDC",
  "investor_id": INVESTOR_ID,
  "partner_id": "",
  "limit": LENDING_LOANS_SEARCH_LIMIT,
  "offset": 0,
  "loan_ids": []
}
def limit_array(arr, limit=10):
    return arr[:limit] if len(arr) > limit else arr

def fetch_loans():
    response = requests.request("POST",URL_FETCH, headers=HEADERS, json=BODY_FETCH)
      # Debugging line to see the response content
    # print("response content:", response.text)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch loans:", response.status_code)
        return None

def fetch_loans_rep():
    response = requests.request("POST",URL_FETCH, headers=HEADERS, json=BODY_FETCH_REP_LOANS)
      # Debugging line to see the response content
    # print("response content:", response.text)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch loans:", response.status_code)
        return None
def fetch_balance():
    response = requests.get(URL_BAL, headers=HEADERS)
      # Debugging line to see the response content
    # print("response content:", response.text)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch balance:", response.status_code)
        return None
def lend_to_loans(loan_roi_data,loans_lent,balance,repated_loans=False):
    tmp_string =""
    if repated_loans:
        tmp_string = " (Repeated Loans)"
        body = {
        "partner_code": "LDC",
        "investor_id": INVESTOR_ID,
        "loan_roi_data": loan_roi_data,
        "lending_amount": LENDING_LOAN_REPEATED_AMOUNT
        }
    else:
        body = {
        "partner_code": "LDC",
        "investor_id": INVESTOR_ID,
        "loan_roi_data": loan_roi_data,
        "lending_amount": LENDING_LOAN_AMOUNT
        }


    print("Lending to loans:", loan_roi_data)
    response = requests.post(URL_LEND, headers=HEADERS, json=body)
    # print(response.text)
    new_bal_json = fetch_balance()
    if new_bal_json and new_bal_json.get("success") == 1:
        new_balance = new_bal_json["data"].get("account_balance", 0)
    if response.status_code == 200 and response.json().get("success")== 1:
        print("Successfully lent to loans:", loan_roi_data)
        create_github_issue(f"✅ Lending Success : {loans_lent} loans{tmp_string}", f"Balance before {balance} \nBalance after {new_balance} \nLent to loans{tmp_string}: {loan_roi_data}")
    else:
        tmp_response = response.json().get("message", "No message in response")
        print("Lending failed:", response.status_code, tmp_response)
        create_github_issue(f"❌ Lending Failed : {loans_lent} loans", f"Balance before {balance} \nBalance after {new_balance} \nResponse messgae {tmp_response}\nLent to loans: {loan_roi_data}")


# def check_condition():
#     # Dummy condition logic
#     return True

# def generate_output():
#     # This could be any logic
#     return "This is the function output which will go into the GitHub issue."

def create_github_issue(title, body):
    url = f"https://api.github.com/repos/{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}/issues"
    payload = {
        "title": title,
        "body": body
    }
    response = requests.post(url, headers=GITHUB_HEADERS, json=payload)
    print(url)
    if response.status_code == 201:
        print("✅ Issue created successfully.")
    else:
        print(f"❌ Failed to create issue: {response.status_code}")
        print(response.json())

# Main logic
# if check_condition():
#     output = generate_output()
#     create_github_issue("Auto-generated issue from function output", output)
def run():
    bal_json = fetch_balance()
    if bal_json and bal_json.get("success") == 1:
        balance = bal_json["data"].get("account_balance", 0)
        # print(bal_json)
        print(f"Current balance: {balance}")
        if balance < LENDING_LOAN_AMOUNT:
            print("Insufficient balance to lend. Waiting for next cycle.")
    # while True:
    print("Checking for eligible loans...")
    data = fetch_loans()
    # print(data)
    if data and data.get("success") == 1:
        loans = data["data"]["available_loans_list"]
        to_lend = []
        for loan in loans:
            try:
                roi = float(loan["loan_roi"])
                if roi >= LENDER_INTEREST_RATE_INNER:
                    to_lend.append({
                        "loan_id": loan["loan_id"],
                        "loan_roi": "{:.2f}".format(roi)
                    })
            except Exception as e:
                print("Error processing loan:", e)

        # if to_lend and balance >= 250:
        print(len(to_lend), f"loans found with ROI > {LENDER_INTEREST_RATE_INNER}.")
        max_nunber_of_loans_to_lend = int(balance // LENDING_LOAN_AMOUNT)
        print(f"Max number of loans to lend based on balance: {max_nunber_of_loans_to_lend}")
        if balance >= LENDING_LOAN_AMOUNT and len(to_lend) > 0:
            lend_to_loans(limit_array(to_lend, max_nunber_of_loans_to_lend),len(limit_array(to_lend, max_nunber_of_loans_to_lend)),balance)
        else:
            print(f"No loans found with ROI > {LENDER_INTEREST_RATE_INNER} or Balance is < {LENDING_LOAN_AMOUNT}.")
    else:
        print("No data returned or error from API.")

    # print("Sleeping for 15 minutes...\n")
    # time.sleep(900)  # Sleep for 900 seconds (15 minutes)
def fetch_score(loan_id):
    url = f"https://investor-api.lendenclub.com/api/ims/retail-investor/v5/web/available-loan-details?investor_id={INVESTOR_ID}&partner_code=LDC&loan_id={loan_id}&default_amount=250"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if data and data.get("success") == 1:
            credit_score = data["data"].get("bureau", {}).get("score_range",0)
            loan_details = data["data"].get("loan", {})
            return credit_score
        else:
            return f"Failed to fetch loan details for Loan ID {loan_id}: {data.get('message', 'No message in response')}"
    else:
        return f"Failed to fetch loan details for Loan ID {loan_id}: HTTP {response.status_code}"
def run2():
    bal_json = fetch_balance()
    if bal_json and bal_json.get("success") == 1:
        balance = bal_json["data"].get("account_balance", 0)
        # print(bal_json)
        print(f"Current balance: {balance}")
        if balance < LENDING_LOAN_AMOUNT:
            print("Insufficient balance to lend. Waiting for next cycle.")
        if balance < LENDING_LOAN_AMOUNT:
                if CHECK_LOANS_IF_BALANCE_IS_ZERO == "NO": 
                    return

    print("Checking for eligible loans...")
    data = fetch_loans()
    if data and data.get("success") == 1:
        loans = data["data"]["available_loans_list"]
        to_lend = []
        for loan in loans:
            loan_id = loan["loan_id"]
            loan_score = fetch_score(loan_id)
            if float(loan_score) > LENDER_CIBIL_RATE:
                try:
                    roi = float(loan["loan_roi"])
                    if roi >= LENDER_INTEREST_RATE_INNER:
                        to_lend.append({
                            "loan_id": loan["loan_id"],
                            "loan_roi": "{:.2f}".format(roi)
                        })
                except Exception as e:
                    print("Error processing loan:", e)
        print(len(to_lend), f"loans found with ROI > {LENDER_INTEREST_RATE_INNER} and CIBIL > {LENDER_CIBIL_RATE}.")
        max_nunber_of_loans_to_lend = int(balance // LENDING_LOAN_AMOUNT)
        print(f"Max number of loans to lend based on balance: {max_nunber_of_loans_to_lend}")
        if balance >= LENDING_LOAN_AMOUNT and len(to_lend) > 0:
            lend_to_loans(limit_array(to_lend, max_nunber_of_loans_to_lend),len(limit_array(to_lend, max_nunber_of_loans_to_lend)),balance)
        else:
            print(f"No loans found with ROI > {LENDER_INTEREST_RATE_INNER} or Balance is < {LENDING_LOAN_AMOUNT}.")
    else:
        print("No data returned or error from API.")

def run3():
    bal_json = fetch_balance()
    if bal_json and bal_json.get("success") == 1:
        balance = bal_json["data"].get("account_balance", 0)
        # print(bal_json)
        print(f"Current balance: {balance}")
        if balance < LENDING_LOAN_REPEATED_AMOUNT:
            print("Insufficient balance to lend. Waiting for next cycle.")
        if balance < LENDING_LOAN_AMOUNT:
                if CHECK_LOANS_IF_BALANCE_IS_ZERO == "NO": 
                    return
    print("Checking for eligible loans...")
    data = fetch_loans_rep()
    if data and data.get("success") == 1:
        loans = data["data"]["available_loans_list"]
        to_lend = []
        for loan in loans:
            loan_id = loan["loan_id"]
            loan_score = fetch_score(loan_id)
            if float(loan_score) > LENDER_CIBIL_REPEATED_RATE:
                try:
                    roi = float(loan["loan_roi"])
                    if roi >= LENDER_INTEREST_RATE_INNER:
                        to_lend.append({
                            "loan_id": loan["loan_id"],
                            "loan_roi": "{:.2f}".format(roi)
                        })
                except Exception as e:
                    print("Error processing loan:", e)
        print(len(to_lend), f"repeated loans found with ROI > {LENDER_INTEREST_RATE_INNER} and CIBIL > {LENDER_CIBIL_REPEATED_RATE}.")
        max_nunber_of_loans_to_lend = int(balance // LENDING_LOAN_REPEATED_AMOUNT)
        print(f"Max number of loans to lend based on balance: {max_nunber_of_loans_to_lend}")
        if balance >= LENDING_LOAN_REPEATED_AMOUNT and len(to_lend) > 0:
            lend_to_loans(limit_array(to_lend, max_nunber_of_loans_to_lend),len(limit_array(to_lend, max_nunber_of_loans_to_lend)),balance,repated_loans=True)
        else:
            print(f"No loans found with ROI > {LENDER_INTEREST_RATE_INNER} or Balance is < {LENDING_LOAN_REPEATED_AMOUNT}.")
    else:
        print("No data returned or error from API.")
if __name__ == "__main__":
    # run()
    if LENDING_TO_REPEATED_PEOPLE == "YES":
        run3()
    else:
        run2()
    # run3()
