/**
 * FinnCharts - Shared chart factory module for Finn Investment Tracker.
 * Uses ApexCharts. All formatters and configs defined once (DRY).
 */
var FinnCharts = {
    // Reusable formatters
    formatRM: function(val) { return 'RM ' + val.toLocaleString(); },
    formatPct: function(val) { return val.toFixed(2) + '%'; },
    formatPctInt: function(val) { return val.toFixed(0) + '%'; },
    formatPct1: function(val) { return val.toFixed(1) + '%'; },

    // Shared colors
    colors: {
        success: '#198754',
        danger: '#dc3545',
        primary: '#0d6efd',
        muted: '#6c757d',
        warning: '#ffc107',
        info: '#17a2b8'
    },

    // Empty state helper
    showEmpty: function(selector, message) {
        var el = document.querySelector(selector);
        if (el) {
            el.innerHTML = '<div class="text-center text-muted py-5">' + message + '</div>';
        }
    },

    // Net Worth History - area chart with 3 series
    renderNetWorthHistory: function(selector, data) {
        if (!data || data.length === 0) {
            this.showEmpty(selector, 'No historical data available. Create monthly snapshots to see trends.');
            return;
        }

        var options = {
            series: [
                { name: 'Assets', data: data.map(function(d) { return d.total_assets; }) },
                { name: 'Liabilities', data: data.map(function(d) { return d.total_liabilities; }) },
                { name: 'Net Worth', data: data.map(function(d) { return d.net_worth; }) }
            ],
            chart: { type: 'area', height: 300, toolbar: { show: false } },
            colors: [this.colors.success, this.colors.danger, this.colors.primary],
            dataLabels: { enabled: false },
            stroke: { curve: 'smooth', width: 2 },
            fill: { type: 'gradient', gradient: { opacityFrom: 0.4, opacityTo: 0.1 } },
            xaxis: {
                categories: data.map(function(d) { return d.date; }),
                labels: { rotate: -45 }
            },
            yaxis: { labels: { formatter: this.formatRM } },
            tooltip: { y: { formatter: this.formatRM } }
        };

        new ApexCharts(document.querySelector(selector), options).render();
    },

    // Asset Allocation - donut chart
    renderAllocationPie: function(selector, data) {
        if (!data || data.length === 0) {
            this.showEmpty(selector, 'No assets found. Add assets to see allocation.');
            return;
        }

        var self = this;
        var options = {
            series: data.map(function(d) { return d.total_value; }),
            labels: data.map(function(d) { return d.asset_class_name; }),
            colors: data.map(function(d) { return d.color; }),
            chart: { type: 'donut', height: 300 },
            plotOptions: {
                pie: {
                    donut: {
                        size: '60%',
                        labels: {
                            show: true,
                            total: {
                                show: true,
                                label: 'Total',
                                formatter: function(w) {
                                    return self.formatRM(w.globals.seriesTotals.reduce(function(a, b) { return a + b; }, 0));
                                }
                            }
                        }
                    }
                }
            },
            tooltip: { y: { formatter: this.formatRM } },
            legend: { position: 'bottom' }
        };

        new ApexCharts(document.querySelector(selector), options).render();
    },

    // Actual vs Strategic Allocation - grouped bar chart
    renderAllocationComparison: function(selector, data) {
        if (!data || data.length === 0) {
            this.showEmpty(selector, 'No allocation data available.');
            return;
        }

        var options = {
            series: [
                { name: 'Actual', data: data.map(function(d) { return Math.round(d.percentage * 10) / 10; }) },
                { name: 'Target (SAA)', data: data.map(function(d) { return d.target_percentage; }) }
            ],
            chart: { type: 'bar', height: 300, toolbar: { show: false } },
            colors: [this.colors.primary, this.colors.muted],
            plotOptions: { bar: { horizontal: false, columnWidth: '55%', borderRadius: 4 } },
            dataLabels: { enabled: false },
            xaxis: { categories: data.map(function(d) { return d.asset_class_name; }) },
            yaxis: { labels: { formatter: this.formatPctInt } },
            tooltip: { y: { formatter: this.formatPct1 } }
        };

        new ApexCharts(document.querySelector(selector), options).render();
    },

    // Income Summary - pie chart
    renderIncomeSummary: function(selector, data) {
        if (!data || Object.keys(data).length === 0) {
            this.showEmpty(selector, 'No income recorded. Add dividend or rental income to see summary.');
            return;
        }

        var labels = Object.keys(data).map(function(k) {
            return k.charAt(0).toUpperCase() + k.slice(1);
        });

        var options = {
            series: Object.values(data),
            labels: labels,
            chart: { type: 'pie', height: 300 },
            colors: [this.colors.success, this.colors.primary, this.colors.warning, this.colors.info],
            tooltip: { y: { formatter: this.formatRM } },
            legend: { position: 'bottom' }
        };

        new ApexCharts(document.querySelector(selector), options).render();
    },

    // YTD Cumulative Return - stepline area chart
    renderDailyReturn: function(selector, data) {
        if (!data || data.length <= 1) {
            this.showEmpty(selector, 'No daily performance data. Create multiple snapshots to see cumulative returns.');
            return;
        }

        var options = {
            series: [{ name: 'Cumulative Return', data: data.map(function(d) { return d.cumulative_return; }) }],
            chart: { type: 'area', height: 300, toolbar: { show: false } },
            colors: [this.colors.primary],
            stroke: { curve: 'stepline', width: 2 },
            fill: { type: 'gradient', gradient: { opacityFrom: 0.3, opacityTo: 0.05 } },
            dataLabels: { enabled: false },
            xaxis: {
                categories: data.map(function(d) { return d.date; }),
                type: 'datetime',
                labels: { datetimeUTC: false, format: 'MMM dd' },
                tickAmount: 6
            },
            yaxis: { labels: { formatter: this.formatPct } },
            tooltip: {
                x: { format: 'yyyy-MM-dd' },
                y: { formatter: this.formatPct }
            },
            annotations: {
                yaxis: [{
                    y: 0,
                    borderColor: '#999',
                    strokeDashArray: 4,
                    label: { text: '0%', style: { color: '#999', background: 'transparent' } }
                }]
            }
        };

        new ApexCharts(document.querySelector(selector), options).render();
    }
};
