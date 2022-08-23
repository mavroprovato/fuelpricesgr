const loadData = async () => {
    const response = await fetch('http://localhost:8000/data/dailyCountry');
    return await response.json()
}

const FuelType = {
    UNLEADED_95: {
        label: "Αμόλυβδη 95",
        borderColor: 'rgb(64, 83, 211)'
    },
    UNLEADED_100: {
        label: 'Αμόλυβδη 100',
        borderColor: 'rgb(211, 179, 16)'
    },
    SUPER: {
        label: "Super",
        borderColor: 'rgb(181, 29, 20)'
    },
    DIESEL: {
        label: "Diesel",
        borderColor: 'rgb(0, 190, 255)'
    },
    DIESEL_HEATING: {
        label: "Diesel Θέρμανσης",
        borderColor: 'rgb(251, 73, 176)'
    },
    GAS: {
        label: "Υγραέριο",
        borderColor: 'rgb(0, 178, 93)'
    }
}

loadData().then(data => {
    const dates = [];
    const prices = {};
    for (const fuelType in FuelType) {
        prices[fuelType] = [];
    }
    for (const row of data) {
        dates.push(row['date']);
        for (const fuelType in FuelType) {
            prices[fuelType].push(null);
        }
        for (const result of row['results']) {
            prices[result['fuel_type']][prices[result['fuel_type']].length - 1] = result['price'];
        }
    }
    const datasets = []
    for (const fuelType in FuelType) {
        datasets.push({
            label: FuelType[fuelType].label,
            data: prices[fuelType],
            borderColor:  FuelType[fuelType].borderColor
        })
    }
    const chartData = {
        labels: dates,
        datasets: datasets
    };
    const config = {
        type: 'line',
        data: chartData,
    };
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, config);
});

