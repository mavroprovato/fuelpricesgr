import { DateTime } from 'luxon';
import { easepick } from '@easepick/core';
import { LockPlugin } from '@easepick/lock-plugin';
import { RangePlugin } from '@easepick/range-plugin';
import Chart from 'chart.js/auto';

import { FuelType, Prefecture } from './enums';
import { API } from './api';

import '../scss/styles.scss';

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
 * The prices per prefecture data.
 */
let pricesPerPrefecture = null;

/**
 * Initialize the date range picker from the date range API response.
 *
 * @param dateRange The date range API response.
 */
function initializeDatePicker(dateRange) {
    let minDate = DateTime.fromISO(dateRange.start_date);
    let maxDate = DateTime.fromISO(dateRange.end_date);
    let endDate = maxDate;
    let startDate = endDate.minus({'month': 3});

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
        const tableBody = latestPrices.querySelector('table tbody');
        tableBody.innerHTML = '';
        Object.keys(FuelType).forEach(fuelType => {
            const fuelData = latestData.data.find(e => e.fuel_type === fuelType);
            if (fuelData) {
                const rowElement = document.createElement('tr');
                let evolution = '';
                if (previousData) {
                    const previousFuelData = previousData.data.find(e => e.fuel_type === fuelType);
                    evolution = (fuelData.price - previousFuelData.price) / fuelData.price;
                    evolution = (evolution > 0 ? '+' : '') + (evolution * 100).toFixed(2) + '%';
                }
                rowElement.innerHTML = `
                    <td>${FuelType[fuelType].label}</td><td>${fuelData.price.toFixed(3) + "€"}</td><td>${evolution}</td>
                `;
                tableBody.append(rowElement)
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
 * Display the per prefecture data in a table.
 *
 * @param data The prefecture data.
 */
function displayPrefectureTable(data) {
    if (data) {
        const tableBody = pricesPerPrefecture.querySelector('table tbody');
        tableBody.innerHTML = '';
        data.prefectures.forEach(prefecture => {
            const rowElement = document.createElement('tr');
            rowElement.innerHTML = `<td>${Prefecture[prefecture.prefecture]}</td>`
            tableBody.append(rowElement)
        });
    }
}

/**
 * Load the page for the specified date range.
 *
 * @param startDate The start date.
 * @param endDate The end date.
 */
function loadPage(startDate, endDate) {
    document.querySelectorAll('.latest-date').forEach(span => {
        span.innerHTML = endDate;
    });
    API.dailyCountryData(startDate, endDate).then(response => {
        response.json().then(data => {
            displayLatestValues(...data.slice(-2).reverse());
            displayDailyCountryChart(data);
        });
    });
    API.countryData(endDate).then(response => {
        response.json().then(data => {
            displayPrefectureTable(data);
        });
    })
}

/**
 * Called when the DOM has been loaded.
 */
document.addEventListener("DOMContentLoaded", function() {
    // Fetch date range on load.
    API.dateRage('daily_country').then(response => {
        response.json().then(dateRange => {
            datePicker = initializeDatePicker(dateRange);
            latestPrices = document.getElementById('latest-prices');
            pricesPerPrefecture = document.getElementById('prices-per-prefecture');
            dailyCountryChart = new Chart(document.getElementById('chart').getContext('2d'), {
                type: 'line'
            });
            loadPage(dateRange.start_date, dateRange.end_date);
        });
    });
});
