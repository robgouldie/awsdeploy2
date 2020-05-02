import pandas

business_json_path = "../business.json"
df_b = pandas.read_json(business_json_path, lines=True)
print("after read json")
df_b = df_b[df_b['is_open']==1]
df_b = df_b[df_b['city'] == 'Phoenix']
df_b = df_b[df_b['state'] == 'AZ']
drop_columns = ['latitude', 'longitude', 'attributes']
df_b = df_b.drop(drop_columns, axis=1)
restaurants = df_b[df_b['categories'].str.contains('Restaurants', case=False, na=False)]
#restaurants = restaurants[restaurants["state"].str.contains("Phoenix", case=False, na=False)]
print("after restaurants")
review_json_path = "../review.json"
size = 10000
review = pandas.read_json(review_json_path, lines=True, dtype={'review_id':str,'user_id':str, 'business_id':str,'stars':int, 'date':str,'text':str,'useful':int,'funny':int,'cool':int}, chunksize=size)
print("after reviews")
user_json_path = "../user.json"
user = pandas.read_json(user_json_path, lines=True, dtype={'user_id':str,'name':str,'review_count':int,'yelping_since':str,'friends':str,'useful':int, 'funny':int, 'cool':int, 'fans':int, 'elite':int, 'average_stars':float, 'compliment_hot':int, 'compliment_more':int, 'compliment_profile':int, 'compliment_cute':int, 'compliment_list':int, 'compliment_note':int, 'compliment_plain':int, 'compliment_cool':int, 'compliment_funny':int, 'compliment_writer':int, 'compliment_photos':int}, chunksize=size)
print("after users")
# There are multiple chunks to be read
chunk_list = []
for chunk_review in review:
    # Drop columns that aren't needed
    chunk_review = chunk_review.drop(['funny','cool'], axis=1)
    # Renaming column name to avoid conflict with business overall star rating
    chunk_review = chunk_review.rename(columns={'stars': 'review_stars'})
    # Inner merge with edited business file so only reviews related to the business remain
    chunk_merged = pandas.merge(restaurants, chunk_review, on='business_id', how='inner')
    # Show feedback on progress
    print(f"{chunk_merged.shape[0]} out of {size:,} related reviews")
    chunk_list.append(chunk_merged)
# After trimming down the review file, concatenate all relevant data back to one dataframe
df1 = pandas.concat(chunk_list, ignore_index=True, join='outer', axis=0)

chunk_list = []
for chunk_user in user:
    # Drop columns that aren't needed
    chunk_user = chunk_user.drop(['yelping_since','funny','cool', 'fans', 'elite', 'average_stars', 'compliment_hot', 'compliment_more', 'compliment_profile', 'compliment_cute', 'compliment_list', 'compliment_note', 'compliment_plain', 'compliment_cool', 'compliment_funny', 'compliment_writer', 'compliment_photos'], axis=1)
    # Renaming column name to avoid conflict with business overall star rating
    chunk_user = chunk_user.rename(columns={'useful': 'user_useful'})
    chunk_user = chunk_user.rename(columns={'review_count':'user_review_count'})
    # Inner merge with edited business file so only reviews related to the business remain
    chunk_merged = pandas.merge(df1, chunk_user, on='user_id', how='inner')
    # Show feedback on progress
    print(f"{chunk_merged.shape[0]} out of {size:,} related users")
    chunk_list.append(chunk_merged)
# After trimming down the review file, concatenate all relevant data back to one dataframe
df = pandas.concat(chunk_list, ignore_index=True, join='outer', axis=0)

csv_name = "businesses_reviews_users.csv"
df.to_csv(csv_name, index=False)

#dtype={'user_id':str,'name':str,'review_count':int,'yelping_since':str,'friends':str,'useful':int, 'funny':int, 'cool':int, 'fans':int, 
