function makechart1() {
    var ctx = document.getElementById("declRelatives").getContext("2d");

    window.incomeBars = new Chart(ctx, {
        type: 'bar',
        data: window.chart1,
        options: {
            title:{
                //display:true,
                //text: 'Родственники'
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
                    stacked: true
                }]
            }
        }
    });
}

function makechart2() {
    var ctx = document.getElementById("declLand").getContext("2d"),
        jUrl = $('#declLand').data('jurl');

    $.getJSON(jUrl, function(data) {
        var barChartData = data;

        window.myBar = new Chart(ctx, {
            type: 'line',
            data: barChartData,
            options: {
                responsive: true,
                title:{
                    //display:true,
                    //text:"Объекты недвижимости декларанта и родственников."
                },
                tooltips: {
                    mode: 'index'
                },
                hover: {
                    mode: 'index'
                },
                scales: {
                    xAxes: [{
                        scaleLabel: {
                            display: true
                        }
                    }],
                    yAxes: [{
                        stacked: false,
                        scaleLabel: {
                            display: true
                        }
                    }]
                }
            }
        });
    });
}


function makechart3() {
    var ctx = document.getElementById("declAutoMotive").getContext("2d"),
        jUrl = $('#declAutoMotive').data('jurl');

    $.getJSON(jUrl, function(data) {
        var barChartData = data;

        window.myBar = new Chart(ctx, {
            type: 'bar',
            data: barChartData,
            options: {
                title:{
                    //display:false,
                    //text: 'ЦІННЕ РУХОМЕ МАЙНО - ТРАНСПОРТНІ ЗАСОБИ'
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

                        ticks: {
                            min: 0,
                            stepSize: 1
                        }
                    }]
                }
            }
        });
    });
}

$( document ).ready(function() {
    makechart1();
    // makechart2();
    // makechart3();
});