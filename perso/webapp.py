import time
from flask import *
import sys
import psycopg2	
#NE PAS MODIFIER LA LIGNE SUIVANTE
app = Flask(__name__)

#Hello world basique
@app.route("/")
def hello(error=None):
	#return app.send_static_file("form.html")
	return render_template("form.html",hasError=error, rows=liste_mail())

def display_client(prenom_client):
	# Try to connect to an existing database
	print('Trying to connect to the database')
	try:
		conn = psycopg2.connect("host=dbserver dbname=kservical user=kservical")
		print('Connected to the database')
		cur = conn.cursor()
		command = 'select * FROM hotelbis.client WHERE prenom =\'' + prenom_client + '\';'
		#command = 'select * FROM hotelbis.client;'
		print('Trying to execute command: ' + command)
		try:
			# Query the database and obtain data as Python objects
			cur.execute(command)
			print("execute ok")
			#retrieve all tuple
			rows = cur.fetchall() #rows => tableau (les lignes du résultat) de listes (les différents attributs du résultat)
			print("fetchall ok")
			page = ''
			client = rows[0]
			print(rows)
			print(client)
			page = prenom_client+ " " + client[1] + " " +client[3]
			# Close communication with the database
			cur.close()
			conn.close()
			print('Returning page ' + page)
			return page
		except Exception as e :
			#return "error when running command: " + command + " : " + str(e)
			return redirect (url_for('hello', error=str(e)))
	except Exception as e :
		return "Cannot connect to database: " + str(e)

def list_mail():
	print('Trying to connect to the database')
	try:
		conn = psycopg2.connect("host=dbserver dbname=kservical user=kservical")
		print('Connected to the database')
		cur = conn.cursor()
		command = 'select mail FROM hotelbis.client;'
		#command = 'select * FROM hotelbis.client;'
		print('Trying to execute command: ' + command)
		try:
			# Query the database and obtain data as Python objects
			cur.execute(command)
			print("execute ok")
			#retrieve all tuple
			rows = cur.fetchall() #rows => tableau (les lignes du résultat) de listes (les différents attributs du résultat)		
			# Close communication with the database
			cur.close()
			conn.close()
			print('Returning page ' + page)
			return rows
		except Exception as e :
			#return "error when running command: " + command + " : " + str(e)
			return redirect (url_for('hello', error=str(e)))
	except Exception as e :
		return "Cannot connect to database: " + str(e)

#Hello world avec récupération de paramètres
@app.route("/hello/<name>")
def hello_name(name):
	data= "<b>Hello "+name+"</b>. Nous sommes le " + time.strftime("%d/%m/%Y")
	return data

#after_form
@app.route('/after_form', methods=['POST'])
def after_form():
	print("I got it!")
	#return hello_name(request.form['prenom'])
	return display_client(request.form['prenom'])

#NE SURTOUT PAS MODIFIER     
if __name__ == "__main__":
   app.run(debug=True)


