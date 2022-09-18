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
     * Return the date range for the data type.
     *
     * @param dataType The data type.
     * @returns {Promise<Response>}
     */
    async dateRage(dataType) {
        return await fetch(`${this.baseApiUrl}/dateRange/${dataType}`);
    },

    /**
     * Fetch the country data.
     *
     * @returns {Promise<Response>}
     */
    async dailyCountryData(startDate, endDate) {
        let url = `${this.baseApiUrl}/data/daily/country`;
        let queryString = '';
        if (startDate) {
            queryString += `start_date=${startDate.toISODate()}`
        }
        if (endDate) {
            if (queryString) {
                queryString += '&';
            }
            queryString += `end_date=${endDate.toISODate()}`
        }
        if (queryString) {
            url += `?${queryString}`;
        }
        return await fetch(url);
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
        document.getElementById('latest-prices-heading').innerHTML += ' ' + data[data.length - 1]['date'];
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
 * Load the daily country data chart.
 *
 * @param data The daily country data.
 * @returns {*} The daily country data.
 */
function loadDailyCountryChart(data) {
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
 * Initialize the date range picker from the date range API response.
 *
 * @param dateRange The date range API response.
 */
function initializeDatePicker(dateRange) {
    let minDate = luxon.DateTime.fromISO(dateRange.start_date);
    let maxDate = luxon.DateTime.fromISO(dateRange.end_date);
    let endDate = maxDate;
    let startDate = endDate.minus({'month': 6});
    // Initialize the date picker
    new easepick.create({
        element: document.getElementById('datepicker'),
        css: [
            'https://cdn.jsdelivr.net/npm/@easepick/bundle@1.2.0/dist/index.css',
        ],
        plugins: ['RangePlugin', 'LockPlugin'],
        RangePlugin: {
            startDate: startDate.toISODate(),
            endDate: endDate.toISODate()
        },
        LockPlugin: {
            minDate: minDate.toISODate(),
            maxDate: maxDate.toISODate()
        }
    });
    API.dailyCountryData(startDate, endDate).then(response => {
        if (response.ok) {
            response.json().then(loadLatestValues).then(loadDailyCountryChart);
        } else {
            console.error("Could not fetch country data");
        }
    });
}

/**
 * Called when the DOM has been loaded.
 */
document.addEventListener("DOMContentLoaded", function() {
    // Hide all latest prices elements initially, because they can be missing.
    document.getElementById('latest-prices').querySelectorAll('tr').forEach(elem => {
        elem.style.display = 'none';
    })
    // Fetch date range on load.
    API.dateRage('daily_country').then(response => {
        if (response.ok) {
            response.json().then(initializeDatePicker);
        } else {
            console.error("Could not fetch date range");
        }
    });
});
