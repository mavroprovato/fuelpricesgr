/**
 * The fuel types enumeration.
 */
const FuelType = {
    UNLEADED_95: {
        label: "Αμόλυβδη 95",
        borderColor: 'rgb(64, 83, 211)'
    },
    UNLEADED_100: {
        label: 'Αμόλυβδη 100',
        borderColor: 'rgb(211, 179, 16)'
    },
    GAS: {
        label: "Υγραέριο",
        borderColor: 'rgb(0, 178, 93)'
    },
    DIESEL: {
        label: "Diesel",
        borderColor: 'rgb(0, 190, 255)'
    },
    DIESEL_HEATING: {
        label: "Diesel Θέρμανσης",
        borderColor: 'rgb(251, 73, 176)'
    },
    SUPER: {
        label: "Super",
        borderColor: 'rgb(181, 29, 20)',
        hidden: true
    }
}

/**
 * The API object.
 */
const API = {
    /** The base API URL. */
    baseApiUrl: 'http://localhost:8000',

    /**
     * Fetch the country data.
     *
     * @returns {Promise<Response>}
     */
    async fetchCountryData() {
        return await fetch(`${this.baseApiUrl}/data/daily/country`);
    }
}

/**
 * Load the latest country values.
 *
 * @param data The country daily data.
 * @returns {*} The country daily data.
 */
function loadLatestValues(data) {
    if (data) {
        const table = document.getElementById('latest-prices');
        data[data.length - 1].data.forEach(latestData => {
            const tableRow = table.querySelector(`#${latestData['fuel_type'].toLowerCase().replace('_', '-')}`);
            if (tableRow) {
                tableRow.style.display = 'table-row';
                tableRow.querySelector('.fuel-price').innerHTML = latestData['price'];
                if (data.length > 1) {
                    data[data.length - 2].data.forEach(previousData => {
                        if (previousData['fuel_type'] === latestData['fuel_type']) {
                            const evolution = (latestData['price'] - previousData['price']) / latestData['price'];
                            tableRow.querySelector('.fuel-price-evolution').innerHTML =
                                (evolution > 0 ? '+' : '') + (evolution * 100).toFixed(2) + '%';
                        }
                    })
                }
            }
        });
    }

    return data
}

/**
 * Load the country chart.
 *
 * @param data The country daily data.
 * @returns {*} The country daily data.
 */
function loadCountryChart(data) {
    const prices = {};
    for (const fuelType in FuelType) {
        prices[fuelType] = [];
    }
    const dates = [];
    for (const row of data) {
        dates.push(row['date']);
        for (const fuelType in FuelType) {
            prices[fuelType].push(null);
        }
        for (const result of row['data']) {
            prices[result['fuel_type']][prices[result['fuel_type']].length - 1] = result['price'];
        }
    }
    const datasets = []
    for (const fuelType in FuelType) {
        datasets.push({
            label: FuelType[fuelType].label,
            borderColor: FuelType[fuelType].borderColor,
            hidden: FuelType[fuelType].hidden,
            data: prices[fuelType],
        })
    }
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        }
    });

    return data
}

/**
 * Called when the DOM has been loaded.
 */
document.addEventListener("DOMContentLoaded", function() {
    // Hide all latest prices elements initially, because they can be missing.
    document.getElementById('latest-prices').querySelectorAll('tr').forEach(elem => {
        elem.style.display = 'none';
    })
    // Fetch country data on load.
    API.fetchCountryData().then(response => {
        if (response.ok) {
            response.json().then(loadLatestValues).then(loadCountryChart);
        } else {
            console.error("Could not fetch country data");
        }
    });
});
