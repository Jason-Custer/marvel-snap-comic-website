# Marvel Snap Comic Database

This project aims to create a web application that displays Marvel Snap card information, including comic book connections.

## Hour 1: VS Code Installation and Project Setup

In this hour, I installed VS Code and the Python extension, and set up the basic project structure.

### VS Code and Python Extension

I installed VS Code and the Python extension.

### Project Setup

I created the project folder and initial files (`index.html`, `app.py`, `.gitignore`, `README.md`).

### Learnings

* Learned how to install and set up VS Code.
* Learned how to install the Python extension.
* Learned how to create a basic project structure.

## Hour 2: HTML Structure and Static Data

In this hour, I created the basic HTML structure for the website and set up the static card data.

### HTML Structure

I created the basic HTML structure in `index.html`, including a placeholder for the card data.

### Static Card Data

I created a Python list of dictionaries in `app.py` to represent the card data (Iron Man and Hulk). I also downloaded sample card images and placed them in the "images" folder, naming them "iron-man.png" and "hulk.png".

### Learnings

* Learned the basic structure of an HTML document.
* Learned how to create a Python list of dictionaries to store data.
* Learned how to create a folder within the project.
* Learned how to add images to the project and the importance of consistent naming conventions.

## Hour 3: Flask App Setup and Basic Display Logic

In this hour, I set up a basic Flask application and implemented the logic to display the static card data in the `index.html` template.

### Flask Setup

I installed Flask and created a basic Flask application in `app.py`. I also created a `templates` folder and moved `index.html` into it.

### Display Logic

I modified `app.py` to pass the `card_data` to the `index.html` template.

### Learnings

* Learned how to create a basic Flask application.
* Learned how to use `render_template` to pass data to an HTML template.
* Learned how to run a Flask application.
* Learned how to create a templates folder.

## Hour 4: Displaying Card Images and Information

In this hour, I modified the `index.html` template to display the card images and information from the `card_data` that is passed from the Flask app.

### HTML Modification

I used Jinja2 templating to loop through the `cards` list and display the card names, energy, power, and images.

### Learnings

* Learned how to use Jinja2 templating to display dynamic content in HTML.
* Learned how to display images in HTML.
* Learned how to loop through a list of dictionaries in Jinja2.
* Learned how to configure Flask to serve static files.

## Hour 5: Version Control with GitHub

In this hour, I initialized a Git repository, created a GitHub repository, and connected them to establish version control for the project.

### Git Initialization

I initialized a Git repository using the `git init` command.

### GitHub Repository Creation

I created a new GitHub repository for the project.

### Connecting Local and Remote Repositories

I connected the local repository to the remote repository using the `git remote add origin` command. I then committed and pushed the code to GitHub.

### .gitignore

I created a `.gitignore` file to ignore unnecessary files and folders.

### Learnings

* Learned how to initialize a Git repository.
* Learned how to create a GitHub repository.
* Learned how to connect local and remote repositories.
* Learned how to use `.gitignore` to ignore files.
