from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import yaml
from flask_mail import Mail

app = Flask(__name__)
db = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['local_server']['host'] if not db['hosted'] else db['host_server']['host']
app.config['MYSQL_USER'] = db['local_server']['user'] if not db['hosted'] else db['host_server']['user']
app.config['MYSQL_PASSWORD'] = db['local_server']['password'] if not db['hosted'] else db['host_server']['password']
app.config['MYSQL_DB'] = db['local_server']['database_name'] if not db['hosted'] else db['host_server']['database_name']
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = db['gmail']['address']
app.config['MAIL_PASSWORD'] = db['gmail']['password']
mail = Mail(app)
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html', params=db['params'])


@app.route('/about')
def about():
    return render_template('about.html', params=db['params'])


@app.route('/contact', methods=["GET", "POST"])
def contact():
    if(request.method == "POST"):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contacts(name,email,phone,message) VALUES(%s,%s,%s,%s)",
                    (name, email, phone, message))
        mysql.connection.commit()
        cur.close()
        mail.send_message(
            "A message from "+name,
            sender=email,
            recipients=[
                db['gmail']['address']
            ],
            body=message + "\n\n" + email + '\n' + phone,
        )
    return render_template('contact.html', params=db['params'])


@app.route('/post/<string:slug>', method=["GET"])
def post():
    return render_template('post.html', params=db['params'])


app.run(debug=True)
