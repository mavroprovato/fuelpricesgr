import { DateTime } from 'luxon';
import { easepick } from '@easepick/core';
import { LockPlugin } from '@easepick/lock-plugin';
import { RangePlugin } from '@easepick/range-plugin';
import Chart from 'chart.js/auto';

import { FuelType, Prefecture } from './enums';
import { API } from './api';

import '../scss/styles.scss';

/**
 * Formats a number as a price.
 *
 * @param price The price as a number.
 * @returns {string} The formatted price.
 */
function formatPrice(price) {
    if (price) {
        return price.toFixed(3) + "€";
    }

    return '-';
}

/**
 * Formats the evolution of a value as a percentage.
 *
 * @param {number} value The reference value.
 * @param {number} previousValue The previous value.
 * @returns The formatted evolution.
 */
function formatEvolution(value, previousValue) {
    let evolution = document.createElement('span');
    if (value && previousValue) {
        let evolutionValue = (value - previousValue) / value;
        if (evolutionValue > 0) {
            evolution.classList.add('text-danger');
        }
        else if (evolutionValue < 0) {
            evolution.classList.add('text-success');
        }
        evolution.innerHTML = (evolutionValue > 0 ? '+' : '') + (evolutionValue * 100).toFixed(2) + '%';
    }

    return evolution.outerHTML;
}

/**
 * The main page
 */
class Main {
    /** The latest prices table */
    latestPrices = null;
    /** The daily country chart */
    dailyCountryChart = null;
    /** The prices per prefecture table */
    pricesPerPrefecture = null;

    /**
     * The class constructor
     */
    constructor() {
        const instance = this;
        // Called when the DOM has been loaded
        document.addEventListener("DOMContentLoaded", function() {
            instance.latestPrices = document.getElementById('latest-prices');
            instance.dailyCountryChart = new Chart(document.getElementById('chart').getContext('2d'), {
                type: 'line'
            });
            instance.pricesPerPrefecture = document.getElementById('prices-per-prefecture');

            // Fetch date range on load
            API.dateRage('daily_country').then(response => {
                response.json().then(dateRange => {
                    const minDate = DateTime.fromISO(dateRange['start_date']);
                    const maxDate = DateTime.fromISO(dateRange['end_date']);
                    instance.dateRangeLoaded(minDate, maxDate)
                });
            });
        });
    };

    /**
     * Called when the data
     *
     * @param minDate
     * @param maxDate
     */
    dateRangeLoaded(minDate, maxDate) {
        // Initialize the page components
        this.initializeDatePicker(minDate, maxDate);
        // Load the page
        this.loadPage(minDate, maxDate);
    };

    /**
     * Initialize the date picker.
     *
     * @param minDate {DateTime} The minimum date that can be selected.
     * @param maxDate {DateTime} The maximum date that can be selected.
     * @returns The date picker.
     */
    initializeDatePicker(minDate, maxDate) {
        const instance = this;
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
                    instance.loadPage(DateTime.fromJSDate(event.detail.start), DateTime.fromJSDate(event.detail.end));
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
    };

    /**
     * Load the page for the specified date range.
     *
     * @param startDate {DateTime} The start date.
     * @param endDate {DateTime} The end date.
     */
    loadPage(startDate, endDate) {
        const instance = this;
        API.dailyCountryData(startDate, endDate).then(response => {
            document.querySelectorAll('.latest-date').forEach(span => {
                span.innerHTML = endDate.toISODate();
            });
            response.json().then(data => {
                instance.displayLatestValues(endDate, ...data.slice(-2).reverse());
                instance.displayDailyCountryChart(data);
            });
        });
        API.countryData(endDate).then(response => {
            response.json().then(data => {
                instance.displayPrefectureTable(data);
            });
        })
    };

    /**
     * Display the latest country values.
     *
     * @param date The selected date.
     * @param latestData The data for the latest date.
     * @param previousData The data for the previous available date.
     */
    displayLatestValues(date, latestData, previousData) {
        if (!latestData) {
            return;
        }
        const tableBody = this.latestPrices.querySelector('table tbody');
        tableBody.innerHTML = '';
        Object.keys(FuelType).forEach(fuelType => {
            const fuelData = latestData.data.find(e => e['fuel_type'] === fuelType);
            if (!fuelData) {
                return;
            }
            const rowElement = document.createElement('tr');
            rowElement.innerHTML = `
                <td>${FuelType[fuelType].label}</td>
                <td>${formatPrice(fuelData['price'])}</td>
                <td>${formatEvolution(fuelData['price'], previousData?.data.find(e => e['fuel_type'] === fuelType)?.price)}</td>
            `;
            tableBody.append(rowElement)
        })
    };

    /**
     * Display the daily country data in a graph.
     *
     * @param data The daily country data response from the API.
     */
    displayDailyCountryChart(data) {
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
                prices[result['fuel_type']][prices[result['fuel_type']].length - 1] = result.price;
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

        this.dailyCountryChart.data = {
            labels: labels,
            datasets: datasets
        };
        this.dailyCountryChart.update();
    };

    /**
     * Display the per prefecture data in a table.
     *
     * @param data The prefecture data.
     */
    displayPrefectureTable(data) {
        if (!data) {
            return;
        }
        const tableHeader = this.pricesPerPrefecture.querySelector('thead tr');
        tableHeader.innerHTML = '';
        const tableBody = this.pricesPerPrefecture.querySelector('tbody');
        tableBody.innerHTML = '';
        // Create the table header
        const countryData = {}
        data['country'].forEach(countryRow => {
            countryData[countryRow['fuel_type']] = {
                price: countryRow['price'],
                number_of_stations: countryRow['number_of_stations'],
            }
        });
        const header = document.createElement('th')
        header.innerHTML = 'Νομός';
        tableHeader.append(header);
        Object.keys(FuelType).filter(fuelType => countryData.hasOwnProperty(fuelType)).forEach(fuelType => {
            const header = document.createElement('th')
            header.innerHTML = FuelType[fuelType].label;
            tableHeader.append(header);
        });
        // Add the prefecture data
        data['prefectures'].sort((a, b) => {
            return Prefecture[a['prefecture']].localeCompare(Prefecture[b['prefecture']]);
        }).forEach(prefectureRow => {
            const row = document.createElement('tr')
            let rowHtml = `<td>${Prefecture[prefectureRow['prefecture']]}</td>`;
            Object.keys(FuelType).filter(fuelType => countryData.hasOwnProperty(fuelType)).forEach(fuelType => {
                rowHtml += `<td>${formatPrice(prefectureRow['data'].find(e => e['fuel_type'] === fuelType)?.price)}</td>`;
            });
            row.innerHTML = rowHtml;
            tableBody.append(row);
        });
    }
}

new Main();
