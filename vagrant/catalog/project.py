import string
import random
import requests
from flask import make_response
import json
import httplib2
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from flask import session as login_session
from database_setup import Store, Base, Tv, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Tv Guide App"

engine = create_engine('sqlite:///tvcatalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showlogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, "GET")[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access-token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
    login_session['access-token'] = credentials.access_token
    login_session['gplus'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("You are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/stores/tv/JSON/')
def storeTvJSON():
    items = session.query(Tv).all()
    return jsonify(Tv=[item.serialize for item in items])


@app.route('/stores/<int:tv_id>/JSON/')
def tvJSON(tv_id):
    tv = session.query(Tv).filter_by(id=tv_id).one()
    return jsonify(tv=tv.serialize)


@app.route('/')
@app.route('/tvs/')
def showStores():
    store = session.query(Store).first()
    items = session.query(Tv).all()
    if 'username' not in login_session:
        return render_template('main.html', store=store, items=items)
    else:
        return render_template('publicstore.html', store=store, items=items)


@app.route('/')
@app.route('/stores/')
def storeTv():
    store = session.query(Store).first()
    items = session.query(Tv).all()
    return render_template('main.html', store=store, items=items)


@app.route('/stores/<int:store_id>/<int:tv_id>/tv')
def showTv(store_id, tv_id):
    store = session.query(Store).first()
    items = session.query(Tv).filter_by(id=tv_id)
    return render_template('tv.html', store=store, items=items, store_id=store_id, tv_id=tv_id)


@app.route('/stores/<int:store_id>/new', methods=['GET', 'POST'])
def newTv(store_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newTv = Tv(brand=request.form['brand'], store_id=store_id, user_id=login_session['user_id'])
        if request.form['price']:
            newTv.price = request.form['price']
        if request.form['size']:
            newTv.size = request.form['size']
        if request.form['description']:
            newTv.description = request.form['description']
        if request.form['series']:
            newTv.series = request.form['series']
        if request.form['year']:
            newTv.year = request.form['year']
        session.add(newTv)
        session.commit()
        flash("New tv has been added")
        return redirect(url_for('storeTv', store_id=store_id))
    else:
        return render_template('newtv.html', store_id=store_id)


@app.route('/stores/<int:store_id>/<int:tv_id>/edit', methods=['GET', 'POST'])
def editTv(store_id, tv_id):
    editedTv = session.query(Tv).filter_by(id=tv_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedTv.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this item.\
          Please create your own item in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['brand']:
            editedTv.brand = request.form['brand']
        if request.form['price']:
            editedTv.price = request.form['price']
        if request.form['size']:
            editedTv.size = request.form['size']
        if request.form['description']:
            editedTv.description = request.form['description']
        if request.form['series']:
            editedTv.series = request.form['series']
        if request.form['year']:
            editedTv.year = request.form['year']
            session.add(editedTv)
            session.commit()
        flash("Tv has been edited")
        return redirect(url_for('showTv', store_id=store_id, tv_id=tv_id))
    else:
        return render_template('edittv.html', store_id=store_id, tv_id=tv_id, item=editedTv)


@app.route('/stores/<int:store_id>/<int:tv_id>/delete', methods=['GET', 'POST'])
def deleteTv(store_id, tv_id):
    deletedTv = session.query(Tv).filter_by(id=tv_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deletedTv.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item.\
          Please create your own item in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(deletedTv)
        session.commit()
        flash("Tv has been deleted")
        return redirect(url_for('storeTv', store_id=store_id))
    else:
        return render_template('deletetv.html', store_id=store_id, tv_id=tv_id, item=deletedTv)


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_seceret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
