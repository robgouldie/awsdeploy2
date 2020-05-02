from flask import Flask, request, session, redirect, url_for, render_template, flash
from random import randint
from .models import CreateUser, create_db, Review, Restaurant, find_rest, find_review, get_photos, find_user_name, find_similar, find_searched_rest, find_best, move_photos

import re

app = Flask(__name__)
app.secret_key = "test"
#create_db()

class Rest:
    def __init__(this):
        this.name = "new restaurant"
        this.address = "123 adress"
        this.stars = 5


@app.route('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    pattern = re.compile("^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$")
    error = ""
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        confirm_pass = request.form['confirm_password']

        if len(username) < 1:
            error = 'Input a username'
        elif len(password) < 1:
            error = 'Input a password'
        elif len(confirm_pass) < 1:
            error = 'You need to confirm your password'
        elif not pattern.match(password):
            error = "Please ensure your password meets the requirements"
        elif password != confirm_pass:
            error = 'Your password did not match confirm password'
        elif not CreateUser(username).register(password):
            error = 'That email already exists.'
        else:
            session['username'] = username
            flash('Successfully registered please login.')
            return redirect(url_for('login'))

    return render_template('register.html', entering=True, error = error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error=""
    session['username'] = None
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        if not CreateUser(username).verify_password(password):
            error = 'Invalid login. \n Please check ensure you input the correct username and password.'
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('home'))

    return render_template('login.html', button="LOG IN", reentering=True, error = error)


@app.route('/home', methods=['GET', 'POST'])
def home():
    Srest_id = []
    Srest_name = []
    Srest_address = []
    Trest_id = []
    Trest_name = []
    Trest_address = []
    top5 = []
    best_cuisine = []
    count = 0

    if (session['username'] != None):
        searched = CreateUser(session['username']).find_searched()
        best_cuisine = []
        if searched != None:
            for i in searched:
                r = find_searched_rest(i)
                rest = Rest()
                rest.stars = str(r['r.stars'])
                rest.name = r['r.name']
                rest.address = r['r.address']
                best_cuisine.append(rest)


    top5 = find_best()
    count = 0
    best_city = []
    for i in top5:
        rest = Rest()
        rest.stars = str(i['r.stars'])
        rest.name = i['r.name']
        rest.address = i['r.address']
        best_city.append(rest)

    if 'username' in session:
        return render_template('home.html', button="SEARCH YOUR CITY", dest = "search#", 
                best_city = best_city, best_cuisine = best_cuisine, top_adress = Trest_address, searched_address = Srest_address, 
                username = session['username'])
    else:
        return render_template('home.html', button="SEARCH YOUR CITY", dest = "search#", 
                best_city = best_city, best_cuisine = best_cuisine, top_adress = Trest_address, searched_address = Srest_address, 
                username = None)  

@app.route('/search', methods=['GET', 'POST'])
def search():
    error = ""
    if request.method == 'POST':
        checker = 0
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday","Friday","Saturday", "Sunday"]
        dow = request.form["dow"].lower().title()
        cuisine = request.form["cuisine"].lower().title()
        city = request.form["city"].lower().title()
        time = request.form["time"]
        if dow == None or cuisine == None or city == None or time == None:
            error = "Please ensure you fill out each block"
            return render_template('search.html', button="BACK TO HOME", dest= "home#", looking = True, error=error)
        for i in weekdays:
            if dow == i:
                checker = 1
        if checker == 1:
            restaurant = find_rest(cuisine, time, dow)
            if restaurant == None:
                error = "There is no restaurant with {0} in {1}".format(cuisine, city)
            elif restaurant == "closed":
                error = "There is no open restau.rant on {0} at {1} with cuisine {2}".format(dow, time, cuisine)
            else:
                session['dow'] = dow
                session['cuisine'] = cuisine
                session['city'] = city
                session['time'] = time
                session['restaurant'] = restaurant
                # if 'username' in session:
                #     if (session['username'] != None):
                #         print(session['username'])
                #         print('++++++++++++++++++++++++++++++++++++++++')
                #         CreateUser(session['username']).add_search(cuisine)
                return redirect(url_for('result'))
        else:
            error = "Please ensure you enter a valid day of the week"
        
    if 'username' in session:
        return render_template('search.html', button="BACK TO HOME", dest= "home#", looking = True, error=error, username=session['username'])
    else:
        return render_template('search.html', button="BACK TO HOME", dest= "home#", looking = True, error=error, username = None)
    # if (session['username'] == None):
    #     return render_template('search.html', button="BACK TO HOME", dest= "home#", looking = True, error=error)
    # else:
    #     return render_template('search.html', button="BACK TO HOME", dest= "home#", looking = True, error=error, username=session['username'])

@app.route('/result')
def result():

    error = ""
    dow = session['dow'].capitalize()
    print("day of week: " + dow)
    cuisine = session['cuisine']
    time = session['time']
    city = session['city']
    restaurant = session['restaurant']

    rest_id = restaurant['r.business_id']
    rest_name = restaurant['r.name']
    rest_address = restaurant['r.address']
    rest_stars = int(restaurant['r.stars'])
    rest_count = restaurant['r.review_count']
    review = find_review(rest_id)
    if 'username' in session:
        if (session['username'] != None):
            print(session['username'])
            print('++++++++++++++++++++++++++++++++++++++++')
            CreateUser(session['username']).add_search(rest_id)
    if review == None:
        full_review = "There is no review for this restuarant"
        rev_name = "None"
        rev_date = "None"
        rev_stars = 0
    elif review == "long":
        full_review = "There is no review within the past two years"
        full_review = "There is no review for this restuarant"
        rev_name = "None"
        rev_date = "None"
        rev_stars = 0
    else:
        full_review = review['rev.text']
        rev_userid = review['rev.userid']
        rev_name = find_user_name(rev_userid)
        rev_date = review['rev.date']
        rev_stars = int(review['rev.stars'])
        captions = get_photos(rest_id)
        if captions[0] == 'no_photos':
            error = "There are no photos available for this restaurant"
            captions[0] = 'No photo available'
            captions.append('No photo available')
        move_photos()
        suggestions = find_similar(rev_userid, cuisine)
        if (len(captions) == 1):
            captions.append('No photo available')


    #use the session data from above to check for cuisine etc...
    print('----------------------')
    print(suggestions)
    if 'username' in session:
        return render_template('result.html', button="NOT WHAT YOU'RE LOOKING FOR?", dest="search#",
            name = rest_name, address = rest_address, rest_stars = rest_stars, reviewer = rev_name, 
            revdate = rev_date, rev_stars = rev_stars, rev_count = rest_count, review = full_review, 
            suggested = suggestions, cap0 = captions[0], cap1 = captions[1], username = session['username'], error = error)
    else:
        return render_template('result.html', button="NOT WHAT YOU'RE LOOKING FOR?", dest="search#",
            name = rest_name, address = rest_address, rest_stars = rest_stars, reviewer = rev_name, 
            revdate = rev_date, rev_stars = rev_stars, rev_count = rest_count, review = full_review, 
            suggested = suggestions, cap0 = captions[0], cap1 = captions[1], username = session['username'], error = error)

if __name__ == '__main__':
    app.run(debug=True)
