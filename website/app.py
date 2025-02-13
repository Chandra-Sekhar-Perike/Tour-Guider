import sqlite3 as sql
import json
import os
import sys
import urllib.request
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for, redirect, flash, redirect

conn = sql.connect("tour_places.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS images_data(name VARCHAR, country VARCHAR, state VARCHAR, district VARCHAR, details VARCHAR, viewpoints VARCHAR, location VARCHAR)")
c.execute("CREATE TABLE IF NOT EXISTS sign_up(loginID VARCHAR, password VARCHAR)")
conn.commit()
c.close()
conn.close()

search = ""
app = Flask(__name__)
app.secret_key = "__privatekey"

allowed_extensions = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route("/")
def first():
	return render_template("index.html")

@app.route("/home", methods = ["GET", "POST"])
def home():
	if(request.method == "POST"):
		search = request.form["search"]
		conn = sql.connect("tour_places.db")
		c = conn.cursor()
		c.execute("SELECT name FROM images_data WHERE name == '"+search+"' OR country == '"+search+"' OR state == '"+search+"' OR district == '"+search+"'")
		global r
		r = c.fetchall()
		if(len(r) == 0):
			flash("No results found")
		else:
			return redirect(url_for("results"))
	return render_template("home.html")

@app.route("/results", methods = ["GET", "POST"] )
def results():
	names = []
	for i in range(len(r)):
		for j in range(len(r[i])):
			names.append(r[i][j])
	if(request.method == "POST"):
		global name
		name = request.form["name"]
		if(request.form["name"] != None):
			return redirect(url_for("display"))
	return render_template("results.html", names = names)

@app.route("/display")
def display():
	image_paths = []
	path = name+"/"
	image_names = os.listdir("./static/"+path+"/")
	for image_name in image_names:
		image_paths.append(path+image_name)
	conn = sql.connect("tour_places.db")
	c = conn.cursor()
	c.execute("SELECT name, country, state, district, details, viewpoints, location FROM images_data WHERE name == '"+name+"'")
	paragraphs = c.fetchall()
	return render_template("display.html", image_paths = image_paths, paragraphs = paragraphs)

@app.route("/support", methods = ["GET", "POST"])
def support():
	image = ""
	if(request.method == "POST"):
		name = request.form["name"]
		country = request.form["country"]
		state = request.form["state"]
		district = request.form["district"]
		details = request.form["details"]
		viewpoints = request.form["viewpoints"]
		location = request.form["location"]
		images = request.files.getlist("imgs[]")

		with open('settings_path.json') as settings_file:
			settings = json.load(settings_file)

		outputFolderPath = settings['output_folder']
		outputPath = os.path.join(outputFolderPath, name)
		app.config['outputPath'] = outputPath

		if not os.path.exists(outputPath):
			os.makedirs(outputPath)

		conn = sql.connect("tour_places.db")
		cur = conn.cursor()
		cur.execute("INSERT INTO images_data (name, country, state, district, details, viewpoints, location) VALUES(?, ?, ?, ?, ?, ?, ?)",(name, country, state, district, details, viewpoints, location))
		conn.commit()
		conn.close()
		for image in images:
			if(image and allowed_file(image.filename)):
				imagename = secure_filename(image.filename)
				image.save(os.path.join(app.config['outputPath'], imagename))
		flash("Uploaded successfully")
		
	return render_template("support.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/enquiry", methods = ["GET", "POST"])
def contact_us():
	return render_template("enquiry.html")

@app.route("/sign_up", methods = ["GET", "POST"])
def sign_up():
	msg = None
	password = None
	if(request.method == "POST"):
		loginID = request.form["loginID"]
		password1 = request.form["Password1"]
		password2 = request.form["Password2"]
		if(loginID == "" or password1 == "" or password2 == ""):
			flash("Fields must not be empty!")
		elif(password1 != password2):
			flash("Please re-enter your password")
		else:
			password = password1
			conn = sql.connect("tour_places.db")
			cur = conn.cursor()
			cur.execute("INSERT INTO sign_up (loginID, password) VALUES(?, ?)",(loginID,password))
			conn.commit()
			cur.close()
			conn.close()
			flash("Account created")
			return redirect(url_for("login"))
	return render_template("sign_up.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
	r = ""
	msg = ""
	if(request.method == "POST"):
		loginID = request.form["loginID"]
		password = request.form["Password"]
		conn = sql.connect("tour_places.db")
		cur = conn.cursor()
		cur.execute("SELECT * FROM sign_up WHERE loginID='"+loginID+"' AND password='"+password+"'")
		val = cur.fetchall()
		for i in val:
			if(loginID == i[0] and password == i[1]):
				flash("Login success")
				return redirect(url_for("home"))
			else:
				flash("Please enter correct LoginID/password")
		conn.commit()
		cur.close()
		conn.close()
	return render_template("login.html")

@app.route("/logout")
def logout():
	return render_template("index.html")

if(__name__ == "__main__"):
	app.run(debug=True)