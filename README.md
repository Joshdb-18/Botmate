# Botmate

Botmate is a chatbot that provides users with an interactive communication channel that can be used for a variety of purposes, such as customer support, personal assistant and data collection, it was built mainly as a personal assistant and also to answer educational related questions. It is built using Flask, HTML, CSS, JavaScript, and Bootstrap technologies.

## Features
Botmate has the following features:
- Can hold interactive conversations from users
- Supports text input from users
- Can perform search for images and videos
- Can provide information on variety of topics
- Offers personalized assistance to users

## Environment
This project is interpreted/tested on Ubuntu 22.04 using python3

## File Descriptions
[app.py](app.py) - The file that displays the web application and defines the route for each
List of classes and functions in this app:
* `class User(db.Model)` - Create User Model which contains the user credentials
* `def after_request(response)` - Ensures the responses aren't cached
* `def index()` - Renders the index template
* `def register()` - Registers user
* `def login()` - Logs user in
* `def chat()` - Generates chat response
* `def image()` - Generate images
* `def video()` - Generate videos
* `def history()` - Shows history 
* `def logout()` - Logs user out

[config.py](config.py) - Holds the app configuration 
* `class Config(object)` - sets the debug and testing mode
* `class DevelopmentConfig(Config)` - configures the secret key and the api key

[aiapi.py](aiapi.py) - Sets the bot role
* `def generateChatResponse(prompt)` - sets the bot role and generate a response

[helpers.py](helpers.py) - Helper function for the app
Functions:
* `def apology(message, code=400)` - Render message as apology to user when an error is encountered
* `def login_required(f)` - Decorates routes to require login

[validate.py](validate.py) - Creates database, make sure you run this code using ``python3 validate.py`` or ``./validate.py`` to create the database
 
#### `templates/` directory contains templates used for this project
[login.html](/templates/login.html) - The login page
Form input:
* `Username` - Username of the registered user
* `Password` - Password of the registered user
* `Logout` - Log the user out after login is successful

[register.html](/templates/register.html) - The signup page
Form input:
* `Username` - Unique username of the new user
* `Password` - Unique password of the new user
* `Confirmation` - Password confirmation

[layout.html](/templates/layout.html) - The layout for the entire web application except the landing page
* `header` - Defines the header for the web application
* `body` - Defines the block body for the web application

[chat.html](/templates/chat.html) - Conversation template between the user and the bot
* `input` - Takes the prompt from the user and returns the appropriate answer

[image.html](/templates/image.html) - Image template
* `input` - Takes an input as prompt and returns a corresponding list of images

[video.html](/templates/video.html) - Video template
* `input` - Takes an input as prompt and returns a corresponding list of videos

[styles.css](/static/styles/styles.css) - The styling for the web application


## Installation
To install Botmate, follow these steps:
1. Clone the Botmate repository to your local machine. ``git clone https://github.com/Joshdb-18/Botmate.git``
2. Access Botmate directory: `cd Botmate`
3. Install the required dependencies by running the command ``pip install requirement.txt``
4. Get an OPENAI api key and edit the ``config.py`` file
5. Get an Unsplash api key and edit the ``app.py`` file
6. Get a Youtube api key from [here](https://www.console.cloud.google.com), create a new project, then add the youtube api v3 service, then create a new credential and generate an api key, then edit the ``app.py`` file
7. Run the `app.py` file using the command `python3 app.py` or `flask run`
8. Access the Botmate chatbot at `http://localhost:5000`.

## Usage
To use Botmate, follow these steps:
1. Open your web browser and navigate to the Botmate web application
2. Register, or log in if you already have an account
3. Type your message in the chat input and click the enter key
4. Botmate will respond with a relevant message or perform a search based on your input
5. Use the Image and Video search buttons to perform a search for images or videos.

## Contributing
If you would like to contribute to Botmate, follow these steps:
1. Fork the Botmate repository to your GitHub account
2. Clone the repository to your local machine
3. Create a new branch for your changes
4. Make your changes and test them locally
5. Push your changes to your forked repository
6. Submit a pull request to the main Botmate repository.

## Credits
Botmate was created by Damilola Joshua Oluwafemi

## License
Botmate is licensed under the MIT license. See the LICENSE file for more information

Check out the full deployment off the app [here](http://jalcy.pythonanywhere.com)
