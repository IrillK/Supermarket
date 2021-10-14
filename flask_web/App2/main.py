from flask import Flask, render_template, request, redirect, make_response
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)

    # text = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return self.title


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return self.password


class Basket(db.Model):
    __tablename__ = 'basket'
    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.String, ForeignKey('user.id'))
    idItem = db.Column(db.Integer, ForeignKey('item.id'))
    count = db.Column(db.Integer, default=1)

    def __repr__(self):
        return self.id


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)


# Блок для корзины
@app.route('/basket')
def basket():
    idUser = request.cookies.get('user')
    res = db.session.query(Item, Basket).filter(Item.id == Basket.idItem).join(Basket, Basket.idUser == idUser).filter(Basket.count > 0).all()
    sum = 0
    for r in res:
        sum += r.Basket.count * r.Item.price
    return render_template('basket.html', data=res, sum=sum)


@app.route('/addItem/<int:id>', methods=['POST', 'GET'])
def addItem(id):
    idUser = request.cookies.get('user')
    basket = Basket.query.filter_by(idItem=id, idUser=idUser).first()
    if basket:
        basket.count = basket.count + 1
    else:
        basket = Basket(idUser=idUser, idItem=id)
    try:
        db.session.add(basket)
        db.session.commit()
        return redirect('/')
    except:
        return "Получилась ошибка"


@app.route('/deleteItem/<int:id>', methods=['POST', 'GET'])
def deleteItem(id):
    idUser = request.cookies.get('user')
    try:
        basket = Basket.query.filter_by(idItem=id, idUser=idUser).first()
        basket.count = basket.count - 1
        db.session.add(basket)
        db.session.commit()
        return redirect('/basket')
    except:
        return "Получилась ошибка"


# Логин и регистрация
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        log = request.form['login']
        password = request.form['password']
        response = db.session.query(User).filter_by(name=log).first()
        # чек пароля
        if str(response) == password:
            if log == "admin":
                resp = setcookie1('/admin', log)
            else:
                resp = setcookie1('/', log)
            return resp
        else:
            return render_template('login.html', mes="Неверный пароль")
    else:
        return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('user', '', 0)
    return resp


def setcookie1(url, name):
    resp = make_response(redirect(url))
    resp.set_cookie('user', name)
    return resp


@app.route('/registr', methods=['POST', 'GET'])
def registr():

    if request.method == "POST":
        log = request.form['login']
        password = request.form['password']
        response = db.session.query(User).filter_by(name=log).first()
        print(response)
        if response is None:
            user = User(name=log, password=password)
            db.session.add(user)
            db.session.commit()
            print('Все хорошо')
            return render_template('registr.html', mes="Регистрация прошла успешно")
        else:
            return render_template('registr.html', mes="Пользователь с этим логином уже зарегистрирован")
    else:
        return render_template('registr.html')


#кабинет администратора
@app.route('/admin', methods=['POST', 'GET'])
def admin():
    items = Item.query.order_by(Item.price).all()
    return render_template('admin.html', data=items)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    item = Item.query.get(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/admin')
    except:
        return "Получилась ошибка"


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        item = Item(title=title, price=price)
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Получилась ошибка"
    else:
        return render_template('create.html')


if __name__ == "__main__":
    app.run(debug=True)
