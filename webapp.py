from flask import *
import sys
import psycopg2
from datetime import *
from pymongo import MongoClient
import json
mgclient= MongoClient("mongodb://mongodb.emi.u-bordeaux.fr:27017/admin")
mgdb = mgclient.test
res = mgdb.restaurants.insert_one({'x': 1})



#NE PAS MODIFIER LA LIGNE SUIVANTE
app = Flask(__name__)
app.secret_key = 'some_secret'

#Hello world basique
@app.route("/")
def form_date(error=None):
    dic={}
    global dateDuJour
    dateDuJour= date.today()
    flash('date du jour : ' + dateDuJour.isoformat())
    global dateTest    
    dateTest= (datetime.strptime('03/03/2018',"%d/%m/%Y")).date()
    print(type(dateTest))
    flash('date test : ' +dateTest.isoformat())
    flash('test OK : ' + str(dateDuJour < dateTest))
    flash('mongo object : ' + str(res))
    return render_template("select_date.html", hasError=error, dico=json.dumps(dic))

@app.route("/select_chambre", methods=['POST'])
def after_form_date(error=None):
    dic=json.loads(request.form['dico'])
    dic['debut']=request.form['debut']
    dic['fin']=request.form['fin']
    print("function after_form_date")
    print(request.form['debut'])
    return render_template("chambre.html", hasError=error, rows=after_choix_dates(dic['debut'],dic['fin']),dico=json.dumps(dic))

def after_choix_dates(debut,fin):
    # Try to connect to an existing database
    print('Function after_choix_date debut = ' + debut)
    try:
        conn = psycopg2.connect("host=dbserver dbname=kservical user=kservical")
        print('Connected to the database')
        cur = conn.cursor()
        #command = 'select num_client from hotelbis.reservation except select num_client from hotelbis.reservation where date_debut <\'' + fin + '\' AND date_fin >\'' + debut + '\';'
        command= 'select numero from hotelbis.chambre except select numero from hotelbis.reservation where date_debut <=\'' + fin +'\' AND date_fin >=\'' + debut + '\';'
        
        print('Trying to execute command: ' + command)
        try:
            # Query the database and obtain data as Python objects
            cur.execute(command)
            print("execute ok")
            #retrieve all tuple
            rows = cur.fetchall() #rows => tableau (les lignes du résultat) de listes (les différents attributs du résultat)
            print(rows)
            cur.close()
            conn.close()
            return rows
        except Exception as e :
            # return "error when running command: " + command + " : " + str(e)
            return redirect(url_for('hello', error=str(e)))
    except Exception as e :
        return "Cannot connect to database: " + str(e)


@app.route("/recapitulatif_chambre",methods=['POST'])
def recap_chambre(error=None):
    dic=json.loads(request.form['dico'])
    dic['numero']=request.form['numero']
    print('recap_chambre')
    return render_template("recap_chambre.html",hasError=error,desc=mgdb_display_chambre(dic['numero']), rows=chambre_prix(request.form['numero']),dico=json.dumps(dic))

def chambre_prix(numero):
    # Try to connect to an existing database
    print('chambre_prix')
    print(numero)
    try:
        conn = psycopg2.connect("host=dbserver dbname=kservical user=kservical")
        cur = conn.cursor()
        print("database connect : ok!")
        command = 'select * from hotelbis.chambre where numero =\'' + numero + '\';'
        print(command)
        try:
            cur.execute(command)		
            rows = cur.fetchall()
            print(rows)
            cur.close()
            conn.close()
            return rows
        except Exception as e :
            # return "error when running command: " + command + " : " + str(e)
            return redirect(url_for('hello', error=str(e)))
    except Exception as e :
        return "Cannot connect to database: " + str(e)


@app.route("/select_client", methods=['POST'])
def select_client(error=None):
    dic=json.loads(request.form['dico'])
    print("function select_client")
    return render_template("display_client.html", hasError=error, rows=liste_mail(),dico=json.dumps(dic))

def liste_mail():
    # Try to connect to an existing database
    print('liste_mail')
    try:
        conn = psycopg2.connect("host=dbserver dbname=kservical user=kservical")
        cur = conn.cursor()
        print("database connect : ok!")
        command = 'select mail,num_client from hotelbis.client;'
        try:
            cur.execute(command)
            rows = cur.fetchall()
            print(rows)
            cur.close()
            conn.close()
            return rows
        except Exception as e :
            # return "error when running command: " + command + " : " + str(e)
            return redirect(url_for('hello', error=str(e)))
    except Exception as e :
        return "Cannot connect to database: " + str(e)


@app.route("/recap_client", methods=['POST'])
def recap_client(error=None):
    dic=json.loads(request.form['dico'])
    print("recap_client")
    dic['password']=request.form['password']
    dic['mail']=request.form['mail']
    print(dic['password'])
    print(dic['mail'])
    return render_template("recap_client.html",hasError=error,rows=authentification(dic,dic['mail'],dic['password']),dico=json.dumps(dic))

def authentification(dic,mail,password):
    # Try to connect to an existing database
    print(dic)
    print('authentification')
    try:
        conn = psycopg2.connect("host=dbserver dbname=kservical user=kservical")
        cur = conn.cursor()
        print("database connect : ok!")
        command = 'select * from hotelbis.client where mail=\'' + mail + '\' AND password=\'' + password + '\';'
        try:
            cur.execute(command)
            rows = cur.fetchall()
            print(rows[0][0])
            dic['num_client']=rows[0][0]
            cur.close()
            conn.close()
            return rows
        except Exception as e :
            # return "error when running command: " + command + " : " + str(e)
            return redirect(url_for('hello', error=str(e)))
    except Exception as e :
        return "Cannot connect to database: " + str(e)

@app.route("/confirmation", methods=['POST'])
def reservation_final(error=None):
    dic=json.loads(request.form['dico'])
    print("recapt")
    print(dic['num_client'])
    print(dic)
    return render_template("confirmation.html",hasError=error,dico=json.dumps(dic), rows=add_reservation(dic['num_client'],dic['numero'],dic['debut'],dic['fin']))

def add_reservation(num_client,numero,debut,fin):
    # Try to connect to an existing database
    print('add_reservation')
    try:
        conn = psycopg2.connect("host=dbserver dbname=kservical user=kservical")
        cur = conn.cursor()
        # command = 'test'
        print(type(debut))
        #debut=(datetime.strptime(str(debut),"%d/%m/%Y").date())
        command = 'insert into hotelbis.reservation (num_facture,num_client,numero,date_debut,date_fin,reglee) VALUES (default,\'' + str(num_client) +'\',\'' + str(numero) + '\',\'' + debut + '\',\'' + fin  + '\', FALSE );'
        # command = 'insert into hotelbis.reservation (num_facture,num_client,numero,date_debut,date_fin,reglee) VALUES (default,\'' + num_client +'\',\'' + numero + '\',\'' + debut + '\',\'' + fin + '\', FALSE );'
        print('Connected to the database')
        print('Trying to execute command: ' + command)
        try:
            #Query the database and obtain data as Python objects
            cur.execute(command)
            cur.close()
            conn.commit()
            conn.close()
            print("add")
        except Exception as e :
            print("erreur")
            return redirect(url_for('hello', error=str(e)))
    except Exception as e :
        return "Cannot connect to database: " + str(e)



@app.route("/inscription", methods=['POST'])
def inscription(error=None):
    dic=json.loads(request.form['dico'])
    print("inscription")
    return render_template("inscription.html",hasError=error,dico=json.dumps(dic))

@app.route("/creation_compte", methods=['POST'])
def creation_compte(error=None):
    print("creation_compte")
    dic=json.loads(request.form['dico'])
    dic['insert_nom']=request.form['insert_nom']
    dic['insert_prenom']=request.form['insert_prenom']
    dic['insert_mail']=request.form['insert_mail']
    dic['insert_password']=request.form['insert_password']
    print("recapitulatif")
    return render_template("compte_cree.html", hasError=error, rows=add_inscription(dic['insert_nom'],dic['insert_prenom'],dic['insert_mail'],dic['insert_password']), dico=json.dumps(dic))
    

def add_inscription(nom,prenom,mail,password):
    # Try to connect to an existing database
    print('function add_inscription')
    print('Trying to connect to the database')
    try:
        conn = psycopg2.connect("host=dbserver dbname=kservical user=kservical")
        print('Connected to the database')
        cur = conn.cursor()
        command = 'insert into hotelbis.client (num_client,nom,prenom,mail,password) VALUES(default ,\'' + nom + '\',\'' + prenom + '\',\'' + mail + '\',\'' + password +'\');'
        #command = 'insert into hotelbis.client VALUES(default ,%s,%s,%s),(nom,prenom,mail)'
        print('Trying to execute command: ' + command)
        try:
            # Query the database and obtain data as Python objects
            cur.execute(command)
            cur.close()
            conn.commit()
            conn.close()
        except Exception as e :
            # return "error when running command: " + command + " : " + str(e)
            print("erreur")
            return redirect(url_for('hello', error=str(e)))
    except Exception as e :
        return "Cannot connect to database: " + str(e)



def get_mg_db():
    db=getattr(g, '_mg_database', None)
    if db is None:
        db= g._mg_database = MongoClient("mongodb://mongodb.emi.u-bordeaux.fr:27017").kservical
    return db

def mgdb_display_chambre(idechambre):
    print("mongo display chambre")
    mgdb = get_mg_db()
    request= mgdb.chambres.find()
    print(request)
    if mgdb:
        return mgdb.chambres.find({"chambre_id":float(idechambre)})
    else:
        return None

def test_mongodb(mgdb):
    mgdb = get_mgdb()
    result = mgdb = mgdb.chambres.insert([
        {
            "chambre_id": 1,
            "nom": "chambre 1",
            "vue":"Ocean",
            "couchage":"Lit double",
            "salle de bain":{
                "douche":"Italienne",
                "baignoire":"à bulles"
		}	
        },
        {
            "chambre_id": 2,
            "nom": "chambre 2",
            "vue":"Cuisine",
            "couchage":"Lit simple",
            "salle de bain":{
                "douche":"à l'ancienne",
                "baignoire":"ovale"
                }	
        },        
        {
            "chambre_id": 3,
            "nom": "chambre 3",
            "vue":"jardin",
            "couchage":"Lit double",
            "salle de bain":{
                "douche":"aucun",
                "baignoire":"angle"
                }	
        },
        {
            "chambre_id": 4,
            "nom": "chambre 4",
            "vue":"jardin",
            "couchage":"Lit double",
            "salle de bain":{
                "douche":"aucun",
                "baignoire":"angle"
                }	
        }


])	
	

#NE SURTOUT PAS MODIFIER     
if __name__ == "__main__":
    app.run(debug=True)
