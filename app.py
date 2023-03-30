import requests
from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect(database="service_db",
                        user="postgres",
                        password="05062004liza",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form.get("login"):
            username = request.form.get('username')
            password = request.form.get('password')
            if username == '':
                return render_template('login.html', password=password, empty_login=True)
            if password == '':
                return render_template('login.html', username=username, empty_password=True)
            try:
                cursor.execute("SELECT * FROM service.users WHERE login=%s AND password=%s", (str(username),
                                                                                              str(password)))
                records = list(cursor.fetchall())
                return render_template('account.html', full_name=records[0][1], username=records[0][2],
                                       password=records[0][3])
            except:
                return render_template('login.html', not_in_base=True)

        elif request.form.get("registration"):
            return redirect("/registration/")

    return render_template('login.html')


@app.route('/registration/', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        login = request.form.get('login')
        password = request.form.get('password')
        if name == '':
            return render_template('registration.html', login=login, password=password, e_name=True)
        if login == '':
            return render_template('registration.html', name=name, password=password, e_login=True)
        if password == '':
            return render_template('registration.html', name=name, login=login, e_password=True)
        if len(password) != 6:
            return render_template('registration.html', name=name, login=login, len_password=False)
        try:
            cursor.execute("SELECT * FROM service.users WHERE login=%s", (str(login)))
            records = list(cursor.fetchall())
            print('Пользователь с логином', records[0][2], 'уже существует!')
        except:
            cursor.execute('INSERT INTO service.users (full_name, login, password) VALUES (%s, %s, %s);', (str(name), str(login), str(password)))
            conn.commit()

        return redirect("/login/")
    return render_template('registration.html')


if __name__ == "__main__":
    app.run(debug=True)
