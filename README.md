# LifeHack2022-MixedRice

## About Project
Our Team, Team MixedRice, aims to use our RecyclingRight Bot to make recycling easier and more accessible to Singaporeans.
<div style="display:flex">
<span>
		<img src="https://github.com/EuniceSim142/LifeHack2022-MixedRice/blob/main/assets/checkifrecyclable.jpg?raw=true" alt="IMAGE ALT TEXT HERE" width="200" border="10" />
</span>
<span>
		<img src="https://github.com/EuniceSim142/LifeHack2022-MixedRice/blob/main/assets/findnearestbin.jpg?raw=true" alt="IMAGE ALT TEXT HERE" width="200" border="10" />
</span>
<span>
		<img src="https://github.com/EuniceSim142/LifeHack2022-MixedRice/blob/main/assets/quiz.jpg?raw=true" alt="IMAGE ALT TEXT HERE" width="200" border="10" />
</span>
</div></br>

Our bot can be accessed on @recycleright_bot, the features available in our bot is is shown in the screenshots above and table below:

| Features | Description |
| :------------- |:-------------|
| /start | Description of bot |
| /checkifrecyclable | Check if an item is recyclable |
| /findnearestbin | Find the nearest recycling bin |
| /quiz | Test your recycling knowledge |

## Environment Setup
This project uses local Virtual Environment to manage project dependencies. [(environment creation and activation guide)](https://docs.python.org/3/tutorial/venv.html)

To install dependencies, run:
```pip install -r requirements.txt``` after activating virtual environment.

Alternatively, you can run the commands below:
| Dependency | Installation |
| :------------- |:-------------|
| Python=3.8+ | |
| Python Telegram Bot | `pip install python-telegram-bot` |
| SQLAlchemy | `pip install SQLAlchemy` |
| Requests | `pip install requests` |
| Dot-Env | `pip install python-dotenv` |
| Pandas | `pip install pandas` |
| Psycopg2 | `pip install psycopg2` |
| Psycopg2-binary | `pip install psycopg2-binary` |
| GeoPandas | `pip install geopandas` |
| GeoPy | `pip install geopy` |


Additionaly, you will need to create an ```.env``` file and store your Telegram Bot Token as ```BOT_TOKEN="<Your Telegram Bot Token>"```

## Database Configuration
This project uses PostgreSQL [(setup guide)](https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql/) or SQlite database.</br>
To use PostgreSQL database, add into your .env file ```POSTGRESQL_CONNECTION_STRING = "postgresql://<Username>:<Password>@<Servername>:<Port>/<DB>"```

## Data Used
| File | Source |
| :------------- |:-------------|
| items.csv | Collected from [National Environment Agency](https://www.nea.gov.sg/docs/default-source/our-services/waste-management/list-of-items-that-are-recyclable-and-not.pdf) |
| recycling-bins-shp (Folder) | [Data.gov.sg (National Environment Agency)](https://data.gov.sg/dataset/recycling-bins?resource_id=8ec05819-7d0b-489c-826e-e196f5f4114e)|

## Getting Started
1. Run all the cells in the ```initial_db_upload.ipynb``` Jupyter Notebook to load all the necessary data into the database.
2. Run ```python bot.py``` in terminal
