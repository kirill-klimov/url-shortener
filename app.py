import os
from flask import Flask, request, jsonify, redirect, url_for, session, render_template
from authlib.integrations.flask_client import OAuth
from model.db import get_or_create_user, save_link, update_link_counter, get_link, get_user_links, delete_link, update_link
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET')
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid'})

@app.route('/')
def home_page():
    user_id = dict(session).get("user_id", None)
    picture = dict(session).get("picture", None)
    return render_template(
        'index.html',
        user_id=user_id,
        picture=picture)




@app.route('/', methods=['POST'])
def short():
    user_id = dict(session).get("user_id", None)
    if not user_id:
        return 'Unauthorized', 401
    body = request.get_json()
    link = save_link(body['url'], user_id)
    res = { "url": f"{request.base_url}{link.short_id}" }
    return jsonify(res)



@app.route('/<short_id>', methods=['GET'])
def home(short_id):
    user_id = dict(session).get("user_id", None)
    update_link_counter(short_id)
    link = get_link(short_id)
    try:
        if link.visibility == 'public':
            return redirect(link.url, code=302)
        elif link.visibility == 'auth':
            if user_id:
                return redirect(link.url, code=302)
            else:
                return redirect('/login')
        elif link.visibility == 'private':
            if user_id == link.creator_id:
                return redirect(link.url, code=302)
            elif not user_id:
                return redirect('/login')
            else:
                return 'Unauthorized', 401
    except Exception:
        return f"Error redirecting to {link.url}", 500

@app.route('/<short_id>', methods=['DELETE'])
def delete(short_id):
    user_id = dict(session).get("user_id", None)
    if not user_id:
        return 'Unauthorized', 401
    delete_link(user_id, short_id)
    return '', 200

@app.route('/<short_id>', methods=['UPDATE'])
def update(short_id):
    user_id = dict(session).get("user_id", None)
    if not user_id:
        return 'Unauthorized', 401
    body = request.get_json()
    new_link = {
        "short_id": body["short_id"],
        "visibility": body["visibility"]
    }
    update_link(user_id, new_link, short_id)
    return '', 200

@app.route('/me')
def me():
    user_id = dict(session).get("user_id", None)
    if not user_id:
        return 'Unauthorized', 401
    links = get_user_links(user_id)[::-1]
    return jsonify(links)


@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    res = google.get('userinfo').json()
    session["user_id"] = res["id"]
    session["picture"] = res["picture"]
    get_or_create_user(res["id"])
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')