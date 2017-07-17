function format_uah(value) {
    return accounting.formatMoney(value, "₴", 2);
}

function format_sqm(value) {
    return accounting.formatMoney(value, {symbol: "м²",  format: "%v %s"}, 2 )
}

function incomes() {
    var ctx = document.getElementById("decl_incomes").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.incomes_data,
        options: {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: {
                display: true,
                text: 'Дохід декларанта, родини та загальна сума подарунків',
                fontSize: 30
            },
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_uah(tooltipItem.yLabel);
                    }
                }
            },
            responsive: true,
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
        }
    });
}

function assets() {
    var ctx = document.getElementById("decl_assets").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.assets_data,
        options: {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: {
                display: true,
                text: 'Грошові активи декларанта, родини та загальна сума готівки',
                fontSize: 30
            },
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_uah(tooltipItem.yLabel);
                    }
                }
            },
            responsive: true,
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
        }
    });
}

function global_picture() {
    var ctx = document.getElementById("decl_global").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.incomes_vs_expenses_data,
        options: {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: {
                display: true,
                text: "Доходи та грошові активи VS витрати та зобов'язання",
                fontSize: 30
            },
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_uah(Math.abs(tooltipItem.yLabel));
                    }
                }
            },
            responsive: true,
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
        }
    });
}

function land() {
    var ctx = document.getElementById("decl_land").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.land_data,
        options: {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: {
                display: true,
                text: "Земельні ділянки (м²)",
                fontSize: 30
            },
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_sqm(tooltipItem.yLabel);
                    }
                }
            },
            responsive: true,
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
        }
    });
}

function realty() {
    var ctx = document.getElementById("decl_realty").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.realty_data,
        options: {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: {
                display: true,
                text: "Квартири, будинки, та інша нерухомість (м²)",
                fontSize: 30
            },
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, data) {
                        return format_sqm(tooltipItem.yLabel);
                    }
                }
            },
            responsive: true,
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
        }
    });
}

function cars() {
    var ctx = document.getElementById("decl_cars").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.cars_data,
        options: {
            onClick: function() {
                if (this.tooltip._lastActive.length > 0) {
                    window.open(
                        urls[this.tooltip._lastActive[0]._index],
                        this.tooltip._lastActive[0]._index + ""
                    );
                };
            },
            title: {
                display: true,
                text: "Машини та інші транспортні засоби",
                fontSize: 30
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            responsive: true,
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    stacked: true,
                }]
            }
        }
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