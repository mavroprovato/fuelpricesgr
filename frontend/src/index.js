import { DateTime } from 'luxon';
import { easepick } from '@easepick/core';
import { LockPlugin } from '@easepick/lock-plugin';
import { RangePlugin } from '@easepick/range-plugin';
import Chart from 'chart.js/auto';

import './style.css';

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
};

/**
 * The date picker.
 */
let datePicker = null;

/**
 * The latest prices.
 */
let latestPrices = null;

/**
 * The daily country chart.
 */
let dailyCountryChart = null;

/**
 * The API object.
 */
const API = {
    /** The base API URL. */
    baseApiUrl: 'http://localhost:8000',

    /**
     * Fetch the date range for the data type.
     *
     * @param dataType The data type.
     * @returns {Promise<Response>}
     */
    async dateRage(dataType) {
        return await fetch(`${this.baseApiUrl}/dateRange/${dataType}`);
    },

    /**
     * Fetch the daily country data.
     *
     * @param startDate The start date of the data to fetch, as an ISO date string.
     * @param endDate The end date of the data to fetch, as an ISO date string.
     * @returns {Promise<Response>}
     */
    async dailyCountryData(startDate, endDate) {
        let url = `${this.baseApiUrl}/data/daily/country`;
        let queryString = '';
        if (startDate) {
            queryString += `start_date=${startDate}`
        }
        if (endDate) {
            if (queryString) {
                queryString += '&';
            }
            queryString += `end_date=${endDate}`
        }
        if (queryString) {
            url += `?${queryString}`;
        }

        return await fetch(url);
    }
}

/**
 * Initialize the date range picker from the date range API response.
 *
 * @param dateRange The date range API response.
 */
function initializeDatePicker(dateRange) {
    let minDate = DateTime.fromISO(dateRange.start_date);
    let maxDate = DateTime.fromISO(dateRange.end_date);
    let endDate = maxDate;
    let startDate = endDate.minus({'month': 6});

    return new easepick.create({
        element: document.getElementById('datepicker'),
        css: [
            'https://cdn.jsdelivr.net/npm/@easepick/bundle@1.2.0/dist/index.css',
            'https://cdn.jsdelivr.net/npm/@easepick/lock-plugin@1.2.0/dist/index.css',
        ],
        setup(picker) {
            picker.on('select', event => {
                loadPage(
                    DateTime.fromJSDate(event.detail.start).toISODate(),
                    DateTime.fromJSDate(event.detail.end).toISODate())
                ;
            });
        },
        plugins: [LockPlugin, RangePlugin],
        RangePlugin: {
            startDate: startDate.toISODate(),
            endDate: endDate.toISODate()
        },
        LockPlugin: {
            minDate: minDate.toISODate(),
            maxDate: maxDate.toISODate()
        },
    });
}

/**
 * Load the latest country values.
 */
function displayLatestValues(latestData, previousData) {
    if (latestData) {
        latestPrices.querySelector('h2').innerHTML = `Τιμές Καυσίμων ${latestData.date}`;
        const table = latestPrices.querySelector('table');
        Object.keys(FuelType).forEach(fuelType => {
            const tableRow = table.querySelector(`#${fuelType.toLowerCase().replace('_', '-')}`);
            const fuelData = latestData.data.find(e => e.fuel_type === fuelType);
            if (fuelData) {
                tableRow.style.display = 'table-row';
                tableRow.querySelector('.fuel-price').innerHTML = fuelData.price;
                if (previousData) {
                    const evolutionElem = tableRow.querySelector('.fuel-price-evolution');
                    const previousFuelData = previousData.data.find(e => e.fuel_type === fuelType);
                    if (previousFuelData) {
                        const evolution = (fuelData.price - previousFuelData.price) / fuelData.price;
                        evolutionElem.innerHTML = (evolution > 0 ? '+' : '') + (evolution * 100).toFixed(2) + '%';
                    } else {
                        evolutionElem.innerHTML = '';
                    }
                }
            } else {
                tableRow.style.display = 'none';
            }
        })
    }
}

/**
 * Display the daily country data in a graph.
 *
 * @param data The daily country data response from the API.
 */
function displayDailyCountryChart(data) {
    const prices = {};
    for (const fuelType in FuelType) {
        prices[fuelType] = [];
    }
    const labels = [];
    for (const row of data) {
        labels.push(row.date);
        for (const fuelType in FuelType) {
            prices[fuelType].push(null);
        }
        for (const result of row.data) {
            prices[result.fuel_type][prices[result.fuel_type].length - 1] = result.price;
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

    dailyCountryChart.data = {
        labels: labels,
        datasets: datasets
    };
    dailyCountryChart.update();
}

/**
 * Load the page for the specified date range.
 *
 * @param startDate The start date.
 * @param endDate The end date.
 */
function loadPage(startDate, endDate) {
    API.dailyCountryData(startDate, endDate).then(response => {
        response.json().then(data => {
            displayLatestValues(...data.slice(-2).reverse());
            displayDailyCountryChart(data);
        });
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
        response.json().then(dateRange => {
            datePicker = initializeDatePicker(dateRange);
            latestPrices = document.getElementById('latest-prices');
            dailyCountryChart = new Chart(document.getElementById('chart').getContext('2d'), {
                type: 'line'
            });
            loadPage(dateRange.start_date, dateRange.end_date);
        });
    });
});
