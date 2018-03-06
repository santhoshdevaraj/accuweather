# Weather API

## Running the server

1) Clone the GIT repo
    *   `git clone git-url`

2) Create virtual environment and install python project dependencies:
    *   `cd accuweather`
    *   `python3 -m venv venv`
	*   `source venv/bin/activate`
    *   `pip install -r requirements.txt`

3) Start the server
    *   `python manage.py runserver`

## To load the CSV dataset into the DB

1) You may not need this step as the DB file is included in the pkg
    *   `python manage.py load_data --file 'path_to_the_csv_file'`

## Using the API

1) To get the list of cities having weather information

   * `/api/cities/`

2) To get the daily weather for a given city

   * `/api/weather/?city=abc`

3) To get the weekly or monthly weather for a given city, use the `frequency` filter. Default `frequency` is `daily`

   * `/api/weather/?city=abc&frequency=weekly`

4) To get the weather for a given city between a date range, use the `start_date` and `end_date` filter

   * `/api/weather/?city=abc&start_date=2016-09-23&end_date=2016-10-01`

5) To get the weather for a given city in fahrenheit, use the `temp_format` filter. Default `temp_format` is `fahrenheit`

   * `/api/weather/?city=abc&temp_format=celsius`
