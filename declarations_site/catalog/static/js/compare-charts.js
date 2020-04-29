function format_uah(value) {
    return accounting.formatMoney(value, "₴", 2);
}

function format_sqm(value) {
    return accounting.formatMoney(value, {symbol: "м²",  format: "%v %s"}, 2 )
}

var options = {
    title: {
        display: true,
        fontColor: '#111',
        fontSize: 20
    },
    legend: {
        labels: {
            boxWidth: 20,
            fontSize: 14,
            fontColor: '#111',
            fontWeight: 600,
        },
    },
    responsive: true,
}


function incomes() {
    var ctx = document.getElementById("decl_incomes").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.incomes_data,
        options: Object.assign({}, options, {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: Object.assign({}, options.title, {
                text: $('#decl_inc').data('caption'),
            }),
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_uah(tooltipItem.yLabel);
                    }
                }
            },
            scales: {
                xAxes: [{
                    stacked: true,
                    
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        callback: function(value, index, values) {
                            return format_uah(value);
                        }
                    }
                }]
            }
        })
    });
}

function assets() {
    var ctx = document.getElementById("decl_assets").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.assets_data,
        options: Object.assign({}, options, {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: Object.assign({}, options.title, {
                text: $('#decl_assets').data('caption'),
            }),
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_uah(tooltipItem.yLabel);
                    }
                }
            },
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        callback: function(value, index, values) {
                            return format_uah(value);
                        }
                    }
                }]
            }
        })
    });
}

function global_picture() {
    var ctx = document.getElementById("decl_global").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.incomes_vs_expenses_data,
        options: Object.assign({}, options, {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: Object.assign({}, options.title, {
                text: $('#decl_global').data('caption'),
            }),
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_uah(Math.abs(tooltipItem.yLabel));
                    }
                }
            },
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        callback: function(value, index, values) {
                            return format_uah(value);
                        }
                    }
                }]
            }
        })
    });
}

function land() {
    var ctx = document.getElementById("decl_land").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.land_data,
        options: Object.assign({}, options, {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: Object.assign({}, options.title, {
                text: $('#decl_land').data('caption'),
            }),
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_sqm(tooltipItem.yLabel);
                    }
                }
            },
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        callback: function(value, index, values) {
                            return format_sqm(value);
                        }
                    }
                }]
            }
        })
    });
}

function realty() {
    var ctx = document.getElementById("decl_realty").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.realty_data,
        options: Object.assign({}, options, {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: Object.assign({}, options.title, {
                text: $('#decl_realty').data('caption'),
            }),
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_sqm(tooltipItem.yLabel);
                    }
                }
            },
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        callback: function(value, index, values) {
                            return format_sqm(value);
                        }
                    }
                }]
            }
        })
    });
}

function cars() {
    var ctx = document.getElementById("decl_cars").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.cars_data,
        options: Object.assign({}, options, {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: Object.assign({}, options.title, {
                text: $('#decl_cars').data('caption'),
            }),
            tooltips: {
                mode: 'index',
                intersect: false
            },
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    stacked: true,
                }]
            }
        })
    });
}

$(function() {
    global_picture();
    incomes();
    assets();
    land();
    realty();
    cars();
});
