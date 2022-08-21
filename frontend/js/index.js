const loadData = async () => {
  const response = await fetch('http://localhost:8000/data/dailyCountry');
  return await response.json()
}

loadData().then(data => {
  let dates = [];
  let prices = [];
  for (const row of data) {
    dates.push(row['date']);
    let price = null;
    for (const result of row['results']) {
      if (result['fuel_type'] === 'UNLEADED_95') {
        price = result['price'];
        break;
      }
    }
    prices.push(price);
  }
  const chartData = {
    labels: dates,
    datasets: [{
      label: 'Unleaded 95',
      data: prices,
      borderColor: 'rgb(75, 192, 192)',
    }]
  };
  const config = {
    type: 'line',
    data: chartData,
  };
  const ctx = document.getElementById('chart').getContext('2d');
  new Chart(ctx, config);
});

