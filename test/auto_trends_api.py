from flask import Flask, request, send_file
import os
import requests
import redis
import csv
import matplotlib.pyplot as plt
import numpy as np
import jobs

rd = redis.StrictRedis(host = redis_ip, port = 6379, db = 0, decode_responses = True)
rd2 = redis.StrictRedis(host = redis_ip, port = 6379, db = 1)
q = HotQueue("queue", host = redis_ip, port = 6379, db = 2)

app = Flask(__name__)

@app.route('/jobs', methods=['POST'])
def jobs_api():
      """
      API route for creating a new job to do some analysis. This route accepts a JSON payload
      describing the job to be created.
      """
      try:
          job = request.get_json(force=True)
      except Exception as e:
          return True, json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
      return json.dumps(jobs.add_job(job['start'], job['end']))

@app.route('/data', methods=['POST','GET','DELETE'])
def handle_data() -> list:
    """
    If methods is POST, loads the auto trends data set into redis and returns message
    If method is GET, returns data from redis
    If method is DELETE, clears the data in redis and returns message

    Args:
        no arguments

    Returns:
        auto_data (list): (if method is GET) list of dictionaries of the cars data in redis
    """
    if request.method == 'POST':
        with open('auto_trends_data.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = dict(row)
                key = item['Manufacturer'] + '-' + item['Model Year'] + '-' + item['Vehicle Type']
                rd.hset(key, mapping = item)
        return 'Auto Trends data is loaded into Redis\n'
    elif request.method == 'GET':
        auto_data = []
        for key in rd.keys():
            auto_data.append(rd.hgetall(key))
        return auto_data
    elif request.method == 'DELETE':
        rd.flushdb()
        return 'Auto Trends data has been deleted from Redis\n'
    else:
        return 'The method you tried does not work\n'

@app.route('/years', methods=['GET'])
def get_years() -> list:
    """
    Returns a list of the years currently in redis for the Auto Trends database for the '/years' route
    
    Args:
        no arguments
    
    Returns:
        years_list (list): list of strings of the Model Year
    """
    years_list = []
    for key in rd.keys():
        car_dict = rd.hgetall(key)
        if car_dict['Model Year'] not in years_list:
            years_list.append(car_dict['Model Year'])
    return years_list

@app.route('/years/<year>', methods=['GET'])
def get_year_info(year: str) -> list:
    """
    Returns a list with all cars from that year if found in the Auto Trends database for the '/years/<year>' route

    Args:
        year (str): the string of a Model Year

    Returns:
        year_cars (list): list with cars from the specified year, if year not found, will be empty list
    """
    year_cars = []
    if year in get_years():
        for key in rd.keys():
            car_dict = rd.hgetall(key)
            if car_dict['Model Year'] == year:
                year_cars.append(car_dict)
    return year_cars

@app.route('/manufacturers', methods=['GET'])
def get_manufacturers() -> list:
    """
    Returns a list of the manufacturers currently in redis for the Auto Trends database for the '/manufacturers' route

    Args:
        no arguments

    Returns:
        manufacturers_list (list): list of strings of the Manufacturer
    """
    manufacturers_list = []
    for key in rd.keys():
        car_dict = rd.hgetall(key)
        if car_dict['Manufacturer'] not in manufacturers_list:
            manufacturers_list.append(car_dict['Manufacturer'])
    return manufacturers_list

@app.route('/manufacturers/<manufacturer>', methods=['GET'])
def get_manufacturer_info(manufacturer: str) -> list:
    """
    Returns a list with all cars from that manufacturer if found in the Auto Trends database for the '/manufacturers/<manufacturer>' route

    Args:
        manufacturer (str): the string of a Manufacturer

    Returns:
        manufacturer_cars (list): list with cars from the specified manufacturer, if manufacturer not found, will be empty list
    """
    manufacturer_cars = []
    if manufacturer in get_manufacturers():
        for key in rd.keys():
            car_dict = rd.hgetall(key)
            if car_dict['Manufacturer'] == manufacturer:
                manufacturer_cars.append(car_dict)
    return manufacturer_cars

@app.route('/manufacturers/<manufacturer>/years', methods=['GET'])
def manu_years(manufacturer: str) -> list:
    """
    Returns a list of the years where there is data for a specific manufacturer if found in the Auto Trends database for the '/manufacturers/<manufacturer>/years' route

    Args:
        manufacturer (str): the string of a Manufacturer

    Returns:
        years_list (list): list with years from the specified manufacturer, if manufacturer not found, will be empty list
    """
    years_list = []
    cars_list = get_manufacturer_info(manufacturer)
    for car in cars_list:
        if car['Model Year'] not in years_list:
            years_list.append(car['Model Year'])
    return years_list

@app.route('/manufacturers/<manufacturer>/years/<year>', methods=['GET'])
def manu_years_data(manufacturer: str, year: str) -> list:
    """
    Returns a list for the data for the specified manufacturer and year if found in the Auto Trends database for the '/manufacturers/<manufacturer>/years/<year>' route

    Args:
        manufacturer (str): the string of a Manufacturer
        year (str): the string of the Model Year

    Returns:
        data_list (list): list with data for the year from the specified manufacturer, if manufacturer or year not found, will be empty list
    """
    data_list = []
    cars_list = get_manufacturer_info(manufacturer)
    for car in cars_list:
        if car['Model Year'] == year:
            data_list.append(car)
    return data_list

@app.route('/image', methods=['GET', 'POST', 'DELETE'])
def image_func() -> bytes:
    """
    If method is POST, loads a simple plot of the auto trends data into redis and returns message
    If method is GET, returns image from redis
    If method is DELETE, clears the image in redis and returns message

    Args:
        no arguments

    Returns:
        auto_img (bytes): (if method is GET) bytes object of the image for the data set
    """
    if request.method == 'POST':
        if len(rd.keys()) == 0:
            return 'Auto Trends data not loaded in Redis yet\n'
        else:
            cars_list = get_manufacturer_info('All')
            years = []
            co2 = []
            for car in cars_list:
                if car['Vehicle Type'] == 'All':
                    if car['Model Year'].isdigit():
                        years.append(int(car['Model Year']))
                    else:
                        years.append(2022)
                    co2.append(float(car['Real-World CO2 (g/mi)']))
            plt.scatter(years, co2)
            plt.title('Average Vehicle CO2 Emissions from 1975-2022')
            plt.ylabel('Real-World CO2 (g/mi)')
            plt.xlabel('Year')
            plt.savefig('./co2_graph.png')
            plt.show()
            file_bytes = open('./co2_graph.png', 'rb').read()
            rd2.set('image', file_bytes)
            return 'Auto Trends data image is loaded into Redis\n'
    elif request.method == 'GET':
        if b'image' not in rd2.keys():
            return 'Image not found or has not been loaded yet\n'
        else:
            path = './getimage.png'
            with open(path, 'wb') as f:
                f.write(rd2.get('image'))
            return send_file(path, mimetype='image/png', as_attachment=True)
    elif request.method == 'DELETE':
        if b'image' not in rd2.keys():
            return 'Image not found or has not been loaded yet\n'
        else:
            rd2.delete('image')
            return 'Auto Trends data image has been deleted from Redis\n'
    else:
        return 'The method you tried does not work\n'


@app.route('/weight_mpg_plot', methods=['GET', 'POST', 'DELETE'])
def disp_image():
    """
    This function downloads an image of a plot that compares a vehicles weight to its fuel efficiency from the year 2021
    Args: there are no arguments
    Returns: send_file(path, mimetype='image/png', as_attachment=True) (png image): png image of plot downloaded to redis
    """
    if request.method == 'POST':
        mpg_list = []
        weight_list = []
        output_list = []
        for item in rd.keys():
            output_list.append(rd.hgetall(item))
        if output_list == []:
            return 'there is no data, cannot generate plot\n'
        else:
            for item in list_of_dict:
                key = f"{item['Manufacturer']}:{item['Model Year']}:{item['Vehicle Type']}"
                yr = rd.hget(key,'Model Year')
                if yr == '2021':
                    yr = float(yr)
                    mpg = rd.hget(key, 'Real-World MPG')
                    if mpg != '-':
                        mpg_list.append(float(mpg))
                        weight = rd.hget(key, 'Weight (lbs)')
                        weight_list.append(float(weight))
            plt.scatter(weight_list,mpg_list)
            plt.title('Vehicle Weight vs Fuel Economy in 2021')
            plt.xlabel('Weight (lbs)')
            plt.ylabel('Miles per Gallon')
            plt.savefig('./weight_mpg_plt_2021.png')
            file_bytes = open('./weight_mpg_plt_2021.png', 'rb').read()
            # set the file bytes as a key in Redis
            rd2.set('plotimage', file_bytes)
            return 'image has been loaded to redis\n'
    elif request.method == 'GET':
        # check if image is in database
        # if so, return image
        if rd2.exists('plotimage'):
            path='./weight_mpg_plt_2021.png'
            with open(path,'wb') as f:
                f.write(rd2.get('plotimage'))
            return send_file(path, mimetype='image/png', as_attachment=True)
        else:
            return 'image is not in database\n'
    elif request.method == 'DELETE':
        # delete image from redis
        if rd2.exists('plotimage'):
            rd2.flushdb()
            return 'image deleted\n'
        else:
            return 'database is empty, nothing to flush\n'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
