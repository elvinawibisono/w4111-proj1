
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, flash, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://ss6179:855@34.75.94.195/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print("request args 106", request.args)



  #
  # example of a database query
  #

 
  
  list_categories = []
  cursor = g.conn.execute("SELECT * FROM Categories")
  print("cursor line 116", cursor)

  for result in cursor:
    list_categories.append(result.categoryname)
  cursor.close()

  list_categoryIDs = []
  secondCursor = g.conn.execute("SELECT categoryid FROM Categories")

  for r in secondCursor:
    list_categoryIDs.append(r.categoryid)
  secondCursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #

  context = dict(data = list_categories)
  secondContext = dict(d = list_categoryIDs)
 
  print("index data", context)

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context, **secondContext)



#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/search_item', methods=['GET', 'POST'])
def search_item():
  word = "%"
  word += request.args.get("wsearch")
  word += "%"
  print("word line 180", word)

  if len(word) == 2:
    flash('Please enter a value!')
    return render_template('index.html')

  cursor = g.conn.execute('SELECT p.name, p.price, p.description, p.imageurl, c.categoryname FROM Product p, Categories c WHERE p.name ILIKE %s or p.description ILIKE %s or c.categoryname ILIKE %s', word, word, word)

  word_dict = {}
  for result in cursor:
    word_dict.update(result)
  
  if len(word_dict) == 0:
    flash('No products found')
    return render_template('index.html')

  
  context = dict(data = word_dict)

  

  return render_template('search_item.html', word_dict=word_dict, **context, cursor=cursor)

@app.route('/category', methods=['GET', 'POST'])
def categories_search():
  categoryName = request.args.get('categoryName')
  category = categoryInfo()
  categoryProducts = categoryProductsInfo()
  category_context = dict(data = category)
  category_products_context = dict(productData = categoryProducts)


  result = g.conn.execute("SELECT * FROM Product p, Categories c, In_a c1, Business b, Produces b_p WHERE c.categoryname = (%s) and c1.productnumber = p.productnumber and c1.categoryid = c.categoryid and b_p.productnumber = p.productnumber and b.businessid = b_p.businessid;", categoryName)

  return render_template('category.html', category=category, categoryProducts = categoryProducts, **category_context, **category_products_context, result=result)

def categoryInfo():
  categoryName = request.args.get('categoryName')
  cursor = g.conn.execute('SELECT c.categoryname, c.description FROM Categories c WHERE c.categoryname = (%s)', categoryName)

  categoryInfoData = {}

  for result in cursor:
    categoryInfoData = {'categoryname':result['categoryname'], 'description':result['description']}
    #categoryInfoData.append(result)
  cursor.close()
  
  return categoryInfoData

def categoryProductsInfo():
  categoryName = request.args.get('categoryName')
  cursor = g.conn.execute('SELECT p.name, p.price, p.description, p.imageurl FROM Product p, Categories c, In_a c1 WHERE c.categoryname = (%s) and c1.productnumber = p.productnumber and c1.categoryid = c.categoryid;', categoryName)
  categoryProductsInfoData = {}

  for result in cursor:
    categoryProductsInfoData = {'name':result['name'], 'price':result['price'], 'description':result['description'], 'imageurl':result['imageurl']}
  cursor.close()

  return categoryProductsInfoData

@app.route('/business')
def business():
  bInfo = businessInfo()
  busData = businessInfoProducts()

  return render_template('business.html', bInfo=bInfo, busData=busData)

def businessInfo():
  businessName = request.args.get('businessName')
  bInfo = g.conn.execute('SELECT * FROM Business b, Business_owner b_o, Owns o WHERE b.businessname = (%s) and b.businessid = o.businessid and o.email = b_o.email', businessName)

  return bInfo

def businessInfoProducts():
  businessName = request.args.get('businessName')
  businessData = g.conn.execute('SELECT * FROM Business b, Product p, Produces b_p WHERE b.businessname = (%s) and b.businessid = b_p.businessid and p.productnumber = b_p.productnumber', businessName)

  return businessData

@app.route('/another')
def another():
  return render_template("another.html")


@app.route('/shopping-cart')
def shopping_cart():

  return render_template("shopping_cart.html")



@app.route('/add-to-cart', methods = ["GET", "POST"])
def add_to_cart():
  productNumber = request.args.get("code")
  quantity = request.args.get("quantity")
  print(quantity)

  result = g.conn.execute("SELECT * FROM product p  WHERE p.productnumber = %s", productNumber)

  #itemArray = {result['productNumber'] : {'name' : result['name'], 'productNumber' : result['productNumber'], 'price' : result['price'], 'image' : row['imageurl']}}

  return render_template("shopping_cart.html", result=result)

@app.route('/payment-confirmation')
def payment():
  
  return render_template("payment_conf.html")

@app.route('/add-payment',methods = ['POST'])
def add_payment(): 
  getpaymentId = g.conn.execute('SELECT paymentid FROM payment ORDER BY payment DESC LIMIT 1')
  print(getpaymentId)
  addpaymentid = int(getpaymentId) + 1
  paymentid = str(addpaymentid)
  cardName= request.form['cardName']
  cardNumber = request.form['cardNumber']
  cvvNumber = request.form['cvvNumber']
  zipCode = request.form['zipCode']
  expDate = request.form['expDate']
  print(expDate)
  g.conn.execute('INSERT INTO Payment (paymentId, cardName, cardNumber , cvvNumber, zipCode, expDate) VALUES (%s, %s, %s, %s, %s,%s)', paymentid, cardName, cardNumber, cvvNumber, zipCode,expDate)
  return redirect("index.html")


@app.route('/products')
def products():
  result = g.conn.execute("SELECT * FROM product p")
  return render_template("product.html", result = result)

@app.route('/sign-up')
def signup():
  return render_template("sign_up.html")


@app.route('/add-customer',methods = ['POST'])
def addcustomer(): 
  name = request.form['name']
  email = request.form['e_mail']
  school = request.form['school']
  imgurl = request.form['img_url']
  address = request.form['address']
  g.conn.execute('INSERT INTO Customer ("name", "email", school, address, iconimagurl) VALUES (%s, %s, %s, %s)', name, email, school, address,imgurl)
  return redirect("index.html")

@app.route('/sign-in', methods =['GET', 'POST'])
def signin():
  if request.method =='POST':
    name = request.form['name']
    email = request.form['e_mail']
  
  return render_template('sign-in.html')
  
# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')



@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
