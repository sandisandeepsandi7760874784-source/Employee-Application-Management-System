from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)


def db():
    return sqlite3.connect("leave.db")


# Employee page
@app.route("/")
def home():
    return """
    <h1>Employee Leave Management</h1>

    <form action="/apply" method="post">

    Name:
    <input name="name" required>
    <br><br>

    Leave Type:
    <select name="type">
        <option>Casual Leave</option>
        <option>Sick Leave</option>
        <option>Earned Leave</option>
    </select>
    <br><br>

    Start:
    <input type="date" name="start" required>
    <br><br>

    End:
    <input type="date" name="end" required>
    <br><br>

    Days:
    <input type="number" name="days" required>
    <br><br>

    Reason:
    <textarea name="reason" required></textarea>
    <br><br>

    <button type="submit">Apply Leave</button>

    </form>

    <br>

    <a href="/applications">Previous Applications</a>

    <br><br>

    <a href="/manager">Manager Dashboard</a>
    """


# Apply leave
@app.route("/apply", methods=["POST"])
def apply():
    f = request.form

    con = db()

    con.execute(
        """
        INSERT INTO leaves
        (name, type, start, end, days, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f["name"],
            f["type"],
            f["start"],
            f["end"],
            f["days"],
            f["reason"],
            "Pending"
        )
    )

    con.commit()
    con.close()

    print("Leave Applied:", f["name"], "| Status: Pending")

    return redirect("/applications")


# Previous applications
@app.route("/applications")
def applications():

    con = db()

    rows = con.execute(
        "SELECT * FROM leaves"
    ).fetchall()

    con.close()

    html = "<h1>Previous Applications</h1>"

    html += """
    <table border="1">
    <tr>
    <th>Name</th>
    <th>Leave Type</th>
    <th>Start</th>
    <th>End</th>
    <th>Days</th>
    <th>Reason</th>
    <th>Status</th>
    </tr>
    """

    for r in rows:

        html += f"""
        <tr>
        <td>{r[1]}</td>
        <td>{r[2]}</td>
        <td>{r[3]}</td>
        <td>{r[4]}</td>
        <td>{r[5]}</td>
        <td>{r[6]}</td>
        <td>{r[7]}</td>
        </tr>
        """

    html += """
    </table>

    <br>

    <a href="/">Employee Page</a>

    <br><br>

    <a href="/manager">Manager Dashboard</a>
    """

    return html


# Manager dashboard
@app.route("/manager")
def manager():

    con = db()

    rows = con.execute(
        "SELECT * FROM leaves"
    ).fetchall()

    con.close()

    html = "<h1>Manager Dashboard</h1>"

    html += """
    <table border="1">
    <tr>
    <th>Name</th>
    <th>Leave Type</th>
    <th>Days</th>
    <th>Status</th>
    <th>Action</th>
    </tr>
    """

    for r in rows:

        html += f"""
        <tr>
        <td>{r[1]}</td>
        <td>{r[2]}</td>
        <td>{r[5]}</td>
        <td>{r[7]}</td>

        <td>
        <a href="/approve/{r[0]}">Approve</a>
        |
        <a href="/reject/{r[0]}">Reject</a>
        </td>

        </tr>
        """

    html += """
    </table>

    <br>

    <a href="/">Employee Page</a>
    """

    return html


# Approve leave
@app.route("/approve/<int:id>")
def approve(id):

    con = db()

    con.execute(
        "UPDATE leaves SET status='Approved' WHERE id=?",
        (id,)
    )

    con.commit()
    con.close()

    print("Leave Approved:", id)

    return redirect("/manager")


# Reject leave
@app.route("/reject/<int:id>")
def reject(id):

    con = db()

    con.execute(
        "UPDATE leaves SET status='Rejected' WHERE id=?",
        (id,)
    )

    con.commit()
    con.close()

    print("Leave Rejected:", id)

    return redirect("/manager")


# Start application
if __name__ == "__main__":

    con = db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS leaves(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            start TEXT,
            end TEXT,
            days INTEGER,
            reason TEXT,
            status TEXT
        )
    """)

    con.commit()
    con.close()

    print("Employee Leave Management System Started")

    app.run(debug=True, port=5001)