from flask import Flask, request, send_file, render_template
import os
import requests
import redis
import csv
import matplotlib.pyplot as plt
import numpy as np
import json
from jobs import rd, rd2, rd3, add_job

app = Flask(__name__)

@app.route('/test',methods=['GET'])
def test():
    return render_template('index.html')

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
      return json.dumps(add_job(job['start'], job['end'])) + '\n'

@app.route('/data', methods=['POST','GET','DELETE'])
def handle_data() -> list:
    """
    If methods is POST, loads the auto trends data set into redis and returns message
    If method is GET, returns data from redis
    If method is DELETE, clears the data in redis and returns message

    Args:
        N/A
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
        N/A
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
        N/A
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

@app.route('/co2_year_plot', methods=['GET', 'POST', 'DELETE'])
def image_func() -> bytes:
    """
    If method is POST, loads a simple plot of the auto trends data into redis and returns message
    If method is GET, returns image from redis
    If method is DELETE, clears the image in redis and returns message

    Args:
        N/A
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
                    if car['Model Year'].isdigit() and 1975 <= int(car['Model Year']) <= 2021:
                        years.append(int(car['Model Year']))
                        co2.append(float(car['Real-World CO2 (g/mi)']))
            plt.scatter(years, co2)
            plt.title('Average Vehicle CO2 Emissions from 1975-2021')
            plt.ylabel('Real-World CO2 (g/mi)')
            plt.xlabel('Year')
            plt.savefig('./co2_graph.png')
            plt.clf()
            file_bytes = open('./co2_graph.png', 'rb').read()
            rd2.set('image0', file_bytes)
            return 'Auto Trends data image is loaded into Redis\n'
    elif request.method == 'GET':
        if b'image0' not in rd2.keys():
            return 'Image not found or has not been loaded yet\n'
        else:
            path = './getimage.png'
            with open(path, 'wb') as f:
                f.write(rd2.get('image0'))
            return send_file(path, mimetype='image/png', as_attachment=True)
    elif request.method == 'DELETE':
        if b'image0' not in rd2.keys():
            return 'Image not found or has not been loaded yet\n'
        else:
            rd2.delete('image0')
            return 'Auto Trends data image has been deleted from Redis\n'
    else:
        return 'The method you tried does not work\n'


@app.route('/weight_mpg_plot/<year>', methods=['GET', 'POST', 'DELETE'])
def disp_image(year: str) -> bytes:
    """
    This function downloads an image of a plot that compares a vehicles weight to its fuel efficiency from the year specified by the user
    
    Args:
        manufacturer (str): the string of a Manufacturer
        year (str): the string of the Model Year
    Returns:
        auto_img (bytes): (if method is GET) bytes object of the image for the data set
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
            years_list = get_years()
            if year not in years_list:
                return 'Invalid input, please choose a valid year from 1975 to 2021\n'
            for key in rd.keys():
                yr = rd.hget(key, 'Model Year')
                if yr.isdigit() and int(yr) == int(year):
                    mpg = rd.hget(key, 'Real-World MPG')
                    weight = rd.hget(key, 'Weight (lbs)')
                    if mpg != '-' and weight != '-':
                        mpg_list.append(float(mpg))
                        weight_list.append(float(weight))
            plt.scatter(weight_list, mpg_list)
            plt.title('Vehicle Weight vs Fuel Economy in ' + year)
            plt.xlabel('Weight (lbs)')
            plt.ylabel('Miles per Gallon')
            plt.savefig('./weight_mpg_plt_year.png')
            plt.clf()
            file_bytes = open('./weight_mpg_plt_year.png', 'rb').read()
            # set the file bytes as a key in Redis
            rd2.set('plotimage', file_bytes)
            return 'image has been loaded to redis\n'
    elif request.method == 'GET':
        # check if image is in database
        # if so, return image
        if rd2.exists('plotimage'):
            path='./weight_mpg_plt_year.png'
            with open(path,'wb') as f:
                f.write(rd2.get('plotimage'))
            return send_file(path, mimetype='image/png', as_attachment=True)
        else:
            return 'image is not in database\n'
    elif request.method == 'DELETE':
        # delete image from redis
        if rd2.exists('plotimage'):
            rd2.delete('plotimage')
            return 'image deleted\n'
        else:
            return 'database is empty, nothing to flush\n'

@app.route('/vehicleType_mpg_plot/<year>', methods=['POST','GET','DELETE'])
def showPlot(year: str) -> bytes:
    """
    If method is POST, loads a simple plot of the auto trends data into redis and returns message
    If method is GET, returns image from redis
    If method is DELETE, clears the image in redis and returns message

    Args:
        N/A
    Returns:
        auto_img (bytes): (if method is GET) bytes object of the image for the data set
    """
    years_list = get_years()
    if request.method == 'POST':
        if len(rd.keys()) == 0:
            return 'No data in db. Post data to get info\n'
        else:
            x = []
            y = []
            if year not in years_list:
                return 'Invalid input. Please enter a valid year from 1975 to 2021\n'
            for key in rd.keys():
                carDict = rd.hgetall(key)
                yr = carDict['Model Year']
                if carDict['Manufacturer'] == 'All' and yr.isdigit() and int(yr) == int(year):
                    mpg = carDict['Real-World MPG']
                    carType = carDict['Vehicle Type']
                    if mpg != '-':
                        x.append(carType)
                        y.append(float(mpg))
            plt.bar(x, y, color = 'g', width = 0.72, label = "MPG")
            plt.xlabel('Vehicle Type')
            plt.ylabel('MPG')
            plt.title(year + ': MPG vs Vehicle Type')
            plt.legend()
            plt.savefig('./2021_MPGvType.png')
            plt.clf()
            file_bytes = open('./2021_MPGvType.png', 'rb').read()
            # set the file bytes as a key in Redis
            rd2.set('plot', file_bytes)
            return 'Plot is loaded.\n'
    elif request.method == 'GET':
        if rd2.exists('plot'):
            path = './2021_MPGvType.png'
            with open(path, 'wb') as f:
                f.write(rd2.get('plot'))
            return send_file(path, mimetype='image/png', as_attachment=True)
        else:
            return 'Plot not found\n'
    elif request.method == 'DELETE':
        if rd2.exists('plot'):
            rd2.delete('plot')
            return 'Plot has been deleted\n'
        else:
            return 'The method you tried does not work. DB already empty\n'

@app.route('/download/<jobid>', methods=['GET'])
def download(jobid: str) -> bytes:
    """
    This function downloads an image that was generated by the worker from Redis given the job ID

    Args:
        jobid (str): pseudo-random identifier for a job
    Returns:
        auto_img (bytes): (if method is GET) bytes object of the image for the data set
    """
    if rd3.exists('job.'+jobid) and b'image' in rd3.hgetall('job.'+jobid):
        path = './{jobid}.png'
        with open(path, 'wb') as f:
            f.write(rd3.hget('job.'+jobid, b'image'))
        return send_file(path, mimetype='image/png', as_attachment=True)
    else:
        return 'CO2 Emissions by Vehicle Type is not loaded in redis yet\n'

@app.route('/status/<jobid>', methods=['GET'])
def status(jobid: str) -> str:
    """
    This function returns the job status given the job ID

    Args:
        jobid (str): pseudo-random identifier for a job
    Returns:
        status (if method is GET): the status of the specific job
    """
    if rd3.exists('job.'+jobid):
        return 'Status: ' + rd3.hget('job.'+jobid, b'status').decode() + '\n'
    else:
        return 'Invalid job id, job does not exist in the database\n'

@app.route('/help', methods=['GET'])
def get_help():
    """
    Returns all the available routes to the user
    
    Args: 
        N/A
    Returns:
        help_user (str): String of all the available routes to curl
    """
    help_user = """Try the following routes: 
            /help returns all the routes and their purpose
            /data 
                -X GET returns the entire data set (hundreds of dictionaries)
                -X POST adds the data to the redis database
                -X DELETE deletes all the data from the redis database
            /years
                returns a list of all the years recorded in the dataset
            /years/<year>
                returns a list of all the data from the specified year
            /manufacturers
                returns a list of the manufacturers currently in redis for the Auto Trends Database
            /manufacturers/<manufacturer>
                returns a list with all cars from that manufacturer if found in the Auto Trends database
            /manufacturer/<manufacturer>/years
                returns a list of the years where there is data for a specific manufacturer
            /manufacturer/<manufacturer>/years/<year>
                returns a list for the data for the specified manufacturer and year if found in the Auto Trends database route
            /co2_year_plot
                -X POST loads a plot of the total co2 emissions for a user specified range of years
                -X GET  <some location>:<port> /co2_year_plot --output output.png returns a plot of total co2 emissions for a range of years to redis data base
                -X DELETE deletes the image from the redis data base
            /weight_mpg_plot/<year>
                -X POST loads a plot of the weight vs fuel economy of every vehicle for a user specified year
                -X GET <some location>:<port> /weight_mpg_plot/<year> --output output.png returns a plot of weight vs fuel economy to redis data base
                -X DELETE deletes the image from the redis data base
            /vehicleType_mpg_plot/<year>
                -X POST loads a plot of the weight vs fuel economy of every vehicle for a user specified year
                -X GET <some location>:<port>/vehicleType_mpg_plot/ <year> --output output.png returns a plot of weight vs fuel economy to redis data base
                -X DELETE deletes the image from the redis data base
            /download/<jobid>
                downloads an image that was generated by the worker from Redis given the job ID
            /jobs
                API route for creating a new job to do analysis. This route accepts a JSON payload describing the job to be created
            /status/<jobid>
                returns the status of the specified job id\n"""
    return help_user

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
