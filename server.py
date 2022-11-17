
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
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


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
  word = request.args.get("wsearch")
  print("word line 180", word)

  cursor = g.conn.execute('SELECT p.name, p.price, p.description, p.imageurl FROM Product p, Categories c WHERE p.name LIKE %s or p.description LIKE %s or c.categoryname LIKE %s', word, word, word)

  word_dict = {}
  for result in cursor:
    word_dict.append(result)
  cursor.close()
  context = dict(data = word_dict)
  print("word_dict", word_dict)
  print("word 192", word)
  

  return render_template('search_item.html', word_dict=word_dict, **context)

@app.route('/category', methods=['GET', 'POST'])
def categories_search():
  categoryName = request.args.get('categoryName')
  category = categoryInfo()
  categoryProducts = categoryProductsInfo()
  category_context = dict(data = category)
  category_products_context = dict(productData = categoryProducts)
  print("categories_search line 178")
  print("categories_search cat", category_context)

  return render_template('category.html', category=category, categoryProducts = categoryProducts, **category_context, **category_products_context)

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
  cursor = g.conn.execute('SELECT p.name, p.price, p.description, p.imageurl FROM Product p, Categories c, In_a c1 WHERE c.categoryname = (%s) and c1.productNumber = p.productNumber and c1.categoryid = c.categoryid', categoryName)
  categoryProductsInfoData = {}

  for result in cursor:
    categoryProductsInfoData = {'name':result['name'], 'price':result['price'], 'description':result['description'], 'imageurl':result['imageurl']}
  cursor.close()

  return categoryProductsInfoData

def businessInfo():
  name = request.args.get('businessID')
  cursor = g.conn.execute('SELECT b.businessName, b.socialMedia, o.name, o.school, o.iconImageURL, FROM Business b, Business_owner o, Owns b_o, WHERE b.businessID = (%s) and b.businessID = b_o.businessID and o.email = b_o.email', name)

  businessInfoData = {}
  for result in cursor:
    businessInfoData = {'businessName':result['businessName'], 'socialMedia':result['socialMedia'], 'name':result['name'], 'school':result['school'], 'iconImageURL':result['iconImageURL']}
  cursor.close()

  return businessInfoData

def businessProductsInfo():
  info = request.args.get('businessID')
  cursor = g.conn.execute('SELECT p.name, p.price, p.description, p.imageURL FROM Product p, Business b, Produces b_p, WHERE b.businessID = (%s) and b.businessID = b_p.businessID and p.productNumber = b_p.productNumber', info)

  businessProductsInfoData = {}
  for result in cursor:
    businessProductsInfoData = {'name':result['name'], 'price':result['price'], 'description':result['description'], 'imageURL':result['imageURL']}
  cursor.close()

  return businessProductsInfoData

@app.route('/another')
def another():
  return render_template("another.html")


@app.route('/shopping-cart',methods = ['POST'])

def shopping_cart():
 
  productName = request.form['name']

  return render_template("shopping_cart.html")

@app.route('/products')
def products():
  result = g.conn.execute("SELECT * FROM product p")
  return render_template("product.html", result = result)

@app.route('/sign-up')
def signup():
  return render_template("sign_up.html")
  
  
@app.route('/business/<int:businessID>')
def business(businessID):
  query = ''
  cursor = g.conn.execute(query)
  businessInformation = []
  for result in cursor:
    businessInformation.append(result['Store'], result['Item'], result['Price'])
  return render_template("business.html")


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
