
# IronSource Home Assignment

The containerized application is designed to manage customer purchases. It is made up of the following containers:
 1. MongoDB
 2. Zookeeper (for Kafka)
 3. Kafka server
 4. Customer Management API
 5. Customer-facing web server & frontend.

# Running the application 
To run the application, follow these steps:
1. Make sure you have `git`, `docker`, and `docker compose` on your machine
2. Clone this repository:
`git clone https://github.com/omermishania/ironsource-home-assigment.git`
3. Change the directory to the cloned Git repository:
`cd ironsource-home-assigment`
4. Deploy the application:
`docker compose up -d`
5. 1.  Access the application by navigating to [http://localhost:5002](http://localhost:5002/) in your web browser (you may have to wait a few seconds for the application to start running).

After following these steps, you should be able to use the application's frontend to initiate purchase requests and view all of your purchases.