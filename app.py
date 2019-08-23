# app.py
from flask import Flask, jsonify, request, render_template, session
import pandas as pd
import numpy as np
import requests
import time
import warnings
import json

app = Flask(__name__)

app.secret_key = "whatever"

@app.route('/hello', methods=['GET', 'POST'])
def hello():
    # POST request
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # parse as JSON
        return 'OK', 200

    # GET request
    else:
        message = {'greeting':'Hello from Flask!'}
        return jsonify(message)  # serialize and use JSON headers

@app.route('/citytest', methods=['GET', 'POST'])
def citytest():
    response = request.get_json()
    for i in response:
        city = response[i]
        print(city)    

    start_time = time.time()

    ykey = "YELP API KEY"

    yelp_url = 'https://api.yelp.com/v3/businesses/search'
    yelp_headers = {'Authorization': 'Bearer %s' % ykey}

    # Columns of DataFrame

    id_list = []
    name_list = []
    is_closed_list = []
    review_count_list = []
    categories_list = []
    rating_list = []
    latitude_list = []
    longitude_list = []
    price_list = []
    address_list = []
    city_list = []
    zip_code_list = []
    state_list = []
    categories_all_list = []

    restaurant_count = 0

    session.clear()

    for offset in range(0, 1000, 20):
    # print(f'Retrieving restaurants in {city}')
        yelp_params = {'location': city, 'term': 'restaurants', 'limit': '20', 'offset': offset}
        yelp_response = requests.get(yelp_url, yelp_params, headers = yelp_headers)
        yelp_data = yelp_response.json()
    # print(yelp_data)
        restaurant_data = yelp_data['businesses']

        for restaurant in restaurant_data:
            categories_all_list_sub = []
            for category in restaurant['categories']: 
                categories_all_list_sub.append(category['title'])
            
            for category in restaurant['categories']: 
                id_list.append(restaurant['id'])         
                name_list.append(restaurant['name'])
                is_closed_list.append(restaurant['is_closed'])
                review_count_list.append(restaurant['review_count'])
                categories_list.append(category['title'])
                rating_list.append(restaurant['rating'])
                latitude_list.append(restaurant['coordinates']['latitude'])
                longitude_list.append(restaurant['coordinates']['longitude'])
                address_list.append(restaurant['location']['address1'])
                city_list.append(restaurant['location']['city'])
                zip_code_list.append(restaurant['location']['zip_code'])
                state_list.append(restaurant['location']['state'])
                
                categories_all_list.append(', '.join(categories_all_list_sub))

                try:                
                    price_list.append(restaurant['price'])

                except:
                    price_list.append('')

            restaurant_count += 1
            print(f'Restaurant #{restaurant_count} data retrieved.')
            
    # # cast category & zip code lists to sets to remove duplicates for html rendering             
    # new_cat_list = list(set(categories_list))
    # new_zip_list = list(set(zip_code_list))

    # set lists filled by API results as session variables to call elsewhere
    # session['id_list'] = id_list
    # session['name_list'] = name_list
    # session['is_closed_list'] = is_closed_list
    # session['review_count_list'] = review_count_list
    # session['categories_list'] = categories_list
    # session['rating_list'] = rating_list
    # session['latitude_list'] = latitude_list
    # session['longitude_list'] = longitude_list
    # session['price_list'] = price_list
    # session['address_list'] = address_list
    # session['city_list'] = city_list
    # session['zip_code_list'] = zip_code_list
    # session['state_list'] = state_list
    # session['categories_all_list'] = categories_all_list
    # session['new_cat_list'] = new_cat_list
    # session['new_zip_list'] = new_zip_list

    # print API search time result
    # print (session['categories_list'])

    restaurants_df = pd.DataFrame({
    'ID': id_list,
    'Name': name_list,
    'Is_Closed': is_closed_list,
    'Review_Count': review_count_list,
    'Categories_All': categories_all_list,
    'Categories': categories_list,
    'Rating': rating_list,
    'Latitude': latitude_list,
    'Longitude': longitude_list,
    'Price': price_list,
    'Address': address_list,
    'City': city_list,
    'Zip_Code': zip_code_list,
    'State': state_list
    })

    # print(restaurants_df.head())

    restaurants_df.drop_duplicates(keep = False, inplace = True)
    restaurants_df.dropna(subset = ['Address'], inplace = True)
    restaurants_df.dropna(subset = ['Price'], inplace = True)
    restaurants_df = restaurants_df[restaurants_df.Price != '']
    restaurants_df = restaurants_df[restaurants_df.Zip_Code != '']
    restaurants_df['Price'].replace({'$$$$': 4, '$$$': 3, '$$': 2, '$': 1}, inplace = True)
    restaurants_df['Price'] = pd.to_numeric(restaurants_df['Price'])

    restaurants_df.to_csv('restaurants_df.csv', index=False)

    print("--- %s seconds ---" % (time.time() - start_time))

    # cast category & zip code lists to sets to remove duplicates for html rendering (get list after cleanup)            
    new_cat_list = list(set(list(restaurants_df.Categories)))
    new_zip_list = list(set(list(restaurants_df.Zip_Code)))

    print("Number of items in list: ", len(new_cat_list))        
    
    return jsonify(new_cat_list, new_zip_list)

@app.route('/useroptions', methods=['GET', 'POST'])
def useroptions():

    warnings.filterwarnings('ignore')
    
    # get response from javascript and convert to json
    response = request.get_json()
    print(response)
    
    # set variables based on user responses   
    user_categories = response[0]
    user_zipcode = response[1]
    user_price = response[2]

    # set user responses as session vars to use in /map route
    session['user_categories'] = user_categories
    session['user_zipcode'] = user_zipcode
    session['user_price'] = user_price

    restaurants_df = pd.read_csv('restaurants_df.csv')

    print(restaurants_df.head())

    # create dataframe based on user choices
    # restaurants_df = pd.DataFrame({
    #     'ID': session.get('id_list'),
    #     'Name': session.get('name_list'),
    #     'Is_Closed': session.get('is_closed_list'),
    #     'Review_Count': session.get('review_count_list'),
    #     'Categories_All': session.get('categories_all_list'),
    #     'Categories': session.get('categories_list'),
    #     'Rating': session.get('rating_list'),
    #     'Latitude': session.get('latitude_list'),
    #     'Rating': session.get('rating_list'),
    #     'Latitude': session.get('latitude_list'),
    #     'Longitude': session.get('longitude_list'),
    #     'Price': session.get('price_list'),
    #     'Address': session.get('address_list'),
    #     'City': session.get('city_list'),
    #     'Zip_Code': session.get('zip_code_list'),
    #     'State': session.get('state_list')
    #     })
    
    # print(session.get('categories_list'))

    # restaurants_df.drop_duplicates(keep = False, inplace = True)
    # restaurants_df.dropna(subset = ['Address'], inplace = True)
    # restaurants_df.dropna(subset = ['Price'], inplace = True)
    # restaurants_df = restaurants_df[restaurants_df.Price != '']
    # restaurants_df = restaurants_df[restaurants_df.Zip_Code != '']
    # restaurants_df['Price'].replace({'$$$$': 4, '$$$': 3, '$$': 2, '$': 1}, inplace = True)
    # restaurants_df['Price'] = pd.to_numeric(restaurants_df['Price'])

    # print(restaurants_df.Categories)

    cat_list = list(set(list(restaurants_df.Categories)))
    cat_list.sort()

    print(cat_list)

    # cat_list_df= pd.DataFrame(columns=session.get('new_cat_list'))
    cat_list_df = pd.DataFrame(columns=cat_list)
    cat_list_df['new_col'] = pd.Series()

    new_df = pd.merge(restaurants_df, cat_list_df, how='left', left_on = restaurants_df.ID, right_on = cat_list_df.new_col)

    for i in cat_list:
        new_df.loc[(new_df.Categories.str.contains(i)==True), i] = 1

    new_df.drop(axis = 1, columns = ['Categories', 'key_0', 'new_col'], inplace = True)
    new_df.drop_duplicates(subset = 'ID', inplace = True)
    new_df.fillna(0, inplace = True)

    modeling_df = new_df.drop(axis = 1, columns = ['ID', 'Name', 'Categories_All', 'Is_Closed', 'Latitude', 'Longitude', 'Address', 'City', 'State'])
    modeling_df['Zip_Code'] = modeling_df['Zip_Code'].astype('object')
    modeling_df = pd.get_dummies(modeling_df)

    L = list(modeling_df.columns)

    for i in range(3):
        L.pop(0)

    modeling_df[L] = modeling_df[L].astype('category')

    X = modeling_df.drop(axis = 1, columns = ['Review_Count', 'Rating'])
    y = modeling_df[['Rating']]

    # set test & traning data sets
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.5)
    print(X_train.shape, y_train.shape)
    print(X_test.shape, y_test.shape)

    # random forest set up
    from sklearn.ensemble import RandomForestRegressor
    rf = RandomForestRegressor(n_jobs = -1, oob_score=True, verbose=0, max_depth=3)
    rf = rf.fit(X_train, y_train)

    user_df = X.drop(X.index)

    user_df_col = list(user_df.columns)
    user_df_col.pop(0)

    user_df['Price'] = [0]

    user_df = user_df.fillna(0).astype(np.int64)

    # print(user_df)

    user_df.Price = user_price

    zip_column = [col for col in user_df.columns if user_zipcode in col]
    user_df[zip_column] = 1

    for category in user_categories:
        cat_column = [col for col in user_df.columns if category == col]
        user_df[cat_column[0]] = 1

    user_df[user_df_col] = user_df[user_df_col].astype('category')

    print('************** User Data:')
    print(user_df)

    # Prediction
    user_prediction = np.round(rf.predict(user_df) * 2) / 2
    user_prediction = user_prediction[0] #4
    # user_prediction = 4

    map_df = restaurants_df[restaurants_df.Is_Closed == False].drop(axis = 1, columns = ['ID', 'Is_Closed', 'Categories'])
    map_df.drop_duplicates(inplace = True)

    map_df = map_df[(map_df.Zip_Code == int(user_zipcode)) & (map_df.Categories_All.str.contains('|'.join(user_categories)))]
    map_df['Price'].replace({4 : '$$$$', 3: '$$$', 2 : '$$', 1 : '$'}, inplace = True)
    map_df.to_csv('map_info.csv')

    # print(map_df_display)
    
    # Prediction to display
    print(user_prediction)
    return jsonify(user_prediction)

@app.route("/map", methods=["GET", "POST"])
def send():
    
    map_df=pd.read_csv("map_info.csv")
    
    name_list=list(map_df.Name)
    review_list=list(map_df.Review_Count)
    category_list=list(map_df.Categories_All)
    rating_list=list(map_df.Rating)
    latitude_list=list(map_df.Latitude)
    longitude_list=list(map_df.Longitude)
    price_list=list(map_df.Price)
    address_list=list(map_df.Address)
    city_list=list(map_df.City)
    zip_list=list(map_df.Zip_Code)
    state_list=list(map_df.State)
    
    return render_template('map.html', names=json.dumps(name_list), reviews=json.dumps(review_list), categories=json.dumps(category_list), ratings=json.dumps(rating_list), latitude=json.dumps(latitude_list), longitude=json.dumps(longitude_list), price=json.dumps(price_list), address=json.dumps(address_list), city=json.dumps(city_list), zip_code=json.dumps(zip_list), state=json.dumps(state_list)) 

    # map_df = pd.DataFrame(session['user_categories'], session['user_zipcode'], session['user_price'])

    # print(map_df)
    
    
    # session['name_list'] = list(map_df.Name)
    # session['review_list'] = list(map_df.Review_Count)
    # session['category_list'] = list(map_df.Categories_All)
    # session['rating_list'] = list(map_df.Rating)
    # session['latitude_list'] = list(map_df.Latitude)
    # session['longitude_list'] = list(map_df.Longitude)
    # session['price_list'] = list(map_df.Price)
    # session['address_list'] = list(map_df.Address)
    # session['city_list'] = list(map_df.City)
    # session['zip_list'] = list(map_df.Zip_Code)
    # session['state_list'] = list(map_df.State)
    
    # return render_template('index.html',
    # names=json.dumps(session['name_list']),
    # reviews=json.dumps(session['review_list']),
    # categories=json.dumps(session['category_list']),
    # ratings=json.dumps(session['rating_list']),
    # latitude=json.dumps(session['latitude_list']),
    # longitude=json.dumps(session['longitude_list']),
    # price=json.dumps(session['price_list']),
    # address=json.dumps(session['address_list']),
    # city=json.dumps(session['city_list']),
    # zip_code=json.dumps(session['zip_list']),
    # state=json.dumps(session['state_list'])
    # )    
        
@app.route('/')
def index():
    # look inside `templates` and serve `index.html`
    return render_template('index.html')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

if __name__ == "__main__":
     app.run(debug=True)