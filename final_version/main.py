from flask import Flask, render_template, request, url_for, render_template, redirect, session
import sqlite3 as sql
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

#table User
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String(100))
	lname = db.Column(db.String(100))
	email = db.Column(db.String(100), unique=True)
	uname = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	level = db.Column(db.String(100))

	def __init__(self, fname, lname, email, uname, password, level):
		self.fname = fname
		self.lname = lname
		self.email = email
		self.uname = uname
		self.password = password
		self.level = level


#table Book
class Book(db.Model):
   __tablename__ = "book"

   id= db.Column(db.Integer, primary_key=True)
   bookname = db.Column(db.Text)
   author = db.Column(db.Text)
   ISBN = db.Column(db.Text)
   publisher = db.Column(db.Text)
   catalog = db.Column(db.Text)
   price = db.Column(db.Float)
   arrivedate =  db.Column(db.Date)
   quantity = db.Column(db.Integer)

   def __init__(self, bookname, author, ISBN, publisher, catalog, price, arrivedate, quantity):
       self.bookname = bookname
       self.author = author
       self.ISBN = ISBN
       self.publisher = publisher
       self.catalog = catalog
       self.price = price
       self.arrivedate = arrivedate
       self.quantity = quantity

   def __repr__(self):
       return f"book: {self.id},{self.bookname},{self.author},{self.ISBN},{self.publisher},{self.catalog},{self.price},{self.arrivedate}, {self.quantity}"

#table Orders
class Orders(db.Model):
   __tablename__ = "orders"

   id= db.Column(db.Integer, primary_key=True)
   bookname = db.Column(db.Text)
   ISBN = db.Column(db.Text)
   price = db.Column(db.Integer)
   buyer = db.Column(db.Text)
   orderdate = db.Column(db.DateTime)

   def __init__(self, bookname, ISBN, price, buyer, orderdate):
       self.bookname = bookname
       self.ISBN = ISBN
       self.price = price
       self.buyer = buyer
       self.orderdate = orderdate

   def __repr__(self):
       return f"order: {self.id},{self.bookname},{self.ISBN},{self.price},{self.buyer},{self.orderdate}"


db.create_all()

ADMIN_PASSWORD = 'admin'

#
@app.route('/')
def login():
	return render_template('login.html')


@app.route('/register', methods = ['POST', 'GET'])
def register():
	if request.method == 'POST':
		if request.form["action"]=="Join Now!":
			try:
				password = request.form['password']
				confirm_password = request.form['confirm_password']
				myLevel='user'
				if request.form['adminpassword']==ADMIN_PASSWORD:
					myLevel='manager'
				if password == confirm_password:
					db.session.add(User(fname=request.form['fname'], lname=request.form['lname'], uname=request.form['uname'],
					    email=request.form['email'], password=request.form['password'], level = myLevel))
					db.session.commit()
					return render_template('thankyou.html')
				else:
					return render_template('register.html',msg="Enter the password again!")
			except:
				return render_template('register.html',msg="Something Wrong!")

		elif request.form["action"]=="Sign In":
			return render_template('login.html')
		else:
			return render_template('register.html',msg="Something Wrong!")
	else:
		pass



@app.route('/wait', methods = ['POST', 'GET'])
def wait():
	if request.method == 'POST':
		if request.form["action"]=="Log In":
			try:
				uname = request.form['uname']
				password = request.form['password']
					data = User.query.filter_by(uname=uname, password=password).first()
				session['level'] = data.level
				session['username'] = uname
				print('!!!!!',data)
				if data is not None and uname!='' and password!='':
					session['logged_in'] = True
					return redirect(url_for('home'))
				else:
					return render_template('login.html',msg="Something wrong with Username or Password.")
			except:
				return render_template('login.html',msg="Something wrong with input")

		elif request.form["action"]=="register":
			return render_template('register.html')

		elif request.form["action"]=="register":
			return render_template('home.html')

	else:
			return render_template('login.html')


@app.route('/wait1', methods = ['POST', 'GET'])
def wait1():
	if request.method == 'POST':
		try:
			if request.form["action"]=="Log In Now!":
				return render_template('login.html')
		except:
			return render_template('login.html')

@app.route('/admin', methods = ['POST', 'GET'])
def admin():
	return render_template('home.html')

@app.route('/home', methods = ['POST', 'GET'])
def home():
    books = Book.query.all()
    availBooks = []
    for book in books:
        if book.quantity > 0:
            availBooks.append(book)
    return render_template('home.html', myLevel = session['level'], myBooks = availBooks)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	session['logged_in'] = False
	return render_template('login.html')

@app.route('/addBook')
def addBook():
	return render_template('addBook.html')

@app.route('/addBookSubmit')
def addBookSubmit():
    bookname = request.args.get('bookname')
    author = request.args.get('author')
    ISBN = request.args.get('ISBN')
    publisher = request.args.get('publisher')
    catalog = str(request.args.get('catalog'))
    price = float(request.args.get('price'))
    arrive_year = int(request.args.get('arrivedate')[:4])
    arrive_month = int(request.args.get('arrivedate')[5:7])
    arrive_date = int(request.args.get('arrivedate')[8:10])
    arrivedate =datetime(arrive_year,arrive_month,arrive_date)
    quantity =  int(request.args.get('quantity'))

    a1 = Book(bookname,author,ISBN,publisher,catalog,price,arrivedate,quantity)
    db.session.add(a1)
    db.session.commit()
    return render_template('addbookcomplete.html')

@app.route('/updateBook')
def updateBook():
	return render_template('updatebookpre.html')

@app.route('/updateBookPre')
def updateBookPre():
    ISBN = request.args.get('ISBN')
    data = Book.query.filter_by(ISBN=ISBN).first()
    return render_template('updatebookedit.html', myBook = data)


@app.route('/updateBookSubmit')
def updateBookSubmit():
    id = int(request.args.get('id'))
    book = Book.query.get(id)
    book.bookname = request.args.get('bookname')
    book.author = request.args.get('author')
    book.ISBN = request.args.get('ISBN')
    book.publisher = request.args.get('publisher')
    book.catalog = request.args.get('catalog')
    book.price = float(request.args.get('price'))
    arrive_year = int(request.args.get('arrivedate')[:4])
    arrive_month = int(request.args.get('arrivedate')[5:7])
    arrive_date = int(request.args.get('arrivedate')[8:10])
    arrivedate = datetime(arrive_year,arrive_month,arrive_date)
    book.arrivedate =datetime(arrive_year,arrive_month,arrive_date)
    book.quantity =  int(request.args.get('quantity'))
    db.session.add(book)
    db.session.commit()
    return render_template('updatebookpre.html')


@app.route('/orderStatus')
def orderStatus():
    return render_template('orderstatuspre.html')

@app.route('/orderStatusSubmit')
def orderStatusSubmit():
    start_year = int(request.args.get('startdate')[:4])
    start_month = int(request.args.get('startdate')[5:7])
    start_date = int(request.args.get('startdate')[8:10])
    startDate = datetime(start_year,start_month,start_date)
    end_year = int(request.args.get('enddate')[:4])
    end_month = int(request.args.get('enddate')[5:7])
    end_date = int(request.args.get('enddate')[8:10])
    endDate = datetime(end_year,end_month,end_date)
    data = Orders.query.filter(Orders.orderdate>startDate).filter(Orders.orderdate<endDate).all()
    return render_template('orderStatus.html', myOrders = data)


@app.route('/search')
def search():
    c = str(request.args.get('catalog')).strip()
    resultset = Book.query.filter(Book.catalog==c)
    books = resultset.all()
    return render_template('searchResult.html', myBooks = books)

@app.route('/cart')
def cart():
    c = str(request.args.get('books'))
    ids = c.replace('\'','').split(',')
    books =[]
    for id in ids:
        resultset = Book.query.filter(Book.id==int(id))
        all = resultset.all()
        books.extend(all)
    totalPrice = 0
    for book in books:
        totalPrice = totalPrice + book.price
    return render_template('cart.html', myBooks = books, myPrice = totalPrice, myIds = c)

@app.route('/cartSubmit')
def cartSubmit():
    c = str(request.args.get('books'))
    ids = c.replace('\'','').split(',')
    books =[]
	#update books and insert order table
    result = 'false'
    for id in ids:
        resultset = Book.query.filter(Book.id==int(id))
        all = resultset.all()
        book = all[0]
        book.quantity = book.quantity - 1
        db.session.add(book)
        db.session.commit()
        bookname = book.bookname
        ISBN = book.ISBN
        price = book.price
        orderdate = datetime.now()
        buyer = session['username']
        order = Orders(bookname,ISBN,price, buyer, orderdate)
        db.session.add(order)
        db.session.commit()
        result = 'sucess'
    return render_template('cartcomplete.html', myresult = result)

@app.route('/orderNotify')
def orderNotify():
    newdate = datetime.now()-timedelta(minutes=5000)
    data = Orders.query.filter(Orders.orderdate>newdate).all()
    if len(data) ==0:
       return '';
    result = " New orders:"
    for order in data:
        result = result + "<li>[book name("+order.bookname+"), ordered time("+order.orderdate.strftime("%m/%d/%Y, %H:%M:%S")+")]</li> <br/> ";
    return result


if __name__ == '__main__':
	app.secret_key = "ThisIsNotASecret:p"
	db.create_all()
	app.run(debug=True)
