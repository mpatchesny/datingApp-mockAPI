import os
import json
import random
import dateutil
import requests
from datetime import datetime, timedelta

from bottle import Bottle, run, request, HTTPResponse, response, run
from bottle import static_file

from generator import generate

app = Bottle()


def isAuthorized(func):
    def wrapper(*args, **kwargs):
        current_user = None

        auth_header = request.get_header("Authorization")
        provided_token = ""
        if auth_header:
            provided_token = auth_header.split("Bearer ")[1]

        for token in tokens:
            if token["accessToken"]["token"] == provided_token:
                exp_time = dateutil.parser.isoparse(token["accessToken"]["expirationTime"])
                if exp_time >= datetime.now():
                    for user in users:
                        if provided_token.find(user["userId"]) >= 0:
                            current_user = user
                            globals()["current_user"] = current_user
                            break

        if not current_user:
            err = {"code": "Unauthorized", "reason": "You don't have permission to perform this action"}
            return HTTPResponse(err, status=403)

        return func(*args, **kwargs)
    return wrapper

def corsOptionsWrapper(func):
    def wrapper(*args, **kwargs):
        if (request.method == 'OPTIONS'):
            return HTTPResponse(status=200)
        else:
            return func(*args, **kwargs)
    return wrapper

# https://gist.github.com/richard-flosi/3789163
@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, PATCH, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@app.route('/api')
def hello():
    return "datingApp Mock API"


### AUTH

@app.route('/users/auth', method=['POST', 'OPTIONS'])
@corsOptionsWrapper
def request_access_code():
    body = json.loads(request.body.getvalue())
    email = body["email"]
    return {"email": email}

@app.route('/users/sign-in', method=['POST', 'OPTIONS'])
@corsOptionsWrapper
def login():
    body = json.loads(request.body.getvalue())
    email = body["email"]
    found = __search(users, "email", email);
    if found != []:
        globals()["current_user"] = found[0]
        access_token = found[0]["userId"] + "_" + __get_random_id()
        access_token_exp_time = (datetime.now() + timedelta(days=7)).isoformat()
        refresh_token = found[0]["userId"] + "_" +__get_random_id()
        refresh_token_exp_time = (datetime.now() + timedelta(days=90)).isoformat()
        d = {}
        d["accessToken"] = { "token": access_token, "expirationTime": access_token_exp_time}
        d["refreshToken"] = { "token": refresh_token, "expirationTime": refresh_token_exp_time}
        tokens.append(d)
        return d

@app.route('/users/auth/refresh', method=['POST', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def refresh_access_code():
    access_token = __get_random_id()
    access_token_exp_time = (datetime.now() + timedelta(days=7)).isoformat()
    refresh_token = __get_random_id()
    refresh_token_exp_time = (datetime.now() + timedelta(days=90)).isoformat()
    d = {}
    d["accessToken"] = { "token": access_token, "expirationTime": access_token_exp_time}
    d["refreshToken"] = { "token": refresh_token, "expirationTime": refresh_token_exp_time}
    tokens.append(d)
    return d

### USERS

@app.route('/users/<userId>', method=['GET', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def get_user(userId):
    found = __search(users, "userId", userId)
    if found != []:
        return found[0]
    return HTTPResponse(status=404)

@app.route('/users', method=['POST', 'OPTIONS'])
@corsOptionsWrapper
def post_user():
    body = json.loads(request.body.getvalue())
    new_user = {}
    new_user["userId"] = "user_" + __get_random_id()
    for field in ["name", "phone", "email", "sex", "dateOfBirth", "bio", "job"]:
        if body.get(field):
            new_user[field] = body[field]
    settings = {}
    settings["preferredSex"] = body["preferredSex"]
    settings["preferredAgeFrom"] = 18
    settings["preferredAgeTo"] = 99
    settings["preferredMaxDistance"] = 100
    settings["lat"] = 0.0
    settings["lon"] = 0.0
    new_user["settings"] = settings
    new_user["photos"] = []
    users.append(new_user)
    return new_user

@app.route('/users/<userId>', method=['PATCH', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def patch_user(userId):
    current_user = globals().get("current_user")
    if current_user in users:
        users.remove(current_user)

    body = json.loads(request.body.getvalue())
    for field in ["dateOfBirth", "bio", "job"]:
        if body.get(field):
            current_user[field] = body[field]
    for field in ["preferredAgeFrom", "preferredAgeTo", "preferredMaxDistance", "preferredSex", "lat", "lon"]:
        if body.get(field):
            current_user["settings"][field] = body[field]

    users.append(current_user)
    return HTTPResponse(status=201)

@app.route('/users/<userId>', method=['DELETE', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def delete_user(userId):
    current_user = globals().get("current_user")
    if current_user:
        if current_user in users:
            users.remove(current_user)
        current_user = None
        return HTTPResponse(status=201)
    return HTTPResponse(status=404)

@app.route('/users/me', method=['GET', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def get_me():
    return current_user

@app.route('/users/me/recommendations', method=['GET', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def get_recommendations():
    recommendations = []
    my_swipes = __search(swipes, "swipedById", current_user["userId"])
    
    for user in users:
        if user["userId"] == current_user["userId"]:
            continue
        if __search(my_swipes, "swipedWhoId", user["userId"]) != []:
            continue
        recommendations.append(user)
        if len(recommendations) >= 10:
            break

    response = json.dumps(recommendations)
    return response

### PHOTOS

@app.route('/users/me/photos', method=['POST', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def add_photo():
    upload = request.files.get('file')
    if upload:
        mimetype = upload.content_type
        extension = mimetype.split('/')[-1]
        photoId = "photo_" + __get_random_id()

        if extension not in ['jpeg', 'jpg', 'png', 'bmp']:
            return HTTPResponse(status=400, body="Unsupported file type")
        if upload:
            file_path = f"./storage/{photoId}." + extension
            upload.save(file_path)

        current_user = globals().get("current_user")
        if current_user in users:
            users.remove(current_user)

        photo = {}
        photo["photoId"] = photoId
        photo["url"] = "~/storage/" + photoId + "." + extension
        photo["oridinal"] = len(current_user["photos"])
        current_user["photos"].append(photo)
        users.append(current_user)
        return photo
    return HTTPResponse(status=500)

@app.route('/photos/<photoId>', method=['PATCH', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def patch_photo(photoId):
    found = __search(current_user["photos"], "photoId", photoId)
    if found != []:
        body = json.loads(request.body.getvalue())
        newOridinal = int(body["newOridinal"])
        found[0]["oridinal"] = newOridinal
        return HTTPResponse(status=201)
    return HTTPResponse(status=404)

@app.route('/photos/<photoId>', method=['DELETE', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def delete_photo(photoId):
    found = __search(current_user["photos"], "photoId", photoId)
    if found != []:
        current_user["photos"].remove(found[0])
        path = './' + found[0].url.strip("~/")
        if os.path.exists(path):
            os.remove(path)
        return HTTPResponse(status=201)
    return HTTPResponse(status=404)

### MATCHES

@app.route('/matches/<matchId>', method=['GET', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def get_match(matchId):
    found = __search(matches, "matchId", matchId)
    if found != []:
        return found[0]
    return HTTPResponse(status=404)

@app.route('/matches', method=['GET', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def get_matches():
    found = []
    for match in matches:
        if match["user"]["userId"] == current_user["userId"]:
            found.append(match)
        if match["user1"]["userId"] == current_user["userId"]:
            found.append(match)

    recordsCount = len(found)
    if len(found) > 0:
        found.sort(key=lambda x: x["createdAt"], reverse=True)

    page = int(request.query.page) if request.query.page else 1
    pageSize = int(request.query.pageSize) if request.query.pageSize else 25
    start = (page-1) * pageSize
    end = start + pageSize

    d = {}
    d["page"] = page
    d["pageSize"] = pageSize
    d["pageCount"] = recordsCount // pageSize
    d["data"] = found[start:end]
    return d

@app.route('/matches/<matchId>', method=['PATCH', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def set_match_as_displayed(matchId):
    found = __search(matches, "matchId", matchId)
    if found != []:
        match = found[0]
        match["isDisplayed"] = True
        for msg in match["messages"]:
            msg["isDisplayed"] = True
        return HTTPResponse(status=201)
    return HTTPResponse(status=404)

@app.route('/matches/<matchId>', method=['DELETE', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def delete_match(matchId):
    found = __search(matches, "matchId", matchId)
    if found != []:
        matches.remove(found[0])
        return HTTPResponse(status=201)
    return HTTPResponse(status=404)

@app.route('/matches/<matchId>/messages', method=['GET', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def get_messages(matchId):
    found = __search(matches, "matchId", matchId)
    if found != []:
        messages = found[0]["messages"]
        recordsCount = len(messages)
        if len(messages) > 0:
            messages.sort(key=lambda x: x["createdAt"], reverse=True)

        page = int(request.query.page) if request.query.page else 1
        pageSize = int(request.query.pageSize) if request.query.pageSize else 25
        start = (page-1) * pageSize
        end = start + pageSize

        d = {}
        d["page"] = page
        d["pageSize"] = pageSize
        d["pageCount"] = recordsCount // pageSize
        d["data"] = messages[start:end]
        return d
    return HTTPResponse(status=404)

@app.route('/matches/<matchId>', method=['POST', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def send_message(matchId):
    found = __search(matches, "matchId", matchId)
    if found != []:
        body = json.loads(request.body.getvalue())
        msg = {} 
        msg["messageId"] = "match_" + __get_random_id()
        msg["sendFromUserId"] = current_user["userId"]
        msg["text"] = body["text"]
        msg["createdAt"] = datetime.now().isoformat()
        found[0]["messages"].append(msg)
        return msg
    return HTTPResponse(status=404)

### PASS/LIKE

@app.route('/like/<userId>', method=['PUT', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def like_user(userId):
    swipe = {}
    swipe["swipedById"] = current_user["userId"]
    swipe["swipedWhoId"] = userId
    swipe["like"] = 2
    swipe["createdAt"] = datetime.now().isoformat()
    swipes.append(swipe)

    match = {}
    match["matchId"] = "match_" + __get_random_id()
    match["user"] = __search(users, "userId", userId)[0]
    match["user1"] = current_user
    match["messages"] = []
    match["createdAt"] = datetime.now().isoformat()
    matches.append(match)
    isLikedByOtherUser = True
    return { "isLikedByOtherUser": isLikedByOtherUser }

@app.route('/pass/<userId>', method=['PUT', 'OPTIONS'])
@corsOptionsWrapper
@isAuthorized
def pass_user(userId):
    swipe = {}
    swipe["swipedById"] = current_user["userId"]
    swipe["swipedWhoId"] = userId
    swipe["like"] = 1
    swipe["createdAt"] = datetime.now().isoformat()
    swipes.append(swipe)
    return { "isLikedByOtherUser": False }

@app.route('/storage/<filename:path>')
def serve_static(filename):
    file_path = f"./storage/{filename}"
    if not os.path.exists(file_path):
        response = requests.get("https://thispersondoesnotexist.com")
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
    return static_file(filename, root='./storage')


def __get_random_id():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))

def __search(list, field_name, value):
    found = []
    for item in list:
        if item[field_name] == value:
            found.append(item)
    return found

def __load_data():
    if os.path.exists('./data/users.json'):
        with open('./data/users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
    else:
        users, _, _ = generate(1000, 0)

    if os.path.exists('./data/matches.json'):
        with open('./data/matches.json', 'r', encoding='utf-8') as f:
            matches = json.load(f)
    else:
        matches = []

    if os.path.exists('./data/swipes.json'):
        with open('./data/swipes.json', 'r', encoding='utf-8') as f:
            swipes = json.load(f)
    else:
        swipes = []

    if os.path.exists('./data/tokens.json'):
        with open('./data/tokens.json', 'r', encoding='utf-8') as f:
            tokens = json.load(f)
    else:
        tokens = []

    return users, matches, swipes, tokens

def __dump():
    if not os.path.exists('./data'):
        os.mkdir('./data')
    with open('./data/users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f)
    with open('./data/matches.json', 'w', encoding='utf-8') as f:
        json.dump(matches, f)
    with open('./data/swipes.json', 'w', encoding='utf-8') as f:
        json.dump(swipes, f)
    with open('./data/tokens.json', 'w', encoding='utf-8') as f:
        json.dump(tokens, f)


if __name__ == '__main__':
    users, matches, swipes, tokens = __load_data()

    globals()["users"] = users
    globals()["matches"] = matches
    globals()["swipes"] = swipes
    globals()["tokens"] = tokens
    # globals()["current_user"] = None

    if not os.path.exists('./storage'):
        os.mkdir('./storage')

    run(app, host='localhost', port=8080)

    __dump()
