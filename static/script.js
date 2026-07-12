document.addEventListener('DOMContentLoaded', () => {
    let flightData = [];
    let currentSortColumn = 'Price_INR';
    let sortAscending = true;

    // DOM Elements
    const tableBody = document.getElementById('flights-body');
    const searchInput = document.getElementById('search-input');
    const fileBadge = document.getElementById('file-used-badge');
    const statsContainer = document.getElementById('stats-container');
    const tableHeaders = document.querySelectorAll('th[data-sort]');

    // Fetch data from Flask API
    fetch('/api/flights')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                flightData = data.data;
                fileBadge.textContent = `Data Source: ${data.file_used}`;
                document.getElementById('target-badge').textContent = `Target: ${data.search_target}`;
                
                renderStats(flightData);
                renderTable(flightData);
            } else {
                tableBody.innerHTML = `<tr><td colspan="5" style="color: #ef4444; text-align: center;">${data.error}</td></tr>`;
            }
        })
        .catch(error => {
            console.error('Error fetching flights:', error);
            tableBody.innerHTML = `<tr><td colspan="5" style="color: #ef4444; text-align: center;">Failed to connect to backend API.</td></tr>`;
        });

    // Render Summary Stats
    function renderStats(data) {
        if (data.length === 0) return;

        const minPrice = Math.min(...data.map(d => d.Price_INR));
        const avgPrice = data.reduce((acc, curr) => acc + curr.Price_INR, 0) / data.length;
        
        // Count destinations
        const destinations = new Set(data.map(d => d.Destination_IATA));

        statsContainer.innerHTML = `
            <div class="card">
                <h3>Total Flights Found</h3>
                <div class="value">${data.length}</div>
            </div>
            <div class="card">
                <h3>Cheapest Flight</h3>
                <div class="value">₹${minPrice.toLocaleString('en-IN')}</div>
            </div>
            <div class="card">
                <h3>Average Price</h3>
                <div class="value">₹${Math.round(avgPrice).toLocaleString('en-IN')}</div>
            </div>
            <div class="card">
                <h3>Destinations</h3>
                <div class="value">${destinations.size}</div>
            </div>
        `;
    }

    // Render Table
    function renderTable(data) {
        tableBody.innerHTML = '';

        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No flights match your search.</td></tr>';
            return;
        }

        data.forEach(flight => {
            const tr = document.createElement('tr');
            
            // Format price
            const price = flight.Price_INR.toLocaleString('en-IN');
            
            tr.innerHTML = `
                <td>${flight.Date} <br><small style="color:var(--text-muted)">${flight.Day_of_Week}</small></td>
                <td><strong>${flight.Destination_IATA}</strong> <br><small style="color:var(--text-muted)">${flight.Destination_Name}</small></td>
                <td>${flight.Airline}</td>
                <td>${flight.Flight_Type}</td>
                <td style="color: #10b981; font-weight: 600;">₹${price}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Search Filtering
    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = flightData.filter(f => 
            f.Destination_IATA.toLowerCase().includes(term) ||
            f.Destination_Name.toLowerCase().includes(term) ||
            f.Airline.toLowerCase().includes(term)
        );
        renderTable(filtered);
    });

    // Sorting
    tableHeaders.forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;
            
            if (currentSortColumn === column) {
                sortAscending = !sortAscending;
            } else {
                currentSortColumn = column;
                sortAscending = true;
            }

            // Update arrow UI
            tableHeaders.forEach(header => header.querySelector('span').textContent = '↕');
            th.querySelector('span').textContent = sortAscending ? '↑' : '↓';

            // Sort data
            const sortedData = [...flightData].sort((a, b) => {
                let valA = a[column];
                let valB = b[column];

                if (typeof valA === 'string') {
                    return sortAscending ? valA.localeCompare(valB) : valB.localeCompare(valA);
                } else {
                    return sortAscending ? valA - valB : valB - valA;
                }
            });

            // Re-apply search filter if any
            const term = searchInput.value.toLowerCase();
            const filtered = sortedData.filter(f => 
                f.Destination_IATA.toLowerCase().includes(term) ||
                f.Destination_Name.toLowerCase().includes(term) ||
                f.Airline.toLowerCase().includes(term)
            );

            renderTable(filtered);
        });
    });
});
