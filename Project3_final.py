#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Dependencies
import pandas as pd
import numpy as np
import requests
import time


# In[2]:


pd.options.display.max_rows = 999
pd.options.display.max_columns = 999


# In[3]:


start_time = time.time()
# Get data from Yelp

ykey = "Ii7Pa9IZug_H12vEjc6Z8Q7PVKDIkFXZDYLKJR9xdtTWkgw75dqoWkhpaHQ__jFcmvrmytLdF3plPxFDfw6cJqe5ugr-HOUirTiSPMFI7aYZ1W9mvifY2AJY7Sk5XXYx"

yelp_url = 'https://api.yelp.com/v3/businesses/search'
yelp_headers = {'Authorization': 'Bearer %s' % ykey}

# Input from user
city = 'Los Angeles, CA'

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

for offset in range(0, 1000, 20):
#         print(f'Retrieving restaurants in {city}')
    yelp_params = {'location' : city, 'term': 'restaurants', 'limit' : '20', 'offset' : offset}
    yelp_response = requests.get(yelp_url, yelp_params, headers = yelp_headers)
    yelp_data = yelp_response.json()
#         print(yelp_data)
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
        
            
print("--- %s seconds ---" % (time.time() - start_time))               


# In[4]:


restaurants_df = pd.DataFrame({'ID' : id_list, 'Name' : name_list, 'Is_Closed' : is_closed_list,                               'Review_Count' : review_count_list, 'Categories_All' : categories_all_list,                               'Categories' : categories_list, 'Rating' : rating_list, 'Latitude' : latitude_list,                               'Rating' : rating_list, 'Latitude' : latitude_list, 'Longitude' : longitude_list,                               'Price' : price_list, 'Address' : address_list, 'City' : city_list,                               'Zip_Code' : zip_code_list, 'State' : state_list})

restaurants_df.drop_duplicates(keep = False, inplace = True)
restaurants_df.dropna(subset = ['Address'], inplace = True)
restaurants_df.dropna(subset = ['Price'], inplace = True)

restaurants_df = restaurants_df[restaurants_df.Price != '']
restaurants_df['Price'].replace({'$$$$' : 4, '$$$' : 3, '$$' : 2, '$' : 1}, inplace = True)
restaurants_df['Price'] = pd.to_numeric(restaurants_df['Price'])

restaurants_df['Categories'].replace(['American (New)', 'American (Traditional)'], 'American', inplace = True)
restaurants_df['Categories'].replace(['New Mexican Cuisine'], 'Mexican', inplace = True)


# In[5]:


restaurants_df.count()


# In[6]:


restaurants_df.head()


# In[7]:


category_df = restaurants_df[['Categories']]


# In[8]:


cat_list = list(category_df.Categories.unique())


# In[9]:


cat_list.sort()


# In[10]:


cat_list


# In[11]:


len(cat_list)


# In[12]:


cat_list_df= pd.DataFrame(columns=cat_list)


# In[13]:


cat_list_df


# In[14]:


new_df = pd.merge(restaurants_df, cat_list_df, how='left', left_on = restaurants_df.ID, right_on = cat_list_df.Southern)


# In[15]:


new_df.head(5)


# In[16]:


cat_list_df


# In[17]:


for i in cat_list:
    new_df.loc[(new_df.Categories.str.contains(i)==True), i] = 1


# In[18]:


new_df.drop(axis = 1, columns = ['Categories', 'key_0'], inplace = True)


# In[19]:


new_df.drop_duplicates(subset = 'ID', inplace = True)


# In[20]:


new_df.count()


# In[21]:


new_df.fillna(0, inplace = True)


# In[22]:


new_df.head()


# In[44]:


zip_code_df = restaurants_df[['Zip_Code']]


# In[45]:


zip_code_list = list(zip_code_df.Zip_Code.unique())


# In[48]:


zip_code_list.sort()
zip_code_list


# In[23]:


modeling_df = new_df.drop(axis = 1, columns = ['ID', 'Name', 'Categories_All', 'Is_Closed', 'Latitude', 'Longitude',                                               'Address', 'City', 'State'])


# In[24]:


len(new_df[new_df.Southern == 1])


# In[25]:


modeling_df.head()


# In[26]:


map_df = restaurants_df[restaurants_df.Is_Closed == False].drop(axis = 1, columns = ['ID', 'Is_Closed', 'Categories'])


# In[27]:


map_df.drop_duplicates(inplace = True)


# In[28]:


map_df.count()


# In[29]:


map_df.head()


# In[30]:


modeling_df = pd.get_dummies(modeling_df)


# In[31]:


L = list(modeling_df.columns)

for i in range(3):
    L.pop(0)


# In[32]:


modeling_df[L] = modeling_df[L].astype('category')


# In[33]:


modeling_df.dtypes


# In[34]:


modeling_df.columns


# In[35]:


X = modeling_df.drop(axis = 1, columns = ['Review_Count', 'Rating'])
y = modeling_df[['Rating']]


# In[36]:


from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.5)

print(X_train.shape, y_train.shape)
print(X_test.shape, y_test.shape)


# In[37]:


import warnings
warnings.filterwarnings('ignore')


# In[38]:


from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

rf = RandomForestRegressor(n_jobs = -1, oob_score=True, verbose=0, max_depth=3)
rf = rf.fit(X_train, y_train)

print(mean_squared_error(y_train, rf.predict(X_train).ravel()))
print(mean_squared_error(y_test, rf.predict(X_test).ravel()))


# In[104]:


from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn import metrics
scores_mse = cross_val_score(rf, X_train, y_train, scoring = 'neg_mean_squared_error' ,cv=6)
scores_mse


# In[105]:


from scipy.stats import sem, t
from scipy import mean

confidence = 0.95

data = scores_mse

n = len(data)
m = mean(data)
std_err = sem(data)
h = std_err * t.ppf((1 + confidence) / 2, n - 1)

end = -m + h

start = -m - h

print(f'We are 95% confident that the true mean of the population lies with in {start, end}')


# In[39]:


np.round(rf.predict(X_test)[0:5] * 2) / 2


# In[40]:


y_test[0:5]


# In[121]:


np.max(np.round(rf.predict(X_test) * 2) / 2)


# In[170]:


user_df = X.drop(X.index)
user_df['Price'] = [0]
user_df.fillna(0, inplace = True)


# In[171]:


user_df


# In[155]:


# Inputs from user
user_zipcode = '91604'
user_categories = ['Mexican', 'Bars']
user_price = 2


# In[172]:


user_df.Price = user_price


# In[173]:


zip_column = [col for col in user_df.columns if user_zipcode in col]
user_df[zip_column] = 1


# In[174]:


for category in user_categories:
    cat_column = [col for col in user_df.columns if category == col]
    user_df[cat_column] = 1


# In[175]:


user_df.fillna(0, inplace = True)


# In[176]:


user_df


# In[148]:


user_prediction = np.round(rf.predict(user_df) * 2) / 2
user_prediction = user_prediction[0]

# Prediction to display
user_prediction


# In[149]:


map_df_display = map_df[(map_df.Zip_Code == user_zipcode) & (map_df.Categories_All.str.contains('|'.join(user_categories)))]


# In[177]:


map_df_display['Price'].replace({4 : '$$$$', 3: '$$$', 2 : '$$', 1 : '$'}, inplace = True)


# In[178]:


# df to create geoJSON for Leaflet map
map_df_display


# In[152]:


# Price Explanation:
# 1 - $= under $10
# 2 - $$= $11-$30
# 3 - $$$= $31-$60
# 4 - $$$$= above $61


# In[179]:


map_df_display.to_csv('map_info.csv')


# In[ ]:




