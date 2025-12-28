# Bank Management System 🏦

A full-stack **Bank Management System** built using **Flask (Python)** and **SQL Server**, designed to simulate core banking operations with a clean UI and secure backend logic.

This project demonstrates real-world concepts such as authentication, transaction handling, session management, and role-based workflows.

---

## 🚀 Features

### 🔐 Authentication
- User signup and login
- Secure password hashing using **bcrypt**
- Session-based authentication
- Logout functionality

### 💰 Banking Operations
- Deposit money
- Withdraw money with balance validation
- Fund transfer with confirmation step
- Prevention of invalid operations (negative amount, insufficient balance)

### 📊 Dashboard
- Current balance display
- Inline mini statement (last 3 transactions)
- Full transaction history
- Clean and modern UI layout

### 🧾 Transaction Management
- Deposit, withdraw, and transfer tracking
- Date and time formatted transactions
- Sender and receiver transaction logs

### 🎨 UI / UX
- Responsive design using **Bootstrap**
- Custom CSS styling
- Card-based dashboard layout
- Flash messages for user feedback

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|------------|
| Backend | Python (Flask) |
| Database | SQL Server |
| Frontend | HTML, CSS, Bootstrap |
| Security | bcrypt |
| Version Control | Git & GitHub |

---

## 📂 Project Structure
bank-management-system/
├── app.py
├── database.py
├── config.py
├── static/
│ └── css/
│ └── style.css
├── templates/
│ ├── base.html
│ ├── login.html
│ ├── signup.html
│ ├── dashboard.html
│ ├── deposit.html
│ ├── withdraw.html
│ ├── transfer.html
│ ├── confirm_withdraw.html
│ ├── confirm_transfer.html
│ ├── transactions.html
│ └── mini_statement.html
└── README.md
