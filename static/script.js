async function fetchCities() {
    try {
        const response = await fetch('/cities');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const cities = await response.json();
        console.log("Cities:", cities);
        const citySelect = document.getElementById('city-select');

        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city.id;
            option.text = city.name;
            citySelect.add(option);
        });
    } catch (error) {
        console.error("Error fetching cities:", error);
    }
}

async function fetchWeather() {
    const cityId = document.getElementById('city-select').value;
    const unit = document.querySelector('input[name="unit"]:checked').value;
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    try {
        const response = await fetch(`/weather?city_id=${cityId}&start_date=${startDate}&end_date=${endDate}&unit=${unit}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const weatherData = await response.json();
        displayWeather(weatherData);
    } catch (error) {
        console.error("Error fetching weather:", error);
    }
}

function displayWeather(data) {
    const weatherContainer = document.getElementById('weather-data');
    weatherContainer.innerHTML = '';

    if (data.length === 0) {
        weatherContainer.innerHTML = '<p>No weather data available for the selected city and date range.</p>';
        return;
    }

    data.forEach(item => {
        const weatherItem = document.createElement('div');
        weatherItem.classList.add('weather-item');
        weatherItem.innerHTML = `
            <p><strong>Date:</strong> ${item.date}</p>
            <p><strong>Temperature:</strong> ${item.temperature_c} °C / ${item.temperature_f} °F</p>
        `;
        weatherContainer.appendChild(weatherItem);
    });
}

document.getElementById('fetch-weather').addEventListener('click', fetchWeather);
document.addEventListener('DOMContentLoaded', fetchCities);
