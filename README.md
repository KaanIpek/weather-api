# Weather App

A FastAPI-based application to fetch and display weather data for specified cities. This application integrates with the OpenWeather API to get weather forecasts and stores them in a SQLite database.

## Features

- Fetches weather data for predefined cities: New Delhi, Istanbul, New York, Paris.
- Allows users to select a city, date range, and temperature unit (Celsius or Fahrenheit) to view the weather data.
- Automatically fetches weather data for the predefined cities on application startup.
- Provides endpoints to read city data, fetch weather data, and retrieve weather data from the database.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/weather-app.git
    cd weather-app
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up your OpenWeather API key:
    ```bash
    export WEATHER_API_KEY=your_openweather_api_key  # On Windows use `set WEATHER_API_KEY=your_openweather_api_key`
    ```

## Database Setup

1. Initialize the database:
    ```bash
    alembic upgrade head
    ```

## Running the Application

1. Start the FastAPI application:
    ```bash
    uvicorn app.main:app --reload
    ```

2. Open your browser and navigate to `http://127.0.0.1:8000` to access the application.

## API Endpoints

### Fetch Weather Data

- **Endpoint**: `/weather/fetch`
- **Method**: `POST`
- **Description**: Fetches weather data for the specified city and stores it in the database.
- **Payload**:
    ```json
    {
        "city_name": "Istanbul"
    }
    ```

### Get Weather Data

- **Endpoint**: `/weather`
- **Method**: `GET`
- **Description**: Retrieves weather data for a specified city and date range.
- **Query Parameters**:
    - `city_id`: The ID of the city.
    - `start_date`: The start date in the format `YYYY-MM-DD`.
    - `end_date`: The end date in the format `YYYY-MM-DD`.
    - `unit`: The temperature unit, either `metric` (Celsius) or `imperial` (Fahrenheit).

- **Example**:
    ```bash
    http://127.0.0.1:8000/weather?city_id=1&start_date=2024-06-14&end_date=2024-06-21&unit=metric
    ```

### Get Cities

- **Endpoint**: `/cities`
- **Method**: `GET`
- **Description**: Retrieves the list of cities from the database.

### Create City

- **Endpoint**: `/cities`
- **Method**: `POST`
- **Description**: Adds a new city to the database.
- **Payload**:
    ```json
    {
        "name": "Berlin"
    }
    ```

## Running Tests

1. To run the tests, use:
    ```
    pytest
    ```

## Project Structure

weather-app/
├── alembic/ # Alembic configurations and migrations
├── app/
│ ├── init.py
│ ├── main.py # FastAPI application
│ ├── models.py # SQLAlchemy models
│ ├── schemas.py # Pydantic schemas
│ ├── crud.py # CRUD operations
│ ├── deps.py # Dependency overrides
│ ├── database.py # Database configurations
├── tests/ # Test cases
│ ├── init.py
│ ├── test_main.py # Test cases for main functionalities
├── static/
│ ├── index.html # Frontend HTML
│ ├── style.css # Frontend CSS
│ ├── script.js # Frontend JS
├── requirements.txt # Python dependencies
├── README.md # Project README


## Notes

- Ensure you have set the `WEATHER_API_KEY` environment variable with your OpenWeather API key before running the application.
- The application will fetch and store weather data for the predefined cities (`New Delhi`, `İstanbul`, `New York`, `Paris`) on startup.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
