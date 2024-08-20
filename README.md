# The Kicks API for the Kicks Web Application 

This is a Flask microservice I've built to serve real time shoe prices to the main Kicks Web App which is under development.  

## How it works
The API is hosted on an AWS EC2 instance and can be called [here]([http://18.219.22.255/]). Calling the */scrape* route with a shoe supplier + name will retrieve prices and variants from the official seller's site and return it in JSON format. 

**Example** 
Call to http://18.219.22.255/scrape/nikeairmax270/ 
Returns:
![image](https://github.com/user-attachments/assets/99bfcc7f-75bf-4ae1-8c46-d8612c714e76)

Currently, the API works for shoes from Nike, Adidas, Under Armour, and Skechers. 


