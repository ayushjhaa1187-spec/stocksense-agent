document.addEventListener("DOMContentLoaded", function() {
    refreshData();
});

function refreshData() {
    const loadingSpinner = document.getElementById('loading-spinner');
    const content = document.getElementById('dashboard-content');

    // Show spinner, hide content
    loadingSpinner.style.display = 'flex';
    content.style.display = 'none';

    fetch('/api/recommendations')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error fetching data:", data.error);
                alert("Failed to load data: " + data.error);
                loadingSpinner.style.display = 'none';
                return;
            }

            // Update timestamp
            const date = new Date(data.timestamp);
            document.getElementById('last-scan-time').textContent = date.toLocaleTimeString();

            // Stats Counters with Animation
            animateValue("expiry-count", 0, data.expiry_alerts.length, 1000);
            animateValue("discount-count", 0, data.discount_recommendations.length, 1000);
            animateValue("restock-count", 0, data.restock_orders.length, 1000);

            // Populate Expiry Table
            const expiryTable = document.getElementById('expiry-table').getElementsByTagName('tbody')[0];
            expiryTable.innerHTML = ''; // Clear existing

            if (data.expiry_alerts.length === 0) {
                expiryTable.innerHTML = '<tr><td colspan="5" class="text-center py-3 text-muted">No critical expiries found.</td></tr>';
            } else {
                data.expiry_alerts.forEach(item => {
                    let row = expiryTable.insertRow();
                    let urgencyClass = item.urgency === 'CRITICAL' ? 'bg-danger text-white' : 'bg-warning text-dark';

                    row.innerHTML = `
                        <td class="fw-bold">${item.medicine}</td>
                        <td><span class="badge ${item.days_left <= 7 ? 'bg-danger' : 'bg-warning'}">${item.days_left} days</span></td>
                        <td>${item.stock} units</td>
                        <td>${item.urgency}</td>
                        <td><button class="btn btn-sm btn-outline-light">Details</button></td>
                    `;
                });
            }

            // Populate Discount Table
            const discountTable = document.getElementById('discount-table').getElementsByTagName('tbody')[0];
            discountTable.innerHTML = '';

            if (data.discount_recommendations.length === 0) {
                discountTable.innerHTML = '<tr><td colspan="4" class="text-center py-3 text-muted">No discounts needed.</td></tr>';
            } else {
                data.discount_recommendations.forEach(item => {
                    let row = discountTable.insertRow();
                    row.innerHTML = `
                        <td>${item.medicine}</td>
                        <td class="text-success fw-bold">-${item.discount_percent}%</td>
                        <td>${item.expected_clear_pct}%</td>
                        <td>₹${item.revenue_recovery}</td>
                    `;
                });
            }

            // Populate Restock Table
            const restockTable = document.getElementById('restock-table').getElementsByTagName('tbody')[0];
            restockTable.innerHTML = '';

            if (data.restock_orders.length === 0) {
                restockTable.innerHTML = '<tr><td colspan="4" class="text-center py-3 text-muted">Stock levels healthy.</td></tr>';
            } else {
                data.restock_orders.forEach(item => {
                    let row = restockTable.insertRow();
                    row.innerHTML = `
                        <td>${item.medicine}</td>
                        <td>${item.recommended_qty}</td>
                        <td><small class="text-muted">${item.supplier}</small></td>
                        <td>₹${item.estimated_cost}</td>
                    `;
                });
            }

            // Hide spinner, show content
            loadingSpinner.style.display = 'none';
            content.style.display = 'block';
            content.classList.add('fade-in');
        })
        .catch(error => {
            console.error("Error:", error);
            loadingSpinner.style.display = 'none';
            alert("Network error. Please try again.");
        });
}

function animateValue(id, start, end, duration) {
    if (start === end) return;
    var range = end - start;
    var current = start;
    var increment = end > start? 1 : -1;
    var stepTime = Math.abs(Math.floor(duration / range));
    var obj = document.getElementById(id);
    var timer = setInterval(function() {
        current += increment;
        obj.innerHTML = current;
        if (current == end) {
            clearInterval(timer);
        }
    }, stepTime);
}
