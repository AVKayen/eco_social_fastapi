## Overview
A RESTful API written in Python with FastAPI. Made for the Green Buddies mobile app 
that can be found [here](https://github.com/AVKayen/eco_social_flutter).

## Requirements
- python 3.12+
- MongoDB database

## Setup
Create a .env file in the root directory according to the .env.example file.
To install required dependencies run:
```bash
pip install -r requirements.txt
```

## Run the server
```bash
uvicorn main:app --port 2000
```

## Licence
[MIT](https://github.com/AVKayen/eco_social_fastapi/blob/master/LICENSE)