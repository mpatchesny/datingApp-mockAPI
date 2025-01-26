import json
import random
from datetime import datetime, timedelta

def random_datetime():
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400)
    return start_date + timedelta(days=random_days, seconds=random_seconds)

def random_date():
    start_date = datetime(1970, 1, 1)
    end_date = datetime.now() - timedelta(days=19*365)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    date = start_date + timedelta(days=random_days)
    return date.date()

def random_lat():
    return random.uniform(-90.0, 90.0)

def random_lon():
    return random.uniform(-180.0, 180.0)

def random_name():
    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack"]
    names += ["Karen", "Leo", "Mona", "Nina", "Oscar", "Paul", "Quincy", "Rachel", "Sam", "Tina", "Uma", "Vince", "Wendy", "Xander", "Yara", "Zane"]
    names += ["Aaron", "Bella", "Catherine", "Derek", "Elena", "Fiona", "George", "Helen", "Ian", "Julia"]
    names += ["Kyle", "Liam", "Megan", "Nate", "Olivia", "Peter", "Quinn", "Rebecca", "Steve", "Tracy"]
    names += ["Ursula", "Victor", "Willow", "Xenia", "Yvonne", "Zachary"]
    names += ["Aiden", "Brooke", "Cameron", "Diana", "Ethan", "Faith", "Gavin", "Hailey", "Isaac", "Jasmine"]
    names += ["Kaitlyn", "Landon", "Madison", "Nathan", "Owen", "Peyton", "Quinn", "Riley", "Sophie", "Tyler"]
    names += ["Ulysses", "Violet", "Wyatt", "Ximena", "Yusuf", "Zoey"]
    names += ["Apple", "Apollo", "Banana", "Berry", "Cherry", "Coco", "Daisy", "Echo", "Falcon", "Galaxy"]
    names += ["Halo", "Indigo", "Juno", "Karma", "Luna", "Mango", "Nova", "Orion", "Peach", "Quartz"]
    names += ["Raven", "Sky", "Tiger", "Unity", "Venus", "Willow", "Xander", "Yeti", "Zephyr"]
    return random.choice(list(set(names)))

def random_message():
    messages = [
        "Hey, how's it going?",
        "What's up?",
        "Hi there! How are you?",
        "Hello! What are you up to?",
        "Hey! Want to chat?",
        "Hi! How's your day been?",
        "Hello! Any plans for the weekend?",
        "Hey! How's everything?",
        "Hi! What do you like to do for fun?",
        "Hello! Nice to meet you!",
        "Hi! How's it going?",
        "Hello! How are you?",
        "Hey! What's new?",
        "Hi! How's your day?",
        "Hello! How's everything?",
        "Hey! How's life?",
        "Hi! How's your week?",
        "Hello! How's your weekend?",
        "Hey! How's your evening?",
        "Hi! How's your morning?",
        "Hello! How's your afternoon?",
        "Hey! How's your night?",
        "Hi! How's your work?",
        "Hello! How's your study?",
        "Hey! How's your family?",
        "Hi! How's your friends?",
        "Hello! How's your pet?",
        "Hey! How's your hobby?",
        "Hi! How's your travel?",
        "Hello! How's your vacation?"
    ]
    return random.choice(messages)

def generate_random_message(userId):
    d = {}
    d["messageId"] = "message_" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
    d["sendFromId"] = userId
    d["text"] = random_message()
    d["isDisplayed"] = random.choice([True, False])
    d["createdAt"] = random_datetime().isoformat()
    return d

def generate_random_match(user1, user2):
    d = {}
    d["matchId"] = "match_" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
    d["user1"] = user1
    d["user"] = user2
    d["isDisplayed"] = random.choice([True, False])
    messages = []
    for _ in range(0, random.randrange(0, 10)):
        sendBy = random.choice([user1["userId"], user2["userId"]])
        messages.append(generate_random_message(sendBy))
    d["messages"] = messages
    d["createdAt"] = random_datetime().isoformat()
    return d

def generate_random_photo(oridinal):
    d = {}
    d["photoId"] = "photo_" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
    d["url"] = "~/" + d["photoId"] + ".jpg"
    d["oridinal"] = oridinal
    return d

def generate_random_settings(userId):
    d = {}
    d["userId"] = userId
    d["lat"] = random_lat()
    d["lon"] = random_lon()
    d["preferredSex"] = random.choice([1,2,3])
    d["preferredAgeFrom"] = random.randrange(18, 100)
    d["preferredAgeTo"] = random.randrange(18, 100)
    d["preferredAgeFrom"] = min(d["preferredAgeFrom"], d["preferredAgeTo"])
    d["preferredAgeTo"] = max(d["preferredAgeFrom"], d["preferredAgeTo"])
    d["preferredMaxDistance"] = random.randrange(0, 100)
    return d

def generate_random_user():
    d = {}
    d["userId"] = "user_" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
    d["name"] = random_name()
    d["phone"] = ''.join(random.choices('0123456789', k=9))
    d["email"] = d["name"] + "_" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10)) + "@test.com"
    d["email"] = d["email"].lower()
    d["job"] = "some job"
    d["bio"] = "some bio"
    d["sex"] = random.choice([1, 2])
    photos = []
    for i in range(0, random.randrange(0, 6)):
        photos.append(generate_random_photo(i+1))
    d["photos"] = photos
    d["distanceInKms"] = random.randrange(0, 250)
    dob = random_date()
    d["dateOfBirth"] = dob.isoformat()[:10]
    d["age"] = (datetime.now().date() - dob).days // 365
    d["settings"] = generate_random_settings(d["userId"])
    return d

def get_swipes_from_matches(matches):
    swipes = []
    for match in matches:
        like1 = {}
        like1["swipedById"] = match["user1"]["userId"]
        like1["swipedWhoId"] = match["user"]["userId"] 
        like1["like"] = 2
        like1["createdAt"] = match["createdAt"]
        like2 = {}
        like2["swipedById"] = match["user"]["userId"]
        like2["swipedWhoId"] = match["user1"]["userId"] 
        like2["like"] = 2
        like2["createdAt"] = match["createdAt"]
        swipes.append(like1)
        swipes.append(like2)
    return swipes

def generate(users_count, matches_count):
    users = [ generate_random_user() for _ in range(0, users_count) ]

    matches = []
    for _ in range(0, matches_count):
        user1, user2 = random.choice(users), random.choice(users)
        attempts_count = 0
        while user1["userId"] == user2["userId"]:
            user2 = random.choice(users)
            if attempts_count > 10:
                exit
            attempts_count += 1
        matches.append(generate_random_match(user1, user2))

    return users, matches, get_swipes_from_matches(matches)
