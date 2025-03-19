document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    const cacheHitCtx = document.getElementById('cacheHitChart').getContext('2d');
    const responseTimeCtx = document.getElementById('responseTimeChart').getContext('2d');
    
    const cacheHitChart = new Chart(cacheHitCtx, {
        type: 'pie',
        data: {
            labels: ['Cache Hits', 'Cache Misses'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['#28a745', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Cache Hit Rate'
                }
            }
        }
    });
    
    const responseTimeChart = new Chart(responseTimeCtx, {
        type: 'bar',
        data: {
            labels: ['With Cache', 'Without Cache'],
            datasets: [{
                label: 'Avg Response Time (s)',
                data: [0, 0],
                backgroundColor: ['#007bff', '#6c757d']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Response Time Comparison'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // Query history
    const queryHistory = [];
    
    // Submit query
    document.getElementById('submitQuery').addEventListener('click', function() {
        const query = document.getElementById('queryInput').value.trim();
        const useCache = document.getElementById('useCache').checked;
        
        if (!query) {
            alert('Please enter a question');
            return;
        }
        
        // Show loading state
        document.getElementById('responseContainer').innerHTML = '<p>Loading response...</p>';
        document.getElementById('responseMetadata').innerHTML = '';
        
        // Send query to backend
        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                use_cache: useCache
            })
        })
        .then(response => response.json())
        .then(data => {
            // Update response
            const result = data.result;
            const metrics = data.metrics;
            
            document.getElementById('responseContainer').innerHTML = `
                <p>${result.response}</p>
            `;
            
            document.getElementById('responseMetadata').innerHTML = `
                <p>
                    <span class="${result.used_cache ? 'cache-hit' : 'cache-miss'}">
                        ${result.used_cache ? 'Used cache' : 'No cache used'}
                    </span> | 
                    <span class="response-time">Response time: ${result.response_time.toFixed(2)}s</span>
                    ${result.topics_used.length > 0 ? ' | Topics: ' + result.topics_used.join(', ') : ''}
                </p>
            `;
            
            // Add to history
            queryHistory.unshift(result);
            updateQueryHistory();
            
            // Update charts and metrics
            updateCharts(metrics);
            updateMetricsTable(metrics);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('responseContainer').innerHTML = `
                <p class="text-danger">Error: Could not get response. Please try again.</p>
            `;
        });
    });
    
    // Allow pressing Enter to submit
    document.getElementById('queryInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('submitQuery').click();
        }
    });
    
    // Update query history table
    function updateQueryHistory() {
        const historyTable = document.getElementById('historyTable');
        historyTable.innerHTML = '';
        
        queryHistory.slice(0, 10).forEach(item => {
            const row = document.createElement('tr');
            row.className = 'query-history-item';
            row.innerHTML = `
                <td>${item.query}</td>
                <td><span class="${item.used_cache ? 'cache-hit' : 'cache-miss'}">${item.used_cache ? 'Yes' : 'No'}</span></td>
                <td>${item.response_time.toFixed(2)}s</td>
                <td>${item.topics_used.length > 0 ? item.topics_used.join(', ') : 'N/A'}</td>
            `;
            
            // Click to reuse query
            row.addEventListener('click', function() {
                document.getElementById('queryInput').value = item.query;
            });
            
            historyTable.appendChild(row);
        });
    }
    
    // Update charts with new metrics
    function updateCharts(metrics) {
        // Update cache hit chart
        cacheHitChart.data.datasets[0].data = [
            metrics.cache_hits,
            metrics.cache_misses
        ];
        cacheHitChart.update();
        
        // Update response time chart
        responseTimeChart.data.datasets[0].data = [
            metrics.avg_response_time_with_cache || 0,
            metrics.avg_response_time_without_cache || 0
        ];
        responseTimeChart.update();
    }
    
    // Update metrics table
    function updateMetricsTable(metrics) {
        const metricsTable = document.getElementById('metricsTable');
        metricsTable.innerHTML = '';
        
        const formattedMetrics = [
            { name: 'Cache Hit Rate', value: `${((metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses)) * 100 || 0).toFixed(1)}%` },
            { name: 'Avg Response Time (With Cache)', value: `${metrics.avg_response_time_with_cache?.toFixed(2) || 0}s` },
            { name: 'Avg Response Time (Without Cache)', value: `${metrics.avg_response_time_without_cache?.toFixed(2) || 0}s` },
            { name: 'Time Saved', value: `${((metrics.avg_response_time_without_cache - metrics.avg_response_time_with_cache) * metrics.cache_hits || 0).toFixed(2)}s` }
        ];
        
        formattedMetrics.forEach(metric => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${metric.name}</td>
                <td>${metric.value}</td>
            `;
            metricsTable.appendChild(row);
        });
    }
    
    // Initial fetch of metrics
    fetch('/api/metrics')
        .then(response => response.json())
        .then(metrics => {
            updateCharts(metrics);
            updateMetricsTable(metrics);
        });
}); 