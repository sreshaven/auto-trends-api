# Auto Trends API

## Summary

The EPA, or the Environmental Protection Agency, is an executive agency of the US federal government that is tasked with environmental protection matters. One of their roles is to collect and analyze data related to environmental issues in order to help reduce risks to the environment based on the best available scientific information and to review the safety of parts of society. The EPA collects data about Automotive Trends in the United States to aid in their mission and investigate the effect of the automotive industry on the environment. The goal of this project is to create a Flask API that is containerized and injects the Auto Trends data set into a Redis database. The Flask API will have routes that help with getting access to information directly from the database.

## About the Auto Trends Data Set

The EPA and NHTSA (National Highway Traffic Safety Administration) collects data from directly car manufacturers annually about their vehicles. The database ([located here](https://www.epa.gov/automotive-trends/explore-automotive-trends-data#DetailedData)) has been maintained by the EPA since 1975 and has up to date data available for all model years since then, with preliminary data for 2022. In this data set, there is information about manufacturer and vehicle type, which are categorical values, and model year, production share, compliance and estimated real-world MPG, CO2 emissions, weight, horsepower, and many more, which are numerical values. The data is split into vehicle type categories of sedan/wagon, car SUV, truck SUV, minivan/van, and pickup and the data set also has average observations for all of the cars and all of the trucks. These values reflect arithmetic and harmonic production-weighted averages for each vehicle type. 

## Flask App

The Auto Trends Flask App, located in the `auto_trends_api.py`, helps with processing the Auto Trends data set and adding it into a Redis database so that the data is preserved beyond the lifetime of the application containers. The Flask App also allows the user to query the dataset based on year or manufacturer to get more specific data to help save time in investigating efforts since the data set is so large. The Flask App is also containerized using Docker to allow for more portablility annd easier access to users.

### Run Instructions

In order to run the Flask app and query through the dataset using routes, there are a few steps to the process:

1. Clone this repository to your local system using `git clone git@github.com:sreshaven/auto-trends-api.git` and change your current directory using `cd auto-trends-api/` 

2. Next, get the `auto_trends_api` image in order to start a container for the Flask App. There are two methods to do this:

_Method #1_: Pull the existing image from Docker Hub using the command: `docker pull sreshaven/auto_trends_api:final`

_Method #2_: Build the Docker image locally from the Dockerfile in the repository. To do this, first download the Auto Trends dataset located here: [https://www.epa.gov/automotive-trends/explore-automotive-trends-data#DetailedData](https://www.epa.gov/automotive-trends/explore-automotive-trends-data#DetailedData). Click on the blue button that says "Export Detailed Data by Manufacturer" (which is Table A-1 on the site) to download the file to your local system. Rename this file to `auto_trends_data.csv` and move this file to the homework08/ directory. In the homework08/ directory, use `docker build -t <username>/auto_trends_api:final .` and replace `<username>` with your username to build the image using the Dockerfile in the repository. In the docker-compose.yml file, change the line that says `image: sreshaven/auto_trends_api:final` by replacing `sreshaven` with your username.

3. Then, make a directory in the `auto-trends-api/` directory to which the Redis database can mount a volume to by using `mkdir data`.

4. Lastly, to start up the Flask app in detached mode using the Docker Compose file in the repository, run `docker-compose up -d`. 

Now, you can use the Flask app to inject the dataset into a Redis database and query the dataset using the routes and examples described in the section below.

### Run Instructions - Kubernetes

In order to deploy the Flask container to a Kubernetes cluster, follow the instructions below:

1. First clone this repository to your system that has access to the Kubernetes API for the cluster using `git clone git@github.com:sreshaven/auto-trends-api.git` and change your current directory using `cd auto-trends-api/` 

2. If you built your own Docker image locally following Method #2 in the "Run Instructions" steps above and to use this Docker image in a Kubernetes cluster, run `docker login` in the system that you built your Docker image on to login to your Docker Hub account and `docker push <username>/auto_trends_api:final` to push your built image to Docker Hub. Now in the svv346-test-flask-deployment.yml file in the repo, change the line that says `image: sreshaven/auto_trends_api:final` by replacing `sreshaven` with your username. 

3. To set up the PVC to save the Redis data from the Flask app, change directory to the kubernetes folder by running `cd kubernetes/` and run `kubectl apply -f svv346-test-redis-pvc.yml`.

4. Next, to create a deployment for the Redis database so that the desired state for Redis is always met, run `kubectl apply -f svv346-test-redis-deployment.yml`.

5. The last step for the Redis set up is to start the service so that there is a persistent IP address that you can use to talk to Redis. To do this, run `kubectl apply -f svv346-test-redis-service.yml`. Now to get the IP address for this service, run `kubectl get services` and copy the IP address for the redis service. Now in the `svv346-test-flask-deployment.yml` file, change the line that says `value: 10.233.15.94` by replacing `10.233.15.94` with the copied IP address for your service.

6. To set up the deployment for the Flask app on the Kubernetes cluster, run `kubectl apply -f svv346-test-flask-deployment.yml`.

7. Lastly, to get a persistent IP address for the Flask app with a service, run `kubectl apply -f svv346-test-flask-service.yml`. To use this IP address to run the Flask app routes, run `kubectl get services` and copy the IP address for the flask service. To use the Flask app routes, exec into a Python debug container and use the examples below to guide you. When running curl commands, replace `127.0.0.1` with the IP address for your Flask service.

### Routes and Examples

While the Flask app is running (in the background or in another terminal on the same machine) use these examples to guide you in querying through the dataset.

#### Route: /help
To see all of the possible route and a description of each, you can run the command `curl http://127.0.0.1:5000/help`. There are a total of 13 routes. 

#### Route: /data
Method = POST: Use this route and set the method to POST to inject the auto trends data set into the Redis database that has started up. To do this, run the command `curl -X POST http://127.0.0.1:5000/data` which will return a message like the one below:
```
Auto Trends data is loaded into Redis
```

Method = GET: By setting the method to GET, this route can also be used to get all of the data directly from the Redis database. To use this, run the command `curl -X GET http://127.0.0.1:5000/data` and below is an example of what the output looks like:
```
[
  {
    "2-Cycle MPG": "19.42850",
    "4 or Fewer Gears": "0.861",
    "5 Gears": "0.139",
    "6 Gears": "-",
    "7 Gears": "-",
    "8 Gears": "-",
    "9 or More Gears": "-",
    "Acceleration (0-60 time in seconds)": "15.5542",
    "Average Number of Gears": "3.5",
    "Cylinder Deactivation": "-",
    "Drivetrain - 4WD": "0.211",
    "Drivetrain - Front": "0.018",
    "Drivetrain - Rear": "0.771",
    "Engine Displacement": "235.7915",
    "Footprint (sq. ft.)": "-",
    "Fuel Delivery - Carbureted": "0.948",
    "Fuel Delivery - Gasoline Direct Injection (GDI)": "-",
    "Fuel Delivery - Other": "0.042",
    "Fuel Delivery - Port Fuel Injection": "-",
    "Fuel Delivery - Throttle Body Injection": "0.010",
    "HP/Engine Displacement": "0.548745",
    "HP/Weight (lbs)": "0.031546",
    "Horsepower (HP)": "118.0136",
    "Manufacturer": "All",
    "Model Year": "1980",
    "Multivalve Engine": "-",
    "Powertrain - Diesel": "0.042",
    "Powertrain - Electric Vehicle (EV)": "-",
...
```

Method = DELETE: You can also use this route to delete the data in the Redis database. Below is an example output for the command `curl -X DELETE http://127.0.0.1:5000/data`:
```
Auto Trends data has been deleted from Redis
```

#### Route: /years
To get a list of the model years in the Auto Trends data set, use `curl http://127.0.0.1:5000/years` and below is an example of what the output would look like:
```
[
  "1980",
  "2017",
  "1978",
  "1979",
  "1992",
  "1983",
  "2015",
  "2011",
  "2003",
  "1988",
  "1984",
  "1987",
  "2005",
  "1995",
  "2002",
  "1977",
  "2001",
  "2007",
  "1997",
  "1999",
  "1991",
  "2014",
  "1989",
  "1981",
  "2020",
  "1985",
...
```

#### Route: /years/\<year\>
To get all of the data points from a certain model year, run `curl http://127.0.0.1:5000/years/<year>` and replace \<year\> with a model year that you want to you. Below is an example of what `curl http://127.0.0.1:5000/years/2007` looks like:
```
[
  {
    "2-Cycle MPG": "20.33974",
    "4 or Fewer Gears": "0.979",
    "5 Gears": "0.018",
    "6 Gears": "0.004",
    "7 Gears": "-",
    "8 Gears": "-",
    "9 or More Gears": "-",
    "Acceleration (0-60 time in seconds)": "8.8777",
    "Average Number of Gears": "4.0",
    "Cylinder Deactivation": "0.309",
    "Drivetrain - 4WD": "0.453",
    "Drivetrain - Front": "-",
    "Drivetrain - Rear": "0.547",
    "Engine Displacement": "297.9739",
    "Footprint (sq. ft.)": "-",
    "Fuel Delivery - Carbureted": "-",
    "Fuel Delivery - Gasoline Direct Injection (GDI)": "-",
    "Fuel Delivery - Other": "-",
    "Fuel Delivery - Port Fuel Injection": "1.000",
    "Fuel Delivery - Throttle Body Injection": "-",
    "HP/Engine Displacement": "0.926256",
    "HP/Weight (lbs)": "0.052797",
    "Horsepower (HP)": "276.1167",
    "Manufacturer": "GM",
    "Model Year": "2007",
    "Multivalve Engine": "0.053",
    "Powertrain - Diesel": "-",
...
```

#### Route: /manufacturers
To get a list of the manufacturers in the Auto Trends data set, run the command `curl http://127.0.0.1:5000/manufacturers` and an example output of this command is shown below: 
```
[
  "All",
  "Nissan",
  "Hyundai",
  "Tesla",
  "Mercedes",
  "Ford",
  "VW",
  "Stellantis",
  "GM",
  "Subaru",
  "BMW",
  "Toyota",
  "Kia",
  "Mazda",
  "Honda"
]
```

#### Route: /manufacturers/\<manufacturer\>
To get all of the data associated with a specific manufacturer, use the command `curl http://127.0.0.1:5000/manufacturers/<manufacturer>` and replace \<manufacturer\> with the name of the manufacturer that you are looking for. Below is an example of what `curl http://127.0.0.1:5000/manufacturers/Toyota` looks like:
```
[
  {
    "2-Cycle MPG": "30.58902",
    "4 or Fewer Gears": "0.770",
    "5 Gears": "0.230",
    "6 Gears": "-",
    "7 Gears": "-",
    "8 Gears": "-",
    "9 or More Gears": "-",
    "Acceleration (0-60 time in seconds)": "11.6225",
    "Average Number of Gears": "4.0",
    "Cylinder Deactivation": "-",
    "Drivetrain - 4WD": "-",
    "Drivetrain - Front": "0.847",
    "Drivetrain - Rear": "0.153",
    "Engine Displacement": "120.2838",
    "Footprint (sq. ft.)": "-",
    "Fuel Delivery - Carbureted": "-",
    "Fuel Delivery - Gasoline Direct Injection (GDI)": "-",
    "Fuel Delivery - Other": "-",
    "Fuel Delivery - Port Fuel Injection": "1.000",
    "Fuel Delivery - Throttle Body Injection": "-",
    "HP/Engine Displacement": "0.999072",
    "HP/Weight (lbs)": "0.040460",
    "Horsepower (HP)": "120.3914",
    "Manufacturer": "Toyota",
    "Model Year": "1991",
    "Multivalve Engine": "1.000",
    "Powertrain - Diesel": "-",
    "Powertrain - Electric Vehicle (EV)": "-",
...
```

#### Route: /manufacturers/\<manufacturer\>/years
To get a list of the model years for which there are data points for a specific manufacturer, you can run the command `curl http://127.0.0.1:5000/manufacturers/<manufacturer>/years` and replace \<manufacturer\> with the name of the manufacturer. Below is an example output for `curl http://127.0.0.1:5000/manufacturers/Tesla/years`:
```
[
  "1979",
  "1985",
  "1976",
  "2020",
  "1989",
  "2018",
  "2011",
  "1984",
  "2017",
  "1986",
  "1982",
  "2016",
  "2008",
  "1978",
  "2005",
  "2001",
  "2009",
  "2019",
  "1975",
  "1994",
  "2021",
  "1987",
  "2013",
  "1998",
  "1992",
  "2004",
...
```

#### Route: /manufacturers/\<manufacturer\>/years/\<year\>
To get the data points for a specific manufacturer during a certain year, run the command `curl http://127.0.0.1:5000/manufacturers/<manufacturer>/years/<year>` and replace \<manufacturer\> with the name of the manufacturer and \<year\> with the model year. Below is an example of what running `curl http://127.0.0.1:5000/manufacturers/Tesla/years/2019` could return:
```
[
  {
    "2-Cycle MPG": "125.19278",
    "4 or Fewer Gears": "1.000",
    "5 Gears": "-",
    "6 Gears": "-",
    "7 Gears": "-",
    "8 Gears": "-",
    "9 or More Gears": "-",
    "Acceleration (0-60 time in seconds)": "4.2058",
    "Average Number of Gears": "1.0",
    "Cylinder Deactivation": "-",
    "Drivetrain - 4WD": "1.000",
    "Drivetrain - Front": "-",
    "Drivetrain - Rear": "-",
    "Engine Displacement": "-",
    "Footprint (sq. ft.)": "54.80000",
    "Fuel Delivery - Carbureted": "-",
    "Fuel Delivery - Gasoline Direct Injection (GDI)": "-",
    "Fuel Delivery - Other": "1.000",
    "Fuel Delivery - Port Fuel Injection": "-",
    "Fuel Delivery - Throttle Body Injection": "-",
    "HP/Engine Displacement": "-",
    "HP/Weight (lbs)": "0.094163",
    "Horsepower (HP)": "557.9626",
    "Manufacturer": "Tesla",
    "Model Year": "2019",
    "Multivalve Engine": "-",
    "Powertrain - Diesel": "-",
...
```

#### Route: /co2_year_plot
Method = POST: Use this route to create and load an image based on the Auto Trends Dataset into Redis. This image is a graph of the average CO2 emissions per year plotted over time. To load the image into Redis, run `curl -X POST http://127.0.0.1:5000/co2_year_plot` which will return a message like the one below:
```
Auto Trends data image is loaded into Redis
```

Method = GET: This route can be used also be used to get the image locally if it is present in the database by changing the method to GET. To do this, run `curl -X GET http://127.0.0.1:5000/co2_year_plot --output filename.png` and replace `filename` with a name that you want. This will return the image of the graph in redis to the directory you are currently in and will return an output like below:
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 26827  100 26827    0     0  3274k      0 --:--:-- --:--:-- --:--:-- 3274k
```

Method = DELETE: The DELETE method for this route will delete the image from the Redis database. To do this, run `curl -X DELETE http://127.0.0.1:5000/co2_year_plot` and below is an example of the output message is the image is found in the database and deleted:
```
Auto Trends data image has been deleted from Redis
```

#### Route: /weight_mpg_plot/<year>
Method = POST: Use this route to create and load an image based on the Auto Trends Dataset into Redis. This image is a graph that compares a vehicles weight to its fuel efficiency from the year specified by the user. To load the image into Redis, run `curl -X POST http://127.0.0.1:5000/weight_mpg_plot/<year>` which will return a message like the one below:
```
image has been loaded to redis
```

Method = GET: This route can be used also be used to get the image locally if it is present in the database by changing the method to GET. To do this, run `curl -X GET http://127.0.0.1:5000/weight_mpg_plot/<year> --output filename.png` and replace `filename` with a name that you want. This will return the image of the graph in redis to the directory you are currently in and will return an output like below:
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 26827  100 26827    0     0  3274k      0 --:--:-- --:--:-- --:--:-- 3274k
```

Method = DELETE: The DELETE method for this route will delete the image from the Redis database. To do this, run `curl -X DELETE http://127.0.0.1:5000/weight_mpg_plot/<year>` and below is an example of the output message is the image is found in the database and deleted:
```
database is empty, nothing to flush
```
#### Route: /vehicleType_mpg_plot/<year>
Method = POST: Use this route to create and load an image based on the Auto Trends Dataset into Redis. This image is a graph that compares vehicle type to its fuel efficiency from the year specified by the user. To load the image into Redis, run `curl -X POST http://127.0.0.1:5000/vehicleType_mpg_plot/<year>` which will return a message like the one below:
```
Plot is loaded.
```

Method = GET: This route can be used also be used to get the image locally if it is present in the database by changing the method to GET. To do this, run `curl -X GET http://127.0.0.1:5000//vehicleType_mpg_plot/<year> --output filename.png` and replace `filename` with a name that you want. This will return the image of the graph in redis to the directory you are currently in and will return an output like below:
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 26827  100 26827    0     0  3274k      0 --:--:-- --:--:-- --:--:-- 3274k
```

Method = DELETE: The DELETE method for this route will delete the image from the Redis database. To do this, run `curl -X DELETE http://127.0.0.1:5000/vehicleType_mpg_plot/<year>` and below is an example of the output message is the image is found in the database and deleted:
```
Plot has been deleted
```

#### Route: /download/<jobid\>
To download the image from a specific job ID, you can run the command `curl http://127.0.0.1:5000/download/<jobid>` and replace \<jobID\> with the desired job ID. Below is an example output for `curl http://127.0.0.1:5000/download/<jobid>`:
```
ADD EXAMPLE OUTPUT HERE
```
