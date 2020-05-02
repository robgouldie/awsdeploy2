from py2neo import Graph, Node, Relationship
from py2neo.ogm import GraphObject, Property, Label
from passlib.hash import bcrypt
from datetime import datetime
import webbrowser
import json
# import normalize
import requests
import sys
import uuid
import os
import shutil
from PIL import Image
import pandas as pd
import math
import numpy
import time
import ast

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:8001')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

graph = Graph(url + '/db/data/', username = username, password = password)

class CreateUser(GraphObject):

    def __init__(self, username):
        self.username = username

    def add_search(self, cuisine):
        query = '''
        MATCH (u:Client)
        WHERE u.username = $name
        return u.searched
        '''
        searched = graph.run(query, name = self.username).evaluate()
        wasIn = 0
        count = 0
        if searched != None:
            for i in searched:
                if i == cuisine:
                    print(i)
                    print('------------------------------------------')
                    print(searched)
                    print('------------------------------------------')
                    wasIn = 1
                    del searched[count:count+1]
                count += 1
            searched.insert(0, cuisine)
        else:
            searched = []
            searched.append(cuisine)  
        if wasIn == 0 and len(searched) > 5:  
            searched = searched[:-1]
        print('------------------------------------------')
        print(searched)
        print('------------------------------------------')
        query2 = '''
        MATCH (u:Client)
        WHERE u.username = $name
        set u.searched = $searched
        '''
        graph.run(query2, name = self.username, searched = searched)

    def find_searched(self):
        query = '''
        MATCH (u:Client)
        WHERE u.username = $name
        return u.searched
        '''
        searched = graph.run(query, name = self.username).evaluate()
        return searched

    def find(self):
        query = '''
        OPTIONAL MATCH (r:Client)
        WHERE r.username = $name
        RETURN r.username
        '''
        node = graph.run(query, name = self.username).evaluate()
        return node

    def register(self, password):
        if not self.find():
            user = Node('Client', username = self.username, password = bcrypt.encrypt(password), searched = [])
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        query2 = '''
        MATCH (r:Client)
        WHERE r.username = $name
        RETURN r.password
        '''
        pw = graph.run(query2, name = self.username).evaluate()
        if user:
            return bcrypt.verify(password, pw)
        else:
            return False

def split(str):
        hoursplit = str.split(':')
        hour = hoursplit[0]
        hour = int(hour)
        minute = hoursplit[1]
        if minute is 0:
            minute = 00
        else:
            minute = 30

        time =  datetime(2020, 3, 27, hour, minute)
        return time


class User:

    def __init__(self, id, name, friends, review_count):
        self.id = id
        self.name = name
        self.friends = friends
        self.review_count = review_count

    def new_user(self):
        u = Node('User', id=self.id, name=self.name, friends=self.friends, review_count=self.review_count)
        graph.merge(u, 'User', 'id')
        return u


def find_user_name(userid):
    query3 = '''
    MATCH (u:User)
    WHERE u.id = $id
    RETURN u.name
    '''
    name = graph.evaluate(query3, id=userid)
    return name

class Restaurant:

    def __init__(self, name, stars, review_count, full_address, business_id, hours):
        self.name = name
        self.stars = stars
        self.review_count = review_count
        self.address = full_address
        self.business_id = business_id
        self.hours = hours
        # self.opening_time = ''
        # self.closing_time = ''
        # if hours is '':
        #     open = 0
        # else:
        #
        #     # given by user
        #     time = '18:00'
        #     day = 'Wednesday'
        #
        #     hours_list = hours
        #     if day is 'Monday':
        #         open_hours = hours_list[0]
        #     elif day is 'Tuesday':
        #         open_hours = hours_list[1]
        #     elif day is 'Wednesday':
        #         open_hours = hours_list[2]
        #     elif day is 'Thursday':
        #         open_hours = hours_list[3]
        #     elif day is 'Friday':
        #         open_hours = hours_list[4]
        #     elif day is 'Saturday':
        #         open_hours = hours_list[5]
        #     elif day is 'Sunday':
        #         open_hours = hours_list[6]
        #     else:
        #         open_hours = None
        #         print('Restaurant is not open on this day')
        #
        #     now = datetime.now()
        #
        #     # this must be passed in
        #     # the date can be random if were only looking at week ahead
        #     # so the end result will look like requested_time = datetime(2020, 3, 27, hour, time)
        #     requested_time = datetime(2020, 3, 27, 18, 30)
        #
        #     x = open_hours.split('-')
        #     open_time = x[0]
        #     close_time = x[1]
        #     o_time = split(open_time)
        #     c_time = split(close_time)
        #
        #     if requested_time < o_time or requested_time > c_time:
        #         open = 0
        #     else:
        #         open = 1
        #     self.opening_time = o_time
        #     self.closing_time = c_time
        #
        #
        # self.open = open

    def new_rest(self):

            # FOR ONE RESTAURANT WITH PROPERTIES
            rest = Node('Restaurant', name=self.name, stars=self.stars, review_count=self.review_count, address = self.address, business_id=self.business_id, hours = self.hours)
            graph.merge(rest, 'Restaurant', 'name')
            return rest


def get_photos(busid):
    checker = 0
    f = open("normphoto.json")
    photo_list = json.load(f)
    captions = []
    print('photos!!')
    print(busid)
    print(type(busid))
    
    for i in photo_list:
        if i["business_id"] == busid:
            checker = 1
            print(i['photo_id'])
            name = "photos_norm/" + i["photo_id"] + ".jpg"
            img = Image.open(name)
            #img.show()
            print("caption!!!")
            print(i['caption'])
            captions.append(i["caption"])
    if checker == 0:
        captions.append('no_photos')
    print(captions)

    return captions

def move_photos():
    #delete old photos
    # owd = os.getcwd()
    # directory = 'roamapp/static/img'
    # os.chdir(directory)
    # for file in os.listdir("."):
    #     if file.endswith("photo1.jpg"):
    #         os.unlink(file)
    #     if file.endswith("photo2.jpg"):
    #         os.unlink(file)
    # os.chdir(owd)

    parent = os.path.dirname(os.path.abspath('run.py'))
    dest = os.path.join(parent, 'roamapp/static/img')

    for file in os.listdir(parent):
        if file.endswith('.jpg'):
            src = os.path.abspath(file)
            shutil.move(src, dest)


class City:

    def __init__(self, name):
        self.name = name

    def new_city(self):
        place = Node('City', name=self.name)
        graph.merge(place, 'City', 'name')
        return place

class Cuisine:

    def __init__(self, name):
        self.name = name

    def new_cuisine(self):
        cuis = Node('Cuisine', name=self.name)
        graph.merge(cuis, 'Cuisine', 'name')
        return cuis

class Review:

    def __init__(self, revid, userid, busid, stars, useful, date, text):
        self.revid = revid
        self.userid = userid
        self.busid = busid
        self.stars = stars
        self.useful = useful
        self.date = date
        self.text = text

    def new_review(self):
        rev = Node('Review', revid=self.revid, userid=self.userid, busid=self.busid, stars=self.stars, useful=self.useful, date=self.date, text=self.text)
        graph.merge(rev, 'Review', 'revid')
        return rev

def new_relation(rel_type, a, b):
        graph.merge(rel_type(a, b))

def find_review(busid):
    query2 = '''
    MATCH (r:Restaurant)-[:REVIEW]-(rev:Review)
    WHERE r.business_id = $busid
    RETURN rev.userid, rev.stars, rev.date, rev.text
    ORDER BY rev.useful DESC LIMIT 5
    '''
    nodes = graph.run(query2, busid=busid).data()
    now = datetime.now()
    curr_year = now.year
    two_years_ago = now.replace(year=curr_year-2)
    print("two years ago: ")
    print(two_years_ago)
    if not nodes:
        return None
        # print("no reviews match query")
        # sys.exit(0)

    answer = None
    for i in nodes:
        print("rev date: " + i["rev.date"])
        date_list = i["rev.date"].split("-")
        date = datetime(int(date_list[0]), int(date_list[1]), int(date_list[2][:2]))
        if two_years_ago < date:
            answer = i
            print("\nrev date: ")
            print(date)
            break
        #answer = nodes[0]
    if answer == None:
        return "long"
        # print("No review in past two years\n")
        # sys.exit(0)
    return answer

def find_searched_rest(rest_id):
    # query = '''
    # MATCH (r:Restaurant)-[:CUISINE]->(c:Cuisine)
    # WHERE c.name = $name
    # RETURN r.name, r.stars, r.address, r.review_count, r.business_id, r.hours
    # ORDER BY r.stars DESC LIMIT 5
    # '''

    query = '''
    MATCH (r:Restaurant)
    WHERE r.business_id = $id
    RETURN r.name, r.stars, r.address, r.review_count, r.business_id, r.hours
    '''
    node = graph.run(query, id=rest_id).data()
    if not node:
        return None
    else:
        return node[0]

def find_best():
    query = '''
    MATCH (r:Restaurant)
    RETURN r.name, r.stars, r.address, r.review_count, r.business_id, r.hours
    ORDER BY r.stars DESC LIMIT 5
    '''
    nodes = graph.run(query).data()
    if not nodes:
        return None
    else:
        return nodes

def find_rest(cuisine_name, time, day):
    query = '''
    MATCH (r:Restaurant)-[:CUISINE]->(c:Cuisine)
    WHERE c.name = $name
    RETURN r.name, r.stars, r.address, r.review_count, r.business_id, r.hours
    ORDER BY r.stars DESC LIMIT 5
    '''
    print(cuisine_name)
    nodes = graph.run(query, name=cuisine_name).data()
    if not nodes:
        return None
        # print("no restaurant matches query")
        # sys.exit(0)

    answer = None
    print(nodes[0]["r.name"])
    print("findrest hours type=")
    print(type(nodes[0]["r.hours"]))
    if is_open(time, day, nodes[0]["r.hours"]) and len(nodes) == 1:
        answer = nodes[0]
        return answer

    answer_list = []
    open_list = []
    for i in range(len(nodes)):
        if is_open(time, day, nodes[i]['r.hours']):
            open_list.append(nodes[i])

    if len(open_list) == 1:
        answer = open_list[0]
        return answer
    elif len(open_list) == 0:
        return None

    answer = open_list[0]
    for i in range(len(open_list)-1):
        if open_list[i]['r.stars'] == open_list[i+1]['r.stars']:
            answer_list.append(open_list[i])
        else:
            break
    if len(answer_list) == 1:
        answer = answer_list[0]
        return answer
    elif len(answer_list) == 0:
        return answer
    else:
        answer = answer_list[0]
        for i in range(len(answer_list)-1):
            if answer_list[i]['r.review_count'] > answer_list[i+1]['r.review_count']:
                answer = answer_list[i]
        return answer

    # if is_open(time, day, nodes[0]["r.hours"]):
    #     answer_list.append(nodes[0])
    
    # for i in range(len(nodes)-1):
    #     if (nodes[i]["r.stars"] == nodes[i+1]["r.stars"]) and is_open(time, day, nodes[i+1]["r.hours"]):
    #         answer_list.append(nodes[i+1])
    #     else:
    #         break
    # if len(answer_list) > 1:
    #     for j in range(len(answer_list)-1):
    #         if answer_list[j]["r.review_count"] >= answer_list[j+1]["r.review_count"]:
    #             answer = answer_list[j]
    #             break
    # if answer == None:
    #     return "closed"
    #     # print("No restaurant matches query")
    #     # sys.exit(0)
    return answer

# def get_photos(busid):
#     url = "https://api.yelp.com/v3/businesses/"
#     api_key = "FxR7UkYfaIi7O6tD9jaGFkSgDxbsPcCILepyktUYIqdhvQEiLGTdRrz0XXzuq_H0d4kFap7K533Yk46OvagCA-NgC4Omw69hZh1oodFI17ONaUZafw0SL1UIu8N9XnYx"
#     headers = {'Authorization' : 'bearer %s' % api_key}
#     r = requests.get(url=url + busid, headers=headers)
#     data = r.json()
#     img_url = data["photos"]
#     count = 0
#     for i in img_url:
#         count+=1
#         img_request = requests.get(i)
#         file = "photo" + str(count) + ".jpg"
#         img = open(file, "wb")
#         img.write(img_request.content)
#         img.close()

def find_similar(userid, cuisine_name):
    query4 = '''
    MATCH (u:User)-[:FRIEND*1..2]-(f:User)
    WHERE u.id = $id
    WITH DISTINCT f
    ORDER BY f.review_count DESC LIMIT 50
    OPTIONAL MATCH (f)-[:REVIEWED_BY]-(:Review)-[:REVIEW]-(r:Restaurant)-[:CUISINE]-(c:Cuisine)
    WHERE c.name = $name
    RETURN DISTINCT r.name, r.stars, r.address, r.review_count
    ORDER BY r.stars DESC LIMIT 50
    '''
    nodes = graph.run(query4, id=userid, name=cuisine_name).data()
    count = 0
    print("Alternative restaurants:\n")
    suggestions = []
    for i in nodes:
        if i["r.name"] != None:
            #add = {'name':'another restuarant', 'stars':str(i['r.stars'])}
            suggestions.append( {'name':i['r.name'], 'stars':str(i['r.stars']), 'address':i['r.address'], 'count':i['r.review_count']} )
            print(i["r.name"] + " hello")
            count += 1
            if count >= 5:
                break
    

    return suggestions

def is_open(time, day, hours):
    print(hours)
    print(type(hours))
    hours_list = []
    print("is open day " + day)
    print(type(day))
    hours = str(hours)
    numdays = (hours.count("'")/4)
    numdays = int(numdays)
    print(numdays)
    for i in range(numdays):
        start = hours.find(":")
        end = hours.find(",")
        hours_list.append(hours[(start+3):(end-1)])
        hours = hours[(end+1):]
        
    print(hours_list)
    if day == 'Monday':
        open_hours = hours_list[0]
    elif day == 'Tuesday':
        open_hours = hours_list[1]
    elif day == 'Wednesday':
        open_hours = hours_list[2]
    elif day == 'Thursday':
        open_hours = hours_list[3]
    elif day == 'Friday':
        open_hours = hours_list[4]
    elif day == 'Saturday':
        if numdays < 6:
            return 0
        open_hours = hours_list[5]
    elif day == 'Sunday':
        if numdays < 7:
            return 0
        open_hours = hours_list[6]
    else:
        open_hours = None
        print('Restaurant is not open on this day')
    # print(type(hours))
    # print(hours)
    # print(open_hours)

    x = open_hours.split('-')
    open_time = x[0]
    close_time = x[1]
    o_time = split(open_time)
    c_time = split(close_time)

    req_time = split(time)

    if req_time < o_time or req_time > c_time:
        open = 0
    else:
        open = 1
    return open


def create_db():
    df = pd.read_pickle("fullcsv.pkl")
    print("csv loaded")

    count = 0
    for index, row in df.iterrows():
        start = time.clock()
        print(row['name_x'])
        # end = time.clock()
        # elapsed = end-start
        # print("name time = " +str(elapsed))
        if int(row['stars']) < 2:
            continue
        print("more than 2 stars")
        tempdate = row['date']
        tempdate = tempdate.split("-")
        tempdt = datetime(int(tempdate[0]), int(tempdate[1]), int(tempdate[2][:2]))
        print(tempdt)
        now = datetime.now()
        curr_year = now.year
        three_years_ago = now.replace(year=curr_year-3)
        if three_years_ago > tempdt:
            continue
        print("rev in last three years")
        print("NUM REST ADDED = " + str(count))
        #tempdate = pd.to_datetime(tempdt, format='%Y-%b-%d', utc=True)
        #print(tempdt)
        address = row['address']
        if pd.isnull(row['address']):
            print("no address")
            address = ''
        print(address)
        if pd.isnull(row.loc['hours']):
            print("no hours")
            r = Restaurant(row['name_x'], row['stars'], row['review_count'], address, row['business_id'], '')
        else:
            # hoursdict = ast.literal_eval(row['hours'])
            # hourslist = list(hoursdict.values())
            # print(hourslist)
            # print(type(hourslist))
            #print(row['hours'])
            # print(row['address'])
            # print(type(row['address']))
            # print(type(row['business_id']))
            # print(type(row['hours']))
            r = Restaurant(row['name_x'], row['stars'], row['review_count'], address, row['business_id'], str(row['hours']))
        
    
        # end = time.clock()
        # elapsed = end-start
        # print("hours time = " + str(elapsed))
        r2 = r.new_rest()
        c = City(row['city'])
        c2 = c.new_city()
        loc = Relationship.type("CITY")
        new_relation(loc, r2, c2)
        # end = time.clock()
        # elapsed = end-start
        # print("city time = " + str(elapsed))
        categories_list = row['categories'].split(', ')
        categories_list.remove('Restaurants')
        if categories_list.count('Food') == 1:
            categories_list.remove('Food')
        for i in categories_list:
            cuis = Cuisine(i)
            cuis2 = cuis.new_cuisine()
            new_relation(Relationship.type("CUISINE"), r2, cuis2)
        # end = time.clock()
        # elapsed = end-start
        # print("cat time = " + str(elapsed))
        rev = Review(row['review_id'], row['user_id'], row['business_id'], row['review_stars'], row['useful'], row['date'], row['text'])
        rev2 = rev.new_review()
        new_relation(Relationship.type("REVIEW"), rev2, r2)
        # end = time.clock()
        # elapsed = end-start
        # print("revs time = " + str(elapsed))
        #print("friends = " + row['friends'])
        user = User(row['user_id'], row['name_y'], row['friends'], row['user_review_count'])
        user2 = user.new_user()
        new_relation(Relationship.type("REVIEWED_BY"), rev2, user2)
        # end = time.clock()
        # elapsed = end-start
        # print("user time = " + str(elapsed))
        friends_list = row['friends'].split(', ')
        friend_count = 0
        for i in friends_list:
            friend_rows = df.loc[df['user_id'] == i]
            
            if not friend_rows.empty:
                #print(friend_rows)
                friend_row = friend_rows.head(1).index[0]
                id = df.loc[friend_row, 'user_id']
                name = df.loc[friend_row, 'name_y']
                user_rev_count = df.loc[friend_row, 'user_review_count']
                user_rev_count = user_rev_count.astype(numpy.int32).item()
                friendsofu = df.loc[friend_row, 'friends']
                friend = User(id, name, friendsofu, user_rev_count)
                friend2 = friend.new_user()
                new_relation(Relationship.type("FRIEND"), friend2, user2)
                friend_count+=1
                if friend_count > 7:
                    break
        end = time.clock()
        elapsed = end-start
        print("friends time = " + str(elapsed))
        
        count+=1
        # if count > 10:
        #     break
# f = open("norm.json")
# data_list = json.load(f)
# f2 = open("normrev.json")
# review_list = json.load(f2)
# f3 = open("normuser.json")
# user_list = json.load(f3)

# for j in range(25):
#     i = data_list[j]
#     categories_list = i["categories"].split(", ")
#     categories_list.remove("Restaurants")
#     if categories_list.count("Food") == 1:
#         categories_list.remove("Food")
#     if i['hours'] is None:
#         r = Restaurant(i['name'], i['stars'], i['review_count'], i['address'], i['business_id'], '')
#     else:
#         r = Restaurant(i['name'], i['stars'], i['review_count'], i['address'], i['business_id'], list(i['hours'].values())) #number of reviews
#     r2 = r.new_rest()
#     c = City(i["city"])
#     c2 = c.new_city()
#     loc = Relationship.type("CITY")
#     new_relation(loc, r2, c2)
#     for cat in categories_list:
#         cuis = Cuisine(cat)
#         cuis2 = cuis.new_cuisine()
#         new_relation(Relationship.type("CUISINE"), r2, cuis2)
#     for rev in review_list:
#         if rev["business_id"] == i["business_id"]:
#             review = Review(rev["review_id"], rev["user_id"], rev["business_id"], rev["stars"], rev["useful"], rev["date"], rev["text"])
#             review2 = review.new_review()
#             new_relation(Relationship.type("REVIEW"), review2, r2)
#             for us in user_list:
#                 if rev["user_id"] == us["user_id"]:
#                     user = User(us["user_id"], us["name"], us["friends"], us["review_count"])
#                     user2 = user.new_user()
#                     new_relation(Relationship.type("REVIEWED_BY"), review2, user2)
#                     # friends = us["friends"].split(", ")
#                     # for f in friends:
#                     #     for u in user_list:
#                     #         if u["user_id"] == f and u["user_id"] != us["user_id"]:
#                     #             friend = User(u["user_id"], u["name"], u["friends"], u["review_count"])
#                     #             friend2 = friend.new_user()
#                     #             new_relation(Relationship.type("FRIEND"), friend2, user2)
#                     #             friends_of_friends = u["friends"].split(", ")
#                     #             for fof in friends_of_friends:
#                     #                 for fru in user_list:
#                     #                     if fru["user_id"] == fof and fru["user_id"] != u["user_id"]:
#                     #                         friendof = User(fru["user_id"], fru["name"], fru["friends"], fru["review_count"])
#                     #                         friendof2 = friendof.new_user()
#                     #                         new_relation(Relationship.type("FRIEND"), friendof2, friend2)

#-----------------------------------------------------------------------------------
# cuisine_name = "Mexican"
# query = '''
# MATCH (r:Restaurant)-[:CUISINE]->(c:Cuisine)
# WHERE c.name = $name AND r.open = 1
# RETURN r.name, r.stars, r.address, r.review_count, r.business_id
# ORDER BY r.stars DESC LIMIT 5
# '''
# nodes = graph.run(query, name=cuisine_name).data()
# if not nodes:
#     print("no restaurant matches query")
#     sys.exit(0)
# answer = nodes[1]

# if nodes[0]["r.stars"] > nodes[1]["r.stars"]: # checks for tie
#     answer = nodes[0]
# else: # if there is a tie, pick the restaurant with higher review count
#     if nodes[0]["r.review_count"] >= nodes[1]["review_count"]:
#         answer = nodes[0]
#     else:
#         answer = nodes[1]
#print("Recommended restaurant:")
#print("name: " + answer["r.name"] + ", address: " + answer["r.address"] + ", stars: " + str(answer["r.stars"]) + ", review count: " + str(answer["r.review_count"]))

#busid = answer["r.business_id"] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



# query2 = '''
# MATCH (r:Restaurant)-[:REVIEW]-(rev:Review)
# WHERE r.business_id = $busid
# RETURN rev.userid, rev.stars, rev.date
# ORDER BY rev.useful DESC LIMIT 5
# '''
# nodes = graph.run(query2, busid=busid).data()
# now = datetime.now()
# curr_year = now.year
# two_years_ago = now.replace(year=curr_year-2)
# print("two years ago: ")
# print(two_years_ago)
# if not nodes:
#     print("no reviews match query")
#     sys.exit(0)
#
# answer = None
# for i in nodes:
#     print("rev date: " + i["rev.date"])
#     date_list = i["rev.date"].split("-")
#     date = datetime(int(date_list[0]), int(date_list[1]), int(date_list[2][:2]))
#     if two_years_ago < date:
#         answer = i
#         print("\nrev date: ")
#         print(date)
#         break
# #answer = nodes[0]
# if answer == None:
#     print("No review in past two years\n")
#     sys.exit(0)


#userid = answer["rev.userid"] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# query3 = '''
# MATCH (u:User)
# WHERE u.id = $id
# RETURN u.name
# '''
# name = graph.evaluate(query3, id=userid)
# print("Most useful review of recommended restaurant:\n")
# print("name: " + name + ", stars: " + str(answer["rev.stars"]))

# query4 = '''
# MATCH (u:User)-[:FRIEND*1..2]-(f:User)
# WHERE u.id = $id
# RETURN DISTINCT f.name, f.review_count, f.friends, f.id
# ORDER BY f.review_count DESC LIMIT 50
# '''

# query4 = '''
# MATCH (u:User)-[:FRIEND*1..2]-(f:User)
# WHERE u.id = $id
# WITH DISTINCT f
# ORDER BY f.review_count DESC LIMIT 50
# OPTIONAL MATCH (f)-[:REVIEWED_BY]-(:Review)-[:REVIEW]-(r:Restaurant)-[:CUISINE]-(c:Cuisine)
# WHERE c.name = $name
# RETURN DISTINCT r.name, r.stars, f.review_count
# ORDER BY r.stars DESC LIMIT 50
# '''
# nodes = graph.run(query4, id=userid, name=cuisine_name).data()
# count = 0
# print("Alternative restaurants:\n")
# for i in nodes:
#     if i["r.name"] != None:
#         print(i["r.name"])
#         count += 1
#         if count >= 5:
#             break

# url = "https://api.yelp.com/v3/businesses/"
# api_key = "FxR7UkYfaIi7O6tD9jaGFkSgDxbsPcCILepyktUYIqdhvQEiLGTdRrz0XXzuq_H0d4kFap7K533Yk46OvagCA-NgC4Omw69hZh1oodFI17ONaUZafw0SL1UIu8N9XnYx"
# headers = {'Authorization' : 'bearer %s' % api_key}
# r = requests.get(url=url + busid, headers=headers)
# data = r.json()
# img_url = data["photos"]
# count = 0
# for i in img_url:
#     count+=1
#     img_request = requests.get(i)
#     file = "photo" + str(count) + ".jpg"
#     img = open(file, "wb")
#     img.write(img_request.content)
#     img.close()
