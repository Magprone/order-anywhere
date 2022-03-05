import os

from flask import Flask, render_template

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
print(f' * SECRET_KEY: {os.environ.get("SECRET_KEY")}')


@app.route('/')
def main_page():
    return render_template('main_page.html', title='order anywhere')


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
