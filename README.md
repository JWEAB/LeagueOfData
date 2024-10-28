# League of Data

League of Data is a web application that interacts with the Riot Games API to retrieve match statistics for a specified League of Legends player.

## Features

- Fetch match statistics for a specific League of Legends player.
- Display customizable match tables with user-selected preferences.
- Generate graphs based on selected data preferences.

## Technology Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **APIs**: Riot Games API
- **Graph Generation**: Matplotlib

## Project Structure

```bash
league-of-data/
│
├── app.py                  
├── static/
│   ├── style.css              
│   ├── Draven.jpg              
├── templates/
│   └── index.html              
├── requirements.txt           
└── README.md
```

## Installation

**Install the required dependencies**:

    bash
    pip install -r requirements.txt

**Obtain a Riot Games API Key**:
    - Visit the [Riot Developer Portal](https://developer.riotgames.com/) and sign up or log in.
    - Create an API key to use with your application.
    - Insert into app.py

**Run the application**:

    bash
    flask run

    The application will start at `http://127.0.0.1:5000`.

## Enjoy League of Data

Start analyzing gameplay today! Look up any summoner, create a table, generate graphs, and improve your performance with **League of Data**.
             
