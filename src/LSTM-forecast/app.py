'''
Goal of LSTM microservice:
1. LSTM microservice will accept the GitHub data from Flask microservice and will forecast the data for next 1 year based on past 30 days
2. It will also plot three different graph (i.e.  "Model Loss", "LSTM Generated Data", "All Issues Data") using matplot lib 
3. This graph will be stored as image in Google Cloud Storage.
4. The image URL are then returned back to Flask microservice.
'''
# Import all the required packages
from flask import Flask, jsonify, request, make_response
import os
from dateutil import *
from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
from flask_cors import CORS

# Tensorflow (Keras & LSTM) related packages
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Input, Dense, LSTM, Dropout
from tensorflow.python.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

# Import required storage package from Google Cloud Storage
from google.cloud import storage

# Facebook 
from prophet import Prophet 

# Stats Model
import statsmodels.api as sm 

# Initilize flask app
app = Flask(__name__)
# Handles CORS (cross-origin resource sharing)
CORS(app)
# Initlize Google cloud storage client
client = storage.Client()

# Add response headers to accept all types of  requests

def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

#  Modify response headers when returning to the origin

def build_actual_response(response):
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response



'''
IMPLEMENTATION OF FACEBOOK PROPHET
'''
'''CREATED ISSUES'''
@app.route('/api/createdprophestisc', methods=['POST'])
def fbprophetis():
    body = request.get_json()
    type = body["type"]
    repo_name = body["repo"]
    issues = body["issues"]

    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')


    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')

    LOCAL_IMAGE_PATH = "static/images/"
    FORECAST_IMAGE_NAME = "fbprophet_forecast_" + type +"_"+ repo_name + ".png"
    FORECAST_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_IMAGE_NAME

    FORECAST_COMPONENTS_IMAGE_NAME = "fbprophet_forecast_components_" + type +"_" + repo_name + ".png"
    FORECAST_COMPONENTS_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME

    df = pd.DataFrame(issues)
    df1 = df.groupby(['created_at'], as_index = False).count()
    dataFrame = df1[['created_at','issue_number']]
    dataFrame.columns = ['ds', 'y']
    model = Prophet(daily_seasonality=True, ptimizer='lbfgs')
    model.fit(dataFrame)
    future = model.make_future_dataframe(periods=60)
    forecast = model.predict(future)
    forcast_fig1 = model.plot(forecast)
    forcast_fig2 = model.plot_components(forecast)
    forcast_fig1.savefig(LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)
    forcast_fig2.savefig(LOCAL_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME)

    


    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(FORECAST_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)

    new_blob = bucket.blob(FORECAST_COMPONENTS_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME)


    json_response = {
        "fbprophet_forecast_url": FORECAST_IMAGE_URL,
        "fbprophet_forecast_components_url": FORECAST_COMPONENTS_IMAGE_URL
    }

    return jsonify(json_response)

'''CLOSED ISSUES'''
@app.route('/api/closedprophestisc', methods=['POST'])
def fbprophetisc():
    body = request.get_json()
    type = body["type"]
    repo_name = body["repo"]
    print("type",type)
    issues = body["issues"]

    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')

    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')

    LOCAL_IMAGE_PATH = "static/images/"
    FORECAST_IMAGE_NAME = "fbprophet_forecast_" + type +"_"+ repo_name + ".png"
    FORECAST_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_IMAGE_NAME

    FORECAST_COMPONENTS_IMAGE_NAME = "fbprophet_forecast_components_" + type +"_" + repo_name + ".png"
    FORECAST_COMPONENTS_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME


    df = pd.DataFrame(issues)
    df1 = df.groupby(['closed_at'], as_index = False).count()
    dataFrame = df1[['closed_at','issue_number']]
    dataFrame.columns = ['ds', 'y']
    model = Prophet(daily_seasonality=True)
    model.fit(dataFrame)
    future = model.make_future_dataframe(periods=60)
    forecast = model.predict(future)
    forcast_fig1 = model.plot(forecast)
    forcast_fig2 = model.plot_components(forecast)
    forcast_fig1.savefig(LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)
    forcast_fig2.savefig(LOCAL_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME)

    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(FORECAST_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)

    new_blob = bucket.blob(FORECAST_COMPONENTS_IMAGE_NAME)
    new_blob.upload_from_filename(filename=LOCAL_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME)

    json_response = {
        "fbprophet_forecast_url": FORECAST_IMAGE_URL,
        "fbprophet_forecast_components_url": FORECAST_COMPONENTS_IMAGE_URL
    }

    return jsonify(json_response)

@app.route('/api/prophetpull', methods=['POST'])
def fbprophetpull():
    body = request.get_json()
    pull_req_response = body["pulls"]
    repo_name = body["repo"]
    type = body["type"]


    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')


    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')

    LOCAL_IMAGE_PATH = "static/images/"
    FORECAST_IMAGE_NAME = "fbprophet_pull_" + type +"_"+ repo_name + ".png"
    FORECAST_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_IMAGE_NAME

    FORECAST_COMPONENTS_IMAGE_NAME = "fbprophet_pull_component_" + type +"_" + repo_name + ".png"
    FORECAST_COMPONENTS_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME

    df = pd.DataFrame(pull_req_response)
    df1 = df.groupby(['created_at'], as_index = False).count()
    dataFrame = df1[['created_at','pull_req_number']]
    dataFrame.columns = ['ds', 'y']
    model = Prophet(daily_seasonality=True)
    model.fit(dataFrame)
    future = model.make_future_dataframe(periods=60)
    forecast = model.predict(future)
    forcast_fig1 = model.plot(forecast)
    forcast_fig2 = model.plot_components(forecast)
    forcast_fig1.savefig(LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)
    forcast_fig2.savefig(LOCAL_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME)

    
    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(FORECAST_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)

    new_blob = bucket.blob(FORECAST_COMPONENTS_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME)


    json_response = {
        "fbprophet_forecast_url": FORECAST_IMAGE_URL,
        "fbprophet_forecast_components_url": FORECAST_COMPONENTS_IMAGE_URL
    }

    return jsonify(json_response)

@app.route('/api/prophetcommits', methods=['POST'])
def fbprophetcommits():
    body = request.get_json()
    commit_response = body["commits"]
    repo_name = body["repo"]
    type = body["type"]
    print("type:",type)


    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')

    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')

    LOCAL_IMAGE_PATH = "static/images/"
    FORECAST_IMAGE_NAME = "fbprophet_commit_" + type +"_"+ repo_name + ".png"
    FORECAST_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_IMAGE_NAME

    FORECAST_COMPONENTS_IMAGE_NAME = "fbprophet_commit_components_" + type +"_" + repo_name + ".png"
    FORECAST_COMPONENTS_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME

    df = pd.DataFrame(commit_response)
    df1 = df.groupby(['created_at'], as_index = False).count()
    dataFrame = df1[['created_at','commit_number']]
    dataFrame.columns = ['ds', 'y']
    model = Prophet(daily_seasonality=True)
    model.fit(dataFrame)
    future = model.make_future_dataframe(periods=60)
    forecast = model.predict(future)
    forcast_fig1 = model.plot(forecast)
    forcast_fig2 = model.plot_components(forecast)
    forcast_fig1.savefig(LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)
    forcast_fig2.savefig(LOCAL_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME)


    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(FORECAST_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)

    new_blob = bucket.blob(FORECAST_COMPONENTS_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_COMPONENTS_IMAGE_NAME)

    json_response = {
        "fbprophet_forecast_url": FORECAST_IMAGE_URL,
        "fbprophet_forecast_components_url": FORECAST_COMPONENTS_IMAGE_URL
    }
    return jsonify(json_response)

'''FACEBOOK PROPHET IMPLEMENTATION OVER'''

'''
API route for PULL  requests
'''
@app.route('/api/pulls', methods=['POST'])
def pulls():
    body = request.get_json()
    # print(body)
    pulls = body["pulls"]
    type = body["type"]
    repo_name = body["repo"]
    
    '''DATASET FOR PULLS'''
    data_frame = pd.DataFrame(pulls)
    df1 = data_frame.groupby(["created_at"], as_index=False).count()
    df = df1[["created_at", 'pull_req_number']]
    df.columns = ['ds', 'y']

    df['ds'] = df['ds'].astype('datetime64[ns]')
    array = df.to_numpy()
    x = np.array([time.mktime(i[0].timetuple()) for i in array])
    y = np.array([i[1] for i in array])

    Y = df['y'].values
    firstDay = df['ds'].min()
    Ys = [0] * ((max(df['ds']) - firstDay).days + 1)
    days = pd.Series([firstDay + timedelta(days=i) for i in range(len(Ys))])
    for x, y in zip(df['ds'], Y):
        Ys[(x - firstDay).days] = y
    Ys = np.array(Ys)
    Ys = Ys.astype('float32')
    Ys = np.reshape(Ys, (-1, 1))
    # Apply min max scaler to transform the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    Ys = scaler.fit_transform(Ys)
    # Divide training - test data with 80-20 split
    train_size = int(len(Ys) * 0.80)
    test_size = len(Ys) - train_size
    train, test = Ys[0:train_size, :], Ys[train_size:len(Ys), :]
    print('train size for pulls:', len(train), ", test size for pulls:", len(test))

    # Create the training and test dataset
    def create_dataset(dataset, look_back=1):
        X, Y = [], []
        for i in range(len(dataset)-look_back-1):
            a = dataset[i:(i+look_back), 0]
            X.append(a)
            Y.append(dataset[i + look_back, 0])
        return np.array(X), np.array(Y)
    '''
    Look back decides how many days of data the model looks at for prediction
    Here LSTM looks at approximately one month data
    '''
     
    #Look back decides how many days of data the model looks at for prediction
    look_back = min(30, len(test) - 2)
    print(len(test))

    # Assuming create_dataset is a function that formats the data for LSTM
    if len(test) > look_back + 1:
        X_test, Y_test = create_dataset(test, look_back)
    else:
        print("Test dataset is too small for the specified look_back period.")
    X_train, Y_train = create_dataset(train, look_back)
    
    # Additional check: Ensure that X_test and X_train are not empty
    if len(X_train) == 0:
        print("X_train is empty. Check the train dataset and look_back parameter.")
    if len(X_test) == 0:
        print("X_test is empty. Check the test dataset and look_back parameter.")

    # Add a check to avoid reshaping if the dataset is empty
    if len(X_train) > 0:
        X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    if len(X_test) > 0:
        X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    # Verifying the shapes
    print('Shapes:', X_train.shape, X_test.shape, Y_train.shape, Y_test.shape)

    # Model to forecast
    model = Sequential()
    model.add(LSTM(100, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Fit the model with training data and set appropriate hyper parameters
    history = model.fit(X_train, Y_train, epochs=20, batch_size=70, validation_data=(X_test, Y_test),
                        callbacks=[EarlyStopping(monitor='val_loss', patience=10)], verbose=1, shuffle=False)

    '''
    Creating image URL
    BASE_IMAGE_PATH refers to Google Cloud Storage Bucket URL.Add your Base Image Path in line 145
    if you want to run the application local
    LOCAL_IMAGE_PATH refers local directory where the figures generated by matplotlib are stored
    These locally stored images will then be uploaded to Google Cloud Storage
    '''
    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')
    # DO NOT DELETE "static/images" FOLDER as it is used to store figures/images generated by matplotlib
    LOCAL_IMAGE_PATH = "static/images/"

    # Creating the image path for model loss, LSTM generated image and all issues data image
    MODEL_LOSS_IMAGE_NAME = "model_loss_" + type +"_"+ repo_name + ".png"
    MODEL_LOSS_URL = BASE_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME

    LSTM_GENERATED_IMAGE_NAME = "lstm_generated_data_" + type +"_" + repo_name + ".png"
    LSTM_GENERATED_URL = BASE_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME

    ALL_PULLS_DATA_IMAGE_NAME = "all_pulls_data_" + type + "_"+ repo_name + ".png"
    ALL_PULLS_DATA_URL = BASE_IMAGE_PATH + ALL_PULLS_DATA_IMAGE_NAME

    # Add your unique Bucket Name if you want to run it local
    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')
    
    # Plot the model loss image
    plt.figure(figsize=(8, 4))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Test Loss')
    plt.title('Model Loss For ' + type)
    plt.ylabel('Loss')
    plt.xlabel('Epochs')
    plt.legend(loc='upper right')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)

    # Predict pulls for test data
    y_pred = model.predict(X_test)

    # Plot the LSTM Generated image
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(np.arange(0, len(Y_train)), Y_train, 'g', label="history")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             Y_test, marker='.', label="true")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             y_pred, 'r', label="prediction")
    axs.legend()
    axs.set_title('LSTM Generated Data For ' + type)
    axs.set_xlabel('Time Steps')
    axs.set_ylabel('Issues')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)

    # Plot the All pulls data images
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(X, Ys, 'purple', marker='.')
    locator = mdates.AutoDateLocator()
    axs.xaxis.set_major_locator(locator)
    axs.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    axs.legend()
    axs.set_title('All Issues Data')
    axs.set_xlabel('Date')
    axs.set_ylabel('Issues')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + ALL_PULLS_DATA_IMAGE_NAME)
    
    # Uploads an images into the google cloud storage bucket
    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(MODEL_LOSS_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)
    new_blob = bucket.blob(ALL_PULLS_DATA_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + ALL_PULLS_DATA_IMAGE_NAME)
    new_blob = bucket.blob(LSTM_GENERATED_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)
    
        # Construct the response
    json_response = {
        "model_loss_image_url": MODEL_LOSS_URL,
        "lstm_generated_image_url": LSTM_GENERATED_URL,
        "all_pulls_data_image": ALL_PULLS_DATA_URL
    }
    
    return jsonify(json_response)

@app.route('/api/commits', methods=['POST'])
def commits():
    body = request.get_json()
    # Extracting the data from the request body
    commits_data = body["commits"]
    type = body["type"]
    repo_name = body["repo"]
    
    '''DATASET FOR COMMITS'''
    data_frame = pd.DataFrame(commits_data)
    df1 = data_frame.groupby(["created_at"], as_index=False).count()
    df = df1[["created_at", 'commit_number']]  # Assuming 'commit_number' is the column for commits
    df.columns = ['ds', 'y']

    df['ds'] = df['ds'].astype('datetime64[ns]')
    array = df.to_numpy()
    x = np.array([time.mktime(i[0].timetuple()) for i in array])
    y = np.array([i[1] for i in array])

    Y = df['y'].values
    firstDay = df['ds'].min()
    Ys = [0] * ((max(df['ds']) - firstDay).days + 1)
    days = pd.Series([firstDay + timedelta(days=i) for i in range(len(Ys))])
    for x, y in zip(df['ds'], Y):
        Ys[(x - firstDay).days] = y
    Ys = np.array(Ys)
    Ys = Ys.astype('float32')
    Ys = np.reshape(Ys, (-1, 1))
    # Apply min max scaler to transform the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    Ys = scaler.fit_transform(Ys)
    # Divide training - test data with 80-20 split
    train_size = int(len(Ys) * 0.80)
    test_size = len(Ys) - train_size
    train, test = Ys[0:train_size, :], Ys[train_size:len(Ys), :]
    print('train size for commits:', len(train), ", test size for commits:", len(test))

    # Create the training and test dataset
    def create_dataset(dataset, look_back=1):
        X, Y = [], []
        for i in range(len(dataset)-look_back-1):
            a = dataset[i:(i+look_back), 0]
            X.append(a)
            Y.append(dataset[i + look_back, 0])
        return np.array(X), np.array(Y)
    '''
    Look back decides how many days of data the model looks at for prediction
    Here LSTM looks at approximately one month data
    '''
     
    # Look back decides how many days of data the model looks at for prediction
    look_back = min(30, len(test) - 2)
    print(len(test))

    # Assuming create_dataset is a function that formats the data for LSTM
    if len(test) > look_back + 1:
        X_test, Y_test = create_dataset(test, look_back)
    else:
        print("Test dataset is too small for the specified look_back period.")
    X_train, Y_train = create_dataset(train, look_back)
    
    # Additional check: Ensure that X_test and X_train are not empty
    if len(X_train) == 0:
        print("X_train is empty. Check the train dataset and look_back parameter.")
    if len(X_test) == 0:
        print("X_test is empty. Check the test dataset and look_back parameter.")

    # Add a check to avoid reshaping if the dataset is empty
    if len(X_train) > 0:
        X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    if len(X_test) > 0:
        X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    # Verifying the shapes
    print('Shapes:', X_train.shape, X_test.shape, Y_train.shape, Y_test.shape)

    # Model to forecast
    model = Sequential()
    model.add(LSTM(100, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Fit the model with training data and set appropriate hyper parameters
    history = model.fit(X_train, Y_train, epochs=20, batch_size=70, validation_data=(X_test, Y_test),
                        callbacks=[EarlyStopping(monitor='val_loss', patience=10)], verbose=1, shuffle=False)

    '''
    Creating image URL
    BASE_IMAGE_PATH refers to Google Cloud Storage Bucket URL.Add your Base Image Path in line 145
    if you want to run the application locally
    LOCAL_IMAGE_PATH refers local directory where the figures generated by matplotlib are stored
    These locally stored images will then be uploaded to Google Cloud Storage
    '''
    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')
    # DO NOT DELETE "static/images" FOLDER as it is used to store figures/images generated by matplotlib
    LOCAL_IMAGE_PATH = "static/images/"

    # Creating the image path for model loss, LSTM generated image, and all commits data image
    MODEL_LOSS_IMAGE_NAME = "model_loss_" + type + "_" + repo_name + ".png"
    MODEL_LOSS_URL = BASE_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME

    LSTM_GENERATED_IMAGE_NAME = "lstm_generated_data_" + type + "_" + repo_name + ".png"
    LSTM_GENERATED_URL = BASE_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME

    ALL_COMMITS_DATA_IMAGE_NAME = "all_commits_data_" + type + "_" + repo_name + ".png"
    ALL_COMMITS_DATA_URL = BASE_IMAGE_PATH + ALL_COMMITS_DATA_IMAGE_NAME

    # Add your unique Bucket Name if you want to run it locally
    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')
    
    # Plot the model loss image
    plt.figure(figsize=(8, 4))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Test Loss')
    plt.title('Model Loss For ' + type)
    plt.ylabel('Loss')
    plt.xlabel('Epochs')
    plt.legend(loc='upper right')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)

    # Predict commits for test data
    y_pred = model.predict(X_test)

    # Plot the LSTM Generated image
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(np.arange(0, len(Y_train)), Y_train, 'g', label="history")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             Y_test, marker='.', label="true")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             y_pred, 'r', label="prediction")
    axs.legend()
    axs.set_title('LSTM Generated Data For ' + type)
    axs.set_xlabel('Time Steps')
    axs.set_ylabel('Commits')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)

    # Plot the All commits data images
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(X, Ys, 'purple', marker='.')
    locator = mdates.AutoDateLocator()
    axs.xaxis.set_major_locator(locator)
    axs.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    axs.legend()
    axs.set_title('All Commits Data')
    axs.set_xlabel('Date')
    axs.set_ylabel('Commits')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + ALL_COMMITS_DATA_IMAGE_NAME)
    
    # Uploads the images into the Google Cloud storage bucket
    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(MODEL_LOSS_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)
    new_blob = bucket.blob(ALL_COMMITS_DATA_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + ALL_COMMITS_DATA_IMAGE_NAME)
    new_blob = bucket.blob(LSTM_GENERATED_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)
    
    # Construct the response
    json_response = {
        "model_loss_image_url": MODEL_LOSS_URL,
        "lstm_generated_image_url": LSTM_GENERATED_URL,
        "all_commits_data_image": ALL_COMMITS_DATA_URL
    }
    
    return jsonify(json_response)

'''COMMITS IMPLEMENTATION OVER'''

# '''BRANCHES IMPLEMENTATION'''
# @app.route('/api/branches', methods=['POST'])
# def branches():
#     body = request.get_json()
#     # Extracting the data from the request body
#     branches_data = body["branches"]
#     type = body["type"]
#     repo_name = body["repo"]
    
#     '''DATASET FOR BRANCHES'''
#     data_frame = pd.DataFrame(branches_data)
#     df1 = data_frame.groupby(["created_at"], as_index=False).count()
#     df = df1[["created_at", 'branch_number']]  # Assuming 'branch_number' is the column for branches
#     df.columns = ['ds', 'y']

#     df['ds'] = df['ds'].astype('datetime64[ns]')
#     array = df.to_numpy()
#     x = np.array([time.mktime(i[0].timetuple()) for i in array])
#     y = np.array([i[1] for i in array])

#     Y = df['y'].values
#     firstDay = df['ds'].min()
#     Ys = [0] * ((max(df['ds']) - firstDay).days + 1)
#     days = pd.Series([firstDay + timedelta(days=i) for i in range(len(Ys))])
#     for x, y in zip(df['ds'], Y):
#         Ys[(x - firstDay).days] = y
#     Ys = np.array(Ys)
#     Ys = Ys.astype('float32')
#     Ys = np.reshape(Ys, (-1, 1))

#     # Apply min max scaler to transform the data
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     Ys = scaler.fit_transform(Ys)

#     # Divide training - test data with 80-20 split
#     train_size = int(len(Ys) * 0.80)
#     test_size = len(Ys) - train_size
#     train, test = Ys[0:train_size, :], Ys[train_size:len(Ys), :]
#     print('train size for branches:', len(train), ", test size for branches:", len(test))

#     # Create the training and test dataset
#     def create_dataset(dataset, look_back=1):
#         X, Y = [], []
#         for i in range(len(dataset)-look_back-1):
#             a = dataset[i:(i+look_back), 0]
#             X.append(a)
#             Y.append(dataset[i + look_back, 0])
#         return np.array(X), np.array(Y)

#     '''
#     Look back decides how many days of data the model looks at for prediction
#     Here LSTM looks at approximately one month data
#     '''
     
#     # Look back decides how many days of data the model looks at for prediction
#     look_back = min(30, len(test) - 2)
#     print(len(test))

#     # Assuming create_dataset is a function that formats the data for LSTM
#     if len(test) > look_back + 1:
#         X_test, Y_test = create_dataset(test, look_back)
#     else:
#         print("Test dataset is too small for the specified look_back period.")
#     X_train, Y_train = create_dataset(train, look_back)
    
#     # Additional check: Ensure that X_test and X_train are not empty
#     if len(X_train) == 0:
#         print("X_train is empty. Check the train dataset and look_back parameter.")
#     if len(X_test) == 0:
#         print("X_test is empty. Check the test dataset and look_back parameter.")

#     # Add a check to avoid reshaping if the dataset is empty
#     if len(X_train) > 0:
#         X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
#     if len(X_test) > 0:
#         X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

#     # Verifying the shapes
#     print('Shapes:', X_train.shape, X_test.shape, Y_train.shape, Y_test.shape)

#     # Model to forecast
#     model = Sequential()
#     model.add(LSTM(100, input_shape=(X_train.shape[1], X_train.shape[2])))
#     model.add(Dropout(0.2))
#     model.add(Dense(1))
#     model.compile(loss='mean_squared_error', optimizer='adam')

#     # Fit the model with training data and set appropriate hyper parameters
#     history = model.fit(X_train, Y_train, epochs=20, batch_size=70, validation_data=(X_test, Y_test),
#                         callbacks=[EarlyStopping(monitor='val_loss', patience=10)], verbose=1, shuffle=False)

#     '''
#     Creating image URL
#     BASE_IMAGE_PATH refers to Google Cloud Storage Bucket URL. Add your Base Image Path in line 145
#     if you want to run the application locally
#     LOCAL_IMAGE_PATH refers to the local directory where the figures generated by matplotlib are stored
#     These locally stored images will then be uploaded to Google Cloud Storage
#     '''
#     BASE_IMAGE_PATH = os.environ.get(
#         'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')
#     LOCAL_IMAGE_PATH = "static/images/"

#     # Creating the image path for model loss, LSTM generated image, and all branches data image
#     MODEL_LOSS_IMAGE_NAME = "model_loss_" + type + "_" + repo_name + ".png"
#     MODEL_LOSS_URL = BASE_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME

#     LSTM_GENERATED_IMAGE_NAME = "lstm_generated_data_" + type + "_" + repo_name + ".png"
#     LSTM_GENERATED_URL = BASE_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME

#     ALL_BRANCHES_DATA_IMAGE_NAME = "all_branches_data_" + type + "_" + repo_name + ".png"
#     ALL_BRANCHES_DATA_URL = BASE_IMAGE_PATH + ALL_BRANCHES_DATA_IMAGE_NAME

#     BUCKET_NAME = os.environ.get(
#         'BUCKET_NAME', 'lstm-bucket-a20543213')
    
#     # Plot the model loss image
#     plt.figure(figsize=(8, 4))
#     plt.plot(history.history['loss'], label='Train Loss')
#     plt.plot(history.history['val_loss'], label='Test Loss')
#     plt.title('Model Loss For ' + type)
#     plt.ylabel('Loss')
#     plt.xlabel('Epochs')
#     plt.legend(loc='upper right')
#     plt.savefig(LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)

#     # Predict branches for test data
#     y_pred = model.predict(X_test)

#     # Plot the LSTM Generated image
#     fig, axs = plt.subplots(1, 1, figsize=(10, 4))
#     X = mdates.date2num(days)
#     axs.plot(np.arange(0, len(Y_train)), Y_train, 'g', label="history")
#     axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
#              Y_test, marker='.', label="true")
#     axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
#              y_pred, 'r', label="prediction")
#     axs.legend()
#     axs.set_title('LSTM Generated Data For ' + type)
#     axs.set_xlabel('Time Steps')
#     axs.set_ylabel('Branches')
#     plt.savefig(LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)

#     # Plot the All branches data images
#     fig, axs = plt.subplots(1, 1, figsize=(10, 4))
#     X = mdates.date2num(days)
#     axs.plot(X, Ys, 'purple', marker='.')
#     locator = mdates.AutoDateLocator()
#     axs.xaxis.set_major_locator(locator)
#     axs.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
#     axs.legend()
#     axs.set_title('All Branches Data')
#     axs.set_xlabel('Date')
#     axs.set_ylabel('Branches')
#     plt.savefig(LOCAL_IMAGE_PATH + ALL_BRANCHES_DATA_IMAGE_NAME)
    
#     # Uploads the images into the Google Cloud storage bucket
#     bucket = client.get_bucket(BUCKET_NAME)
#     new_blob = bucket.blob(MODEL_LOSS_IMAGE_NAME)
#     new_blob.upload_from_filename(
#         filename=LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)
#     new_blob = bucket.blob(ALL_BRANCHES_DATA_IMAGE_NAME)
#     new_blob.upload_from_filename(
#         filename=LOCAL_IMAGE_PATH + ALL_BRANCHES_DATA_IMAGE_NAME)
#     new_blob = bucket.blob(LSTM_GENERATED_IMAGE_NAME)
#     new_blob.upload_from_filename(
#         filename=LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)
    
#     # Construct the response
#     json_response = {
#         "model_loss_image_url": MODEL_LOSS_URL,
#         "lstm_generated_image_url": LSTM_GENERATED_URL,
#         "all_branches_data_image": ALL_BRANCHES_DATA_URL
#     }
    
#     return jsonify(json_response)
# '''BRANCHES IMLEMENTATION OVER'''

'''
API route path is  "/api/forecast"
This API will accept only POST request
'''
@app.route('/api/forecast', methods=['POST'])
def forecast():
    body = request.get_json()
    # print(body)
    issues = body["issues"]
    # pulls = body["pulls"]
    type = body["type"]
    repo_name = body["repo"]
    
    '''DATASET FOR ISSUES'''
    data_frame = pd.DataFrame(issues)
    df1 = data_frame.groupby([type], as_index=False).count()
    df = df1[[type, 'issue_number']]
    df.columns = ['ds', 'y']

    df['ds'] = df['ds'].astype('datetime64[ns]')
    array = df.to_numpy()
    x = np.array([time.mktime(i[0].timetuple()) for i in array])
    y = np.array([i[1] for i in array])

    Y = df['y'].values
    firstDay = df['ds'].min()
    '''
    To achieve data consistancy with both actual data and predicted values, 
    add zeros to dates that do not have orders
    [firstDay + timedelta(days=day) for day in range((max(X) - firstDay).days + 1)]
    '''
    Ys = [0] * ((max(df['ds']) - firstDay).days + 1)
    days = pd.Series([firstDay + timedelta(days=i) for i in range(len(Ys))])
    for x, y in zip(df['ds'], Y):
        Ys[(x - firstDay).days] = y
    
    Ys = np.array(Ys)
    Ys = Ys.astype('float32')
    Ys = np.reshape(Ys, (-1, 1))
    # Apply min max scaler to transform the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    Ys = scaler.fit_transform(Ys)
    # Divide training - test data with 80-20 split
    train_size = int(len(Ys) * 0.80)
    test_size = len(Ys) - train_size
    train, test = Ys[0:train_size, :], Ys[train_size:len(Ys), :]
    print('train size for issues:', len(train), ", test size for issues:", len(test))

    
    # Create the training and test dataset
    def create_dataset(dataset, look_back=1):
        X, Y = [], []
        for i in range(len(dataset)-look_back-1):
            a = dataset[i:(i+look_back), 0]
            X.append(a)
            Y.append(dataset[i + look_back, 0])
        return np.array(X), np.array(Y)
    '''
    Look back decides how many days of data the model looks at for prediction
    Here LSTM looks at approximately one month data
    '''
    look_back = 30
    X_train, Y_train = create_dataset(train, look_back)
    X_test, Y_test = create_dataset(test, look_back)

    # Reshape input to be [samples, time steps, features]
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    # Verifying the shapes
    X_train.shape, X_test.shape, Y_train.shape, Y_test.shape

    # Model to forecast
    model = Sequential()
    model.add(LSTM(100, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # Fit the model with training data and set appropriate hyper parameters
    history = model.fit(X_train, Y_train, epochs=20, batch_size=70, validation_data=(X_test, Y_test),
                        callbacks=[EarlyStopping(monitor='val_loss', patience=10)], verbose=1, shuffle=False)

    '''
    Creating image URL
    BASE_IMAGE_PATH refers to Google Cloud Storage Bucket URL.Add your Base Image Path in line 145
    if you want to run the application local
    LOCAL_IMAGE_PATH refers local directory where the figures generated by matplotlib are stored
    These locally stored images will then be uploaded to Google Cloud Storage
    '''
    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')
    # DO NOT DELETE "static/images" FOLDER as it is used to store figures/images generated by matplotlib
    LOCAL_IMAGE_PATH = "static/images/"

    # Creating the image path for model loss, LSTM generated image and all issues data image
    MODEL_LOSS_IMAGE_NAME = "model_loss_" + type +"_"+ repo_name + ".png"
    MODEL_LOSS_URL = BASE_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME

    LSTM_GENERATED_IMAGE_NAME = "lstm_generated_data_" + type +"_" + repo_name + ".png"
    LSTM_GENERATED_URL = BASE_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME

    ALL_ISSUES_DATA_IMAGE_NAME = "all_issues_data_" + type + "_"+ repo_name + ".png"
    ALL_ISSUES_DATA_URL = BASE_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME

    DAY_OF_WEEK_ISSUES_NAME = "day_of_week_issues_"+ repo_name + ".png"
    DAY_OF_WEEK_ISSUES_URL = BASE_IMAGE_PATH + DAY_OF_WEEK_ISSUES_NAME
    
    DAY_OF_WEEK_ISSUES_CLOSED_NAME = "day_of_week_issues_closed_"+ repo_name + ".png"
    DAY_OF_WEEK_ISSUES_CLOSED_URL = BASE_IMAGE_PATH + DAY_OF_WEEK_ISSUES_CLOSED_NAME
    
    MONTH_ISSUE_CLOSED_NAME = "month_issues_closed_"+ repo_name + ".png"
    MONTH_ISSUE_CLOSED_URL = BASE_IMAGE_PATH + MONTH_ISSUE_CLOSED_NAME
    


    # Add your unique Bucket Name if you want to run it local
    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')

    # Model summary()

    # Plot the model loss image
    plt.figure(figsize=(8, 4))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Test Loss')
    plt.title('Model Loss For ' + type)
    plt.ylabel('Loss')
    plt.xlabel('Epochs')
    plt.legend(loc='upper right')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)

    # Predict issues for test data
    y_pred = model.predict(X_test)

    # Plot the LSTM Generated image
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(np.arange(0, len(Y_train)), Y_train, 'g', label="history")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             Y_test, marker='.', label="true")
    axs.plot(np.arange(len(Y_train), len(Y_train) + len(Y_test)),
             y_pred, 'r', label="prediction")
    axs.legend()
    axs.set_title('LSTM Generated Data For ' + type)
    axs.set_xlabel('Time Steps')
    axs.set_ylabel('Issues')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)

    # Plot the All Issues data images
    fig, axs = plt.subplots(1, 1, figsize=(10, 4))
    X = mdates.date2num(days)
    axs.plot(X, Ys, 'purple', marker='.')
    locator = mdates.AutoDateLocator()
    axs.xaxis.set_major_locator(locator)
    axs.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    axs.legend()
    axs.set_title('All Issues Data')
    axs.set_xlabel('Date')
    axs.set_ylabel('Issues')
    # Save the figure in /static/images folder
    plt.savefig(LOCAL_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME)
    
    
    '''
    MAX ISSUES CREATED DAY OF WEEK
    '''
    data_frame = pd.DataFrame(issues)

    # Convert 'created_at' to datetime format
    data_frame['created_at'] = pd.to_datetime(data_frame['created_at'], errors='coerce')
    # Group by day of the week and count issues
    week_df = data_frame.groupby(data_frame['created_at'].dt.day_name()).size()
    week_df = pd.DataFrame({'Created_On': week_df.index, 'Count': week_df.values})
    # ReinZ to make sure the days appear in the correct order
    week_df = week_df.groupby(['Created_On']).sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    # Get the day with maximum issues
    max_issue_count = week_df['Count'].max()
    max_issue_day = week_df['Count'].idxmax()
    # Print max day and count for debugging
    # print(f"Day with max issues: {max_issue_day} ({max_issue_count} issues)")

    # Plot the issues count for each day of the week
    plt.figure(figsize=(12, 7))
    plt.plot(week_df['Count'], label='Issues', marker='o', color='b')
    plt.title(f'Number of Issues Created for Week Days - {repo_name}')
    plt.ylabel('Number of Issues')
    plt.xlabel('Week Days')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(LOCAL_IMAGE_PATH + DAY_OF_WEEK_ISSUES_NAME)


    '''
    MAX ISSUES CLOSED DAY OF WEEK 
    '''

    data_frame['closed_at'] = pd.to_datetime(data_frame['closed_at'], errors='coerce')
    # Plot for issues created on each day of the week (already implemented)
    # Group by the day of the week and count closed issues
    week_closed_df = data_frame.groupby(data_frame['closed_at'].dt.day_name()).size()
    week_closed_df = pd.DataFrame({'Closed_On': week_closed_df.index, 'Count': week_closed_df.values})
    # Reindex to make sure the days appear in the correct order
    week_closed_df = week_closed_df.groupby(['Closed_On']).sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    # Get the day with maximum closed issues
    max_closed_issue_count = week_closed_df['Count'].max()
    max_closed_issue_day = week_closed_df['Count'].idxmax()
    # print(f"Day with max closed issues: {max_closed_issue_day} ({max_closed_issue_count} issues)")

    # Plot the closed issues count for each day of the week
    plt.figure(figsize=(12, 7))
    plt.plot(week_closed_df['Count'], label='Closed Issues', marker='o', color='r')
    plt.title(f'Number of Issues Closed for Week Days - {repo_name}')
    plt.ylabel('Number of Issues')
    plt.xlabel('Week Days')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(LOCAL_IMAGE_PATH + DAY_OF_WEEK_ISSUES_CLOSED_NAME)




     # Now we handle the second part: Monthly Closed Issues
    # Group by month name and count closed issues
    month_closed_df = data_frame.groupby(data_frame['closed_at'].dt.month_name()).size()
    month_closed_df = pd.DataFrame({'Closed_Month': month_closed_df.index, 'Count': month_closed_df.values})
    # Reindex to ensure the months appear in the correct order
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month_closed_df = month_closed_df.groupby(['Closed_Month']).sum().reindex(month_order)
    # Get the month with maximum closed issues
    max_month_closed_issue_count = month_closed_df['Count'].max()
    max_month_closed_issue = month_closed_df['Count'].idxmax()
    # print(f"Month with max closed issues: {max_month_closed_issue} ({max_month_closed_issue_count} issues)")
    
    # Plot the closed issues count for each month
    plt.figure(figsize=(12, 7))
    plt.plot(month_closed_df['Count'], label='Closed Issues', marker='o', color='b')
    plt.title(f'Number of Issues Closed per Month - {repo_name}')
    plt.ylabel('Number of Issues')
    plt.xlabel('Month of the Year')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(LOCAL_IMAGE_PATH + MONTH_ISSUE_CLOSED_NAME)




    # Uploads an images into the google cloud storage bucket
    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(MODEL_LOSS_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + MODEL_LOSS_IMAGE_NAME)
    new_blob = bucket.blob(ALL_ISSUES_DATA_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + ALL_ISSUES_DATA_IMAGE_NAME)
    new_blob = bucket.blob(LSTM_GENERATED_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + LSTM_GENERATED_IMAGE_NAME)
    
    new_blob = bucket.blob(DAY_OF_WEEK_ISSUES_NAME)
    new_blob.upload_from_filename(filename = LOCAL_IMAGE_PATH + DAY_OF_WEEK_ISSUES_NAME)
    
    new_blob = bucket.blob(DAY_OF_WEEK_ISSUES_CLOSED_NAME)
    new_blob.upload_from_filename(filename = LOCAL_IMAGE_PATH + DAY_OF_WEEK_ISSUES_CLOSED_NAME)

    new_blob = bucket.blob(MONTH_ISSUE_CLOSED_NAME)
    new_blob.upload_from_filename(filename = LOCAL_IMAGE_PATH + MONTH_ISSUE_CLOSED_NAME)


    # Construct the response
    json_response = {
        "day_of_week_image_url": DAY_OF_WEEK_ISSUES_URL,
        "day_of_week_image_closed_url": DAY_OF_WEEK_ISSUES_CLOSED_URL,
        "month_issue_closed": MONTH_ISSUE_CLOSED_URL,
        "model_loss_image_url": MODEL_LOSS_URL,
        "lstm_generated_image_url": LSTM_GENERATED_URL,
        "all_issues_data_image": ALL_ISSUES_DATA_URL
    }
    # Returns image url back to flask microservice
    
    print(json_response)
    return jsonify(json_response)




'''STATS MODEL'''
@app.route('/api/statscreated', methods=['POST'])
def statmis():
    body = request.get_json()
    type = body["type"]
    repo_name = body["repo"]
    print("type",type)
    issues = body["issues"]

    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')

    # Add your unique Bucket Name if you want to run it local
    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')

    LOCAL_IMAGE_PATH = "static/images/"
    OBSERVATION_IMAGE_NAME = "stats_observation_" + type +"_"+ repo_name + ".png"
    OBSERVATION_IMAGE_URL = BASE_IMAGE_PATH + OBSERVATION_IMAGE_NAME

    FORECAST_IMAGE_NAME = "stats_forecast_" + type +"_" + repo_name + ".png"
    FORECAST_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_IMAGE_NAME

    df = pd.DataFrame(issues)
    df1 = df.groupby(['created_at'], as_index = False).count()
    dataFrame = df1[['created_at','issue_number']]
    dataFrame.columns = ['ds', 'y']
    dataFrame.set_index('y')
    period = len(dataFrame) // 2
    predict = sm.tsa.seasonal_decompose(dataFrame.index, period=period)
    figure = predict.plot()
    figure.set_size_inches(12,7)
    plt.title("Observations plot of created issues")
    
    #observation image
    figure.get_figure().savefig(LOCAL_IMAGE_PATH + OBSERVATION_IMAGE_NAME)               
    model = sm.tsa.ARIMA(dataFrame['y'].iloc[1:], order = (1, 0, 0))
    results = model.fit()
    dataFrame['forecast'] = results.fittedvalues
    fig = dataFrame[['y', 'forecast']].plot(figsize=(12,7))
    plt.title("Timeseries forecasting of created issues")
    
    #forecast image
    fig.get_figure().savefig(LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)                      

     # Uploads an images into the google cloud storage bucket
    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(OBSERVATION_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + OBSERVATION_IMAGE_NAME)

    new_blob = bucket.blob(FORECAST_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)

    # Construct the response
    json_response = {
        "stats_observation_url": OBSERVATION_IMAGE_URL,
        "stats_forecast_url": FORECAST_IMAGE_URL
    }
    # Returns image url back to flask microservice
    return jsonify(json_response)

@app.route('/api/statsclosed', methods=['POST'])
def statmisc():
    body = request.get_json()
    type = body["type"]
    repo_name = body["repo"]
    print("type",type)
    issues = body["issues"]

    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')

    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')
    
    LOCAL_IMAGE_PATH = "static/images/"
    OBSERVATION_IMAGE_NAME = "stats_observation_" + type +"_"+ repo_name + ".png"
    OBSERVATION_IMAGE_URL = BASE_IMAGE_PATH + OBSERVATION_IMAGE_NAME

    FORECAST_IMAGE_NAME = "stats_forecast_" + type +"_" + repo_name + ".png"
    FORECAST_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_IMAGE_NAME

    df = pd.DataFrame(issues)
    df1 = df.groupby(['closed_at'], as_index = False).count()
    dataFrame = df1[['closed_at','issue_number']]
    dataFrame.columns = ['ds', 'y']
    dataFrame.set_index('y')
    period = len(dataFrame) // 2
    predict = sm.tsa.seasonal_decompose(dataFrame.index, period=period)
    figure = predict.plot()
    figure.set_size_inches(12,7)
    plt.title("Observations plot of closed issues")
    

    figure.get_figure().savefig(LOCAL_IMAGE_PATH + OBSERVATION_IMAGE_NAME)               
    model = sm.tsa.ARIMA(dataFrame['y'].iloc[1:], order = (1, 0, 0))
    results = model.fit()
    dataFrame['forecast'] = results.fittedvalues
    fig = dataFrame[['y', 'forecast']].plot(figsize=(12,7))
    plt.title("Timeseries forecasting of closed issues")
    fig.get_figure().savefig(LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)


    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(OBSERVATION_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + OBSERVATION_IMAGE_NAME)

    new_blob = bucket.blob(FORECAST_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)

    json_response = {
        "stats_observation_url": OBSERVATION_IMAGE_URL,
        "stats_forecast_url": FORECAST_IMAGE_URL
    }

    return jsonify(json_response)

@app.route('/api/statspull', methods=['POST'])
def statmpull():
    body = request.get_json()
    pull_req_response = body["pulls"]
    repo_name = body["repo"]
    type = body["type"]
    
    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')

    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')

    LOCAL_IMAGE_PATH = "static/images/"
    OBSERVATION_IMAGE_NAME = "stats_observation_" + type +"_"+ repo_name + ".png"
    OBSERVATION_IMAGE_URL = BASE_IMAGE_PATH + OBSERVATION_IMAGE_NAME

    FORECAST_IMAGE_NAME = "stats_forecast_" + type +"_" + repo_name + ".png"
    FORECAST_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_IMAGE_NAME

    df = pd.DataFrame(pull_req_response)
    df1 = df.groupby(['created_at'], as_index = False).count()
    dataFrame = df1[['created_at','pull_req_number']]
    dataFrame.columns = ['ds', 'y']
    dataFrame.set_index('y')
    period = len(dataFrame) // 2
    predict = sm.tsa.seasonal_decompose(dataFrame.index, period=period)
    figure = predict.plot()
    figure.set_size_inches(12,7)
    plt.title("Observations plot of pull requests")
    

    figure.get_figure().savefig(LOCAL_IMAGE_PATH + OBSERVATION_IMAGE_NAME)               
    model = sm.tsa.ARIMA(dataFrame['y'].iloc[1:], order = (1, 0, 0))
    results = model.fit()
    dataFrame['forecast'] = results.fittedvalues
    fig = dataFrame[['y', 'forecast']].plot(figsize=(12,7))
    plt.title("Timeseries forecasting of pull requests")
    fig.get_figure().savefig(LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)
    

    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(OBSERVATION_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + OBSERVATION_IMAGE_NAME)

    new_blob = bucket.blob(FORECAST_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)

    json_response = {
        "stats_observation_url": OBSERVATION_IMAGE_URL,
        "stats_forecast_url": FORECAST_IMAGE_URL
    }

    return jsonify(json_response)

@app.route('/api/statscommits', methods=['POST'])
def statmcommits():
    body = request.get_json()
    commit_response = body["commits"]
    repo_name = body["repo"]
    type = body["type"]
    print("type:",type)

    BASE_IMAGE_PATH = os.environ.get(
        'BASE_IMAGE_PATH', 'https://storage.googleapis.com/lstm-bucket-a20543213/')


    BUCKET_NAME = os.environ.get(
        'BUCKET_NAME', 'lstm-bucket-a20543213')
    
    LOCAL_IMAGE_PATH = "static/images/"
    OBSERVATION_IMAGE_NAME = "stats_observation_" + type +"_"+ repo_name + ".png"
    OBSERVATION_IMAGE_URL = BASE_IMAGE_PATH + OBSERVATION_IMAGE_NAME

    FORECAST_IMAGE_NAME = "stats_forecast_" + type +"_" + repo_name + ".png"
    FORECAST_IMAGE_URL = BASE_IMAGE_PATH + FORECAST_IMAGE_NAME

    df = pd.DataFrame(commit_response)
    df1 = df.groupby(['created_at'], as_index = False).count()
    dataFrame = df1[['created_at','commit_number']]
    dataFrame.columns = ['ds', 'y']
    print(dataFrame)
    dataFrame.set_index('y')
    period = len(dataFrame) // 2
    predict = sm.tsa.seasonal_decompose(dataFrame.index, period=period)
    figure = predict.plot()
    figure.set_size_inches(12,7)
    plt.title("Observations plot of commits")
    

    figure.get_figure().savefig(LOCAL_IMAGE_PATH + OBSERVATION_IMAGE_NAME)               
    model = sm.tsa.ARIMA(dataFrame['y'].iloc[1:], order = (1, 0, 0))
    results = model.fit()
    dataFrame['forecast'] = results.fittedvalues
    fig = dataFrame[['y', 'forecast']].plot(figsize=(12,7))
    plt.title("Timeseries forecasting of commits")
    fig.get_figure().savefig(LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)


    bucket = client.get_bucket(BUCKET_NAME)
    new_blob = bucket.blob(OBSERVATION_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + OBSERVATION_IMAGE_NAME)

    new_blob = bucket.blob(FORECAST_IMAGE_NAME)
    new_blob.upload_from_filename(
        filename=LOCAL_IMAGE_PATH + FORECAST_IMAGE_NAME)


    json_response = {
        "stats_observation_url": OBSERVATION_IMAGE_URL,
        "stats_forecast_url": FORECAST_IMAGE_URL
    }

    return jsonify(json_response)

'''STATS MODEL IMPLEMENTATION OVER'''




# Run LSTM app server on port 8080
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
