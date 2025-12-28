from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import random
from database import db_query

app = Flask(__name__)
app.secret_key = "bank-secret-key"


# HOME
@app.route("/")
def home():
    return redirect(url_for("login"))


# LOGIN 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db_query(
            "SELECT password FROM customers WHERE username = ?",
            (username,)
        )

        if not user:
            flash("Invalid username", "danger")
            return redirect(url_for("login"))

        stored_hash = user[0][0]

        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            session["user"] = username
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Wrong password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")

        existing = db_query(
            "SELECT username FROM customers WHERE username = ?",
            (username,)
        )

        if existing:
            flash("Username already exists", "danger")
            return render_template("signup.html")

        hashed_pw = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        while True:
            account_no = random.randint(10000000, 99999999)
            check = db_query(
                "SELECT account_number FROM customers WHERE account_number = ?",
                (account_no,)
            )
            if not check:
                break

        db_query(
            """
            INSERT INTO customers
            (username, password, name, balance, account_number, status)
            VALUES (?, ?, ?, 0, ?, 1)
            """,
            (username, hashed_pw, name, account_no),
            fetch=False
        )

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


# DASHBOARD 
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    user = db_query(
        "SELECT name, balance FROM customers WHERE username = ?",
        (username,)
    )[0]

    name = user[0]
    balance = user[1]

    recent_txn = db_query(
        """
        SELECT TOP 3 transaction_type, amount, transaction_time
        FROM transactions
        WHERE username = ?
        ORDER BY transaction_time DESC
        """,
        (username,)
    )

    return render_template(
        "dashboard.html",
        name=name,
        balance=balance,
        recent_txn=recent_txn
    )


#LOGOUT 
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


#DEPOSIT 
@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            amount = int(request.form.get("amount"))
            if amount <= 0:
                raise ValueError
        except:
            flash("Enter a valid amount", "danger")
            return render_template("deposit.html")

        username = session["user"]

        db_query(
            "UPDATE customers SET balance = balance + ? WHERE username = ?",
            (amount, username),
            fetch=False
        )

        db_query(
            """
            INSERT INTO transactions (username, account_number, transaction_type, amount)
            VALUES (
                ?,
                (SELECT account_number FROM customers WHERE username = ?),
                'Deposit',
                ?
            )
            """,
            (username, username, amount),
            fetch=False
        )

        flash("Amount deposited successfully", "success")
        return redirect(url_for("dashboard"))

    return render_template("deposit.html")


#WITHDRAW
@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    if request.method == "POST":
        try:
            amount = int(request.form.get("amount"))
            if amount <= 0:
                raise ValueError
        except:
            flash("Enter a valid amount", "danger")
            return render_template("withdraw.html")

        balance = db_query(
            "SELECT balance FROM customers WHERE username = ?",
            (username,)
        )[0][0]

        if amount > balance:
            flash("Insufficient balance", "danger")
            return render_template("withdraw.html")

        return render_template("confirm_withdraw.html", amount=amount)

    return render_template("withdraw.html")


@app.route("/confirm-withdraw", methods=["POST"])
def confirm_withdraw():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    amount = int(request.form.get("amount"))

    db_query(
        "UPDATE customers SET balance = balance - ? WHERE username = ?",
        (amount, username),
        fetch=False
    )

    db_query(
        """
        INSERT INTO transactions (username, account_number, transaction_type, amount)
        VALUES (
            ?,
            (SELECT account_number FROM customers WHERE username = ?),
            'Withdraw',
            ?
        )
        """,
        (username, username, amount),
        fetch=False
    )

    flash("Amount withdrawn successfully", "success")
    return redirect(url_for("dashboard"))


#  TRANSFER 
@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "user" not in session:
        return redirect(url_for("login"))

    sender = session["user"]

    if request.method == "POST":
        try:
            receiver_account = int(request.form.get("account"))
            amount = int(request.form.get("amount"))
            if amount <= 0:
                raise ValueError
        except:
            flash("Invalid input", "danger")
            return render_template("transfer.html")

        sender_balance, sender_account = db_query(
            "SELECT balance, account_number FROM customers WHERE username = ?",
            (sender,)
        )[0]

        if amount > sender_balance:
            flash("Insufficient balance", "danger")
            return render_template("transfer.html")

        receiver_data = db_query(
            "SELECT username FROM customers WHERE account_number = ?",
            (receiver_account,)
        )

        if not receiver_data:
            flash("Receiver not found", "danger")
            return render_template("transfer.html")

        receiver_username = receiver_data[0][0]

        return render_template(
            "confirm_transfer.html",
            amount=amount,
            receiver_account=receiver_account,
            receiver_username=receiver_username
        )

    return render_template("transfer.html")


@app.route("/confirm-transfer", methods=["POST"])
def confirm_transfer():
    if "user" not in session:
        return redirect(url_for("login"))

    sender = session["user"]
    amount = int(request.form.get("amount"))
    receiver_account = int(request.form.get("receiver_account"))

    sender_account = db_query(
        "SELECT account_number FROM customers WHERE username = ?",
        (sender,)
    )[0][0]

    receiver_username = db_query(
        "SELECT username FROM customers WHERE account_number = ?",
        (receiver_account,)
    )[0][0]

    db_query(
        "UPDATE customers SET balance = balance - ? WHERE username = ?",
        (amount, sender),
        fetch=False
    )

    db_query(
        "UPDATE customers SET balance = balance + ? WHERE account_number = ?",
        (amount, receiver_account),
        fetch=False
    )

    db_query(
        """
        INSERT INTO transactions (username, account_number, transaction_type, amount, related_account)
        VALUES (?, ?, 'Transfer Sent', ?, ?)
        """,
        (sender, sender_account, amount, receiver_account),
        fetch=False
    )

    db_query(
        """
        INSERT INTO transactions (username, account_number, transaction_type, amount, related_account)
        VALUES (?, ?, 'Transfer Received', ?, ?)
        """,
        (receiver_username, receiver_account, amount, sender_account),
        fetch=False
    )

    flash("Transfer completed successfully", "success")
    return redirect(url_for("dashboard"))


#  TRANSACTIONS 
@app.route("/transactions")
def transactions():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    records = db_query(
        """
        SELECT transaction_type, amount, related_account, transaction_time
        FROM transactions
        WHERE username = ?
        ORDER BY transaction_time DESC
        """,
        (username,)
    )

    return render_template("transactions.html", records=records)


#RUN APP 
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
