import { DateTime, Settings } from 'luxon';
import { easepick } from '@easepick/core';
import { LockPlugin } from '@easepick/lock-plugin';
import { RangePlugin } from '@easepick/range-plugin';
import Chart from 'chart.js/auto';

import { FuelType, Prefecture } from './enums';
import { API } from './api';

import '../scss/styles.scss';

Settings.defaultLocale = 'el-GR';

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
    } else {
        evolution.innerHTML = '-';
    }

    return evolution.outerHTML;
}

/**
 * The main page
 */
class Main {
    /** The fuel types selector */
    fuelTypeSelector = null;
    /** The latest country data table */
    latestCountryDataTable = null;
    /** The daily country data chart */
    dailyCountryDataChart = null;
    /** The prefecture data table **/
    prefectureDataTable = null;
    /** The daily country data */
    dailyCountryData = null;
    /** The latest country data per prefecture */
    countryData = null;

    /**
     * The class constructor
     */
    constructor() {
        const instance = this;
        // Called when the DOM has been loaded
        document.addEventListener("DOMContentLoaded", function() {
            // Initialize elements
            instance.fuelTypeSelector = instance.initializeFuelTypeSelector();
            instance.dailyCountryDataChart = instance.initializeDailyCountryDataChart();
            instance.latestCountryDataTable = instance.initializeLatestCountryDataTable();
            instance.prefectureDataTable = instance.initializePrefectureDataTable();
            // Fetch date range on load
            API.dateRage('daily_country').then(response => {
                response.json().then(dateRange => {
                    const startDate = DateTime.fromISO(dateRange['start_date']);
                    const endDate = DateTime.fromISO(dateRange['end_date']);
                    instance.initializeDatePicker(startDate, endDate);
                    instance.dateRangeSelected(startDate, endDate);
                });
            });
        });
    };

    /**
     * Initialize the fuel types selector.
     */
    initializeFuelTypeSelector() {
        const instance = this;
        const fuelTypesSelector = document.getElementById('fuel-types');
        Object.keys(FuelType).forEach(fuelType => {
            const fuelTypeInput = document.createElement('input');
            fuelTypeInput.id = `${fuelType}-selector`;
            fuelTypeInput.className = 'btn-check';
            fuelTypeInput.type = 'checkbox';
            fuelTypeInput.checked = !FuelType[fuelType].defaultUnselected;
            fuelTypeInput.addEventListener('input', () => {
                instance.fuelTypeSelectionChanged();
            });
            fuelTypesSelector.append(fuelTypeInput);

            const fuelTypeLabel = document.createElement('label');
            fuelTypeLabel.className = 'btn btn-outline-primary';
            fuelTypeLabel.htmlFor = `${fuelType}-selector`;
            fuelTypeLabel.innerHTML = FuelType[fuelType].label;
            fuelTypesSelector.append(fuelTypeLabel);
        });

        return fuelTypesSelector;
    };


    /**
     * Initialize the date picker.
     *
     * @param minDate {DateTime} The minimum available date.
     * @param maxDate {DateTime} The maximum available date.
     */
    initializeDatePicker(minDate, maxDate) {
        const instance = this;
        const startDate = maxDate.minus({'month': 3});

        new easepick.create({
            element: document.getElementById('datepicker'),
            css: [
                'https://cdn.jsdelivr.net/npm/@easepick/bundle@1.2.0/dist/index.css',
                'https://cdn.jsdelivr.net/npm/@easepick/lock-plugin@1.2.0/dist/index.css',
            ],
            setup(picker) {
                picker.on('select', event => {
                    instance.dateRangeSelected(
                        DateTime.fromJSDate(event.detail.start), DateTime.fromJSDate(event.detail.end));
                });
            },
            lang: 'el-GR',
            plugins: [LockPlugin, RangePlugin],
            RangePlugin: {
                startDate: startDate.toISODate(),
                endDate: maxDate.toISODate()
            },
            LockPlugin: {
                minDate: minDate.toISODate(),
                maxDate: maxDate.toISODate()
            },
        });
    };

    /**
     * Initialize the daily country chart.
     *
     * @returns The chart.
     */
    initializeDailyCountryDataChart() {
        return new Chart(document.getElementById('chart').getContext('2d'), {
            type: 'line'
        });
    };

    /**
     * Initialize the fuel types selector.
     */
    initializeLatestCountryDataTable() {
        const table = document.getElementById('latest-prices');
        const tableBody = table.querySelector('table tbody');
        Object.keys(FuelType).forEach(fuelType => {
            const rowElement = document.createElement('tr');
            rowElement.classList.add(fuelType);
            rowElement.innerHTML = `
                <td>${FuelType[fuelType].label}</td>
                <td class="price">&nbsp;</td>
                <td class="evolution">&nbsp;</td>
            `;
            tableBody.append(rowElement);
        });

        return table;
    };

    /**
     * Initialize the latest prefecture data table.
     */
    initializePrefectureDataTable() {
        const table = document.getElementById('prices-per-prefecture');
        const tableHeader = table.querySelector('thead tr');
        Object.keys(FuelType).forEach(fuelType => {
            const header = document.createElement('th');
            header.className = fuelType;
            header.innerHTML = FuelType[fuelType].label;
            tableHeader.append(header);
        });
        const tableBody = table.querySelector('tbody');
        Object.keys(Prefecture).sort((a, b) => {
            return Prefecture[a].localeCompare(Prefecture[b]);
        }).forEach(prefecture => {
            const row = document.createElement('tr');
            row.id = prefecture;
            let cell = document.createElement('td');
            cell.innerHTML = Prefecture[prefecture];
            row.append(cell);
            Object.keys(FuelType).forEach(fuelType => {
                let cell = document.createElement('td');
                cell.classList.add(fuelType);
                row.append(cell);
            });
            tableBody.append(row);
        });

        return table;
    };

    /**
     * Called when a date range is selected.
     *
     * @param startDate {DateTime} The start date.
     * @param endDate {DateTime} The end date.
     */
    dateRangeSelected(startDate, endDate) {
        const instance = this;
        API.dailyCountryData(startDate, endDate).then(response => {
            response.json().then(data => {
                instance.dailyCountryData = data;
                document.querySelectorAll('.latest-date').forEach(span => {
                    span.innerHTML = endDate.toLocaleString();
                });
                this.loadFuelTypesSelector()
                this.loadLatestCountryDataTable();
                this.loadDailyCountryDataChart();
                this.fuelTypeSelectionChanged();
            }).then(() => {
                API.countryData(endDate).then(response => {
                    response.json().then(data => {
                        instance.countryData = data;
                        instance.loadPrefectureDataTable();
                    });
                });
            });
        });
    }

    /**
     * Load the fuel types selector.
     */
    loadFuelTypesSelector() {
        // Get the available fuel types
        const fuelTypes = new Set();
        this.dailyCountryData.forEach(dataRow => {
            dataRow.data.forEach(dataDateRow => {
                fuelTypes.add(dataDateRow['fuel_type']);
            });
        });
        // Set the state of the selector
        const fuelTypesSelector = document.getElementById('fuel-types');
        Object.keys(FuelType).forEach(fuelType => {
            const fuelTypeInput = fuelTypesSelector.querySelector(`#${fuelType}-selector`);
            if (fuelTypes.has(fuelType)) {
                fuelTypeInput.disabled = false;
            } else {
                fuelTypeInput.disabled = true;
                fuelTypeInput.checked = false;
            }
        });
    };

    /**
     * Load the latest country data table.
     */
    loadLatestCountryDataTable() {
        const latestData = this.dailyCountryData.at(-1);
        const previousData = this.dailyCountryData.at(-2);
        Object.keys(FuelType).forEach(fuelType => {
            const fuelDataRow = this.latestCountryDataTable.querySelector(`tr.${fuelType}`);
            const fuelData = latestData.data.find(e => e['fuel_type'] === fuelType);
            fuelDataRow.querySelector('td.price').innerHTML = formatPrice(fuelData?.price);
            fuelDataRow.querySelector('td.evolution').innerHTML = formatEvolution(
                fuelData?.price, previousData?.data.find(e => e['fuel_type'] === fuelType)?.price);
        });
    };

    /**
     * Load the latest country data chart.
     */
    loadDailyCountryDataChart() {
        const instance = this;
        const datasets = []
        Object.keys(FuelType).forEach(fuelType => {
            const fuelTypeData = [];
            const fuelTypeInput = instance.fuelTypeSelector.querySelector(`#${fuelType}-selector`);
            instance.dailyCountryData.forEach(row => {
                fuelTypeData.push(row['data'].find(e => e['fuel_type'] === fuelType)?.price);
            });
            datasets.push({
                label: FuelType[fuelType].label,
                borderColor: FuelType[fuelType].borderColor,
                hidden: !fuelTypeInput.checked,
                data: fuelTypeData,
            });
        });
        this.dailyCountryDataChart.data = {
            labels: instance.dailyCountryData.map(e => e['date']),
            datasets: datasets
        };
    };

    /**
     * Load the prefecture data table.
     */
    loadPrefectureDataTable() {
        const instance = this;
        Object.keys(Prefecture).forEach(prefecture => {
            const prefectureRow = instance.prefectureDataTable.querySelector(`tr#${prefecture}`);
            const prefectureData = this.countryData['prefectures'].find(e => e['prefecture'] === prefecture)?.data;
            Object.keys(FuelType).forEach(fuelType => {
                prefectureRow.querySelector(`.${fuelType}`).textContent = formatPrice(
                    prefectureData.find(e => e['fuel_type'] === fuelType)?.price);
            });
        });
    };

    /**
     * Called when the fuel type selection has changed.
     */
    fuelTypeSelectionChanged() {
        const instance = this;
        Object.keys(FuelType).forEach(fuelType => {
            const fuelTypeInput = instance.fuelTypeSelector.querySelector(`#${fuelType}-selector`);
            const latestCountryDataFuelDataRow = this.latestCountryDataTable.querySelector(`tr.${fuelType}`);
            latestCountryDataFuelDataRow.style.display = fuelTypeInput.checked ? '' : 'none';
            instance.prefectureDataTable.querySelectorAll(`.${fuelType}`).forEach(element => {
                element.style.display = fuelTypeInput.checked ? '' : 'none';
            });
            const fuelTypeDataset = this.dailyCountryDataChart.data.datasets.find(
                e => e.label === FuelType[fuelType].label);
            if (fuelTypeDataset) {
                fuelTypeDataset.hidden = !fuelTypeInput.checked;
            }
        });
        this.dailyCountryDataChart.update();
    };
}

new Main();
