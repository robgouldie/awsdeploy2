import json
import requests

def normalize():
    data_list = []
    norm_list = []

    data_list = make_dict_list("business.json")

    for a in data_list:
        if (a["categories"] is not None):
            if (a["state"] == "AZ" and (a["city"] == "Phoenix")):# or a["city"] == "Scottsdale")):
                if ("Restaurants" in a["categories"]): # check for restaurants
                    if (a["stars"] > 2.5): # check for positive reviews
                        norm_list.append(a) # list of dictionaries
                        print("restaurant name: " + a["name"])
                        if a["name"] == "Five Guys":
                            return

    # with open('norm.json', 'w') as outfile:
    #     # for temp in norm_list:
    #     #     outfile.write(json.dumps(temp))
    #     json.dump(norm_list, outfile)

    return norm_list

def norm_review():
    review_list = []
    rev_norm_list = []
    data_list = []
    user_list = first_num("../user.json", 50000)
    review_list1 = first_num("../review.json", 50000)
    review_list = []
    count = 0
    f = open("norm.json")
    data_list = json.load(f)

    for a in review_list1:
        for b in user_list:
            if a["user_id"] == b["user_id"]:
                review_list.append(a)
                print("review made by user in list")

    for a in data_list:
        for b in review_list:
            if b["business_id"] == a["business_id"]:
                rev_norm_list.append(b)
                count += 1
                print("review of " + a["name"] + " added in loc: " + a["city"])

    with open('normrev.json', 'w') as outfile:
        json.dump(rev_norm_list, outfile)

    print("review count = " + str(count))
    return rev_norm_list

def norm_user():
    user_list = first_num("../user.json", 50000)
    user_norm_list = []
    review_list = []
    f = open("normrev.json")
    review_list = json.load(f)

    for a in review_list:
        for b in user_list:
            if a["user_id"] == b["user_id"]:
                if check_if_added(a["user_id"], user_norm_list) == 1:
                    user_norm_list.append(b)
                    print("user added")

    with open('normuser.json', 'w') as outfile:
        json.dump(user_norm_list, outfile)

def check_if_added(userid, user_list):
    for i in user_list:
        if i["user_id"] == userid:
            return 0
    return 1

def norm_photos():
    photo_list = first_num("photo.json")
    photo_norm_list = []
    businesses = normalize()
    for a in photo_list:
        if a["label"] == "food":
            for b in businesses:
                if a["business_id"] == b["business_id"]:
                    photo_norm_list.append(a)
                    break

    with open('normphoto.json', 'w') as outfile:
        json.dump(photo_norm_list, outfile)

def make_dict_list(filename):
    data_list = []

    with open(filename) as json_file:
        for temp in json_file:
            data = json.loads(temp)
            data_list.append(data)

    return data_list

def first_num(filename, num):
    data_list = []
    count = 0
    with open(filename) as json_file:
        for temp in json_file:
            data = json.loads(temp)
            data_list.append(data)
            count += 1
            if count > num:
                break

    return data_list

def main():
    #normalize()
    #norm_review()
    #norm_user()
    norm_photos()

    # f = open("normrev.json")
    # rev_list = json.load(f)
    # f2 = open("normuser.json")
    # user_list = json.load(f2)
    # count = 0
    # for a in rev_list:
    #     for b in user_list:
    #         if a["user_id"] == b["user_id"]:
    #             count += 1
    # print("count in main " + str(count))
    # count = 0
    # f = open("norm.json")
    # data_list = json.load(f)
    # for i in data_list:
    #     print("categories: " + i["categories"])
    #     count += 1
    # print(count)

if __name__ == "__main__":
    main()
