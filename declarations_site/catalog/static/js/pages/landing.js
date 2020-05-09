(function($) {
  function format_uah(value) {
    return accounting.formatMoney(value, "₴", 2);
  }

  function format_sqm(value) {
    return accounting.formatMoney(value, {symbol: "м²",  format: "%v %s"}, 2 )
  }

  $(function() {
    var all_data, chart;

    var customTooltips = function(tooltip) {
      var this_chart = this;
      $(this._chart.canvas).css('cursor', 'pointer');

      var positionY = this._chart.canvas.offsetTop;
      var positionX = this._chart.canvas.offsetLeft;

      $('.chartjs-tooltip').css({
        opacity: 0,
      });

      if (!tooltip || !tooltip.opacity) {
        return;
      }

      if (tooltip.dataPoints.length > 0) {
        tooltip.dataPoints.forEach(function(dataPoint) {
          var point = this_chart._data.datasets[dataPoint.datasetIndex].data[dataPoint.index];
          var content = [dataPoint.xLabel, dataPoint.yLabel].join(': ');
          var $tooltip = $('#main-tooltip');

          $tooltip.find(".chartjs-tooltip__name .value").html(point.name);
          $tooltip.find(".chartjs-tooltip__income .value").html(format_uah(point.income));
          $tooltip.find(".chartjs-tooltip__cash .value").html(format_uah(point.cash));
          $tooltip.find(".chartjs-tooltip__liabilities .value").html(format_uah(point.liabilities));
          $tooltip.find(".chartjs-tooltip__expenses .value").html(format_uah(point.expenses));
          $tooltip.find(".chartjs-tooltip__land .value").html(format_sqm(point.land));
          $tooltip.find(".chartjs-tooltip__real_estate .value").html(format_sqm(point.real_estate));
          $tooltip.find(".chartjs-tooltip__assets .value").html(format_uah(point.assets));

          $tooltip.css({
            opacity: 1,
            top: positionY + dataPoint.y + 'px',
            left: positionX + dataPoint.x + 'px',
          });
        });
      }
    };

    function build_main_chart() {
      var year = parseInt($("#year").val());
      var data = [],
        param_x = {
          "name": "incomes.declarant",
          "title": "Дохід декларанта"
        },
        param_y = {
          "name": "incomes.family",
          "title": "Дохід родини"
        },
        param_r = {
          "name": "assets.total",
          "title": "Статки"
        },

        max_r = 0,
        max_estate = 0,
        options = {
          legend: false,
          scales: {
            xAxes: [{
              scaleLabel: {
                display: true,
                labelString: param_x.title,
                fontColor: "#5ECBA1",
                fontSize: 14,
                fontStyle: "bold",
              },
              ticks: {
                fontColor: "#5ECBA1",
                fontSize: 14,
                fontStyle: "bold",
                // Include a dollar sign in the ticks
                callback: function(value, index, values) {
                  return format_uah(value);
                }
              }
            }],
            yAxes: [{
              scaleLabel: {
                fontColor: "#7175D8",
                fontStyle: "bold",
                fontSize: 14,
                display: true,
                labelString: param_y.title,
              },
              ticks: {
                fontColor: "#7175D8",
                fontSize: 14,
                fontStyle: "bold",
                // Include a dollar sign in the ticks
                callback: function(value, index, values) {
                    return format_uah(value);
                }
              }
            }]
          },
          tooltips: {
            mode: 'index',
            intersect: true,
            custom: customTooltips,
            enabled: false,

            callbacks: {
              label: function(tooltipItem, data) {
                var point = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                return (point.label || '');
              },

              afterLabel: function(tooltipItem, data) {
                var point = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                return [
                  param_x.title + ": " + format_uah(point.x),
                  param_y.title + ": " + format_uah(point.y),
                  param_r.title + ": " + format_uah(point.v),
                  "Прапорці: " + point.flags,
                  "Загальна площа нерухомості: " + point.estate
                ];
              }
            }
          },

          elements: {
            point: {
              backgroundColor: function(context) {
                var value = context.dataset.data[context.dataIndex],
                    level = value.scaled_estate,
                    r = Math.round(255 * (1 - level) + 113 * level),
                    g = Math.round(255 * (1 - level) + 118 * level),
                    b = Math.round(255 * (1 - level) + 216 * level);
                return 'rgba(' + r + ',' + g + ',' + b + ',0.7)';
              },

              borderWidth: function(context) {
                var value = context.dataset.data[context.dataIndex];
                if (value.flags) {
                  return Math.min(value.flags / 3 + 0.5, 3);
                }
                return 1
              },

              hoverBackgroundColor: 'transparent',

              borderColor: function(context) {
                var value = context.dataset.data[context.dataIndex];
                if (value.flags) {
                  return "#FF6B69";
                }
              },

              radius: function(context) {
                var value = context.dataset.data[context.dataIndex],
                  size = context.chart.width;
                return 5 + (size / 20) * value.scaled_r;
              }
            }
          }
        };

      for (var i = 0; i < all_data["persons"].length; i++) {
        var docs = all_data["persons"][i]["documents"];
        for (var curr_year in docs) {
          if (curr_year != year)
            continue;

          var doc = docs[curr_year],
            x = doc["aggregated_data"][param_x.name],
            y = doc["aggregated_data"][param_y.name],
            r = doc["aggregated_data"][param_r.name],
            estate = doc["aggregated_data"]["estate.total_other"];

          if (r > max_r) {
            max_r = r;
          }

          if (estate > max_estate) {
            max_estate = estate;
          }

          data.push({
            "id": all_data["persons"][i]["id"],
            "name": all_data["persons"][i]["name"],
            "income": doc["aggregated_data"]["incomes.total"],
            "cash": doc["aggregated_data"]["assets.cash.total"],
            "liabilities": doc["aggregated_data"]["liabilities.total"],
            "expenses": doc["aggregated_data"]["expenses.total"],
            "land": doc["aggregated_data"]["estate.total_land"],
            "real_estate": doc["aggregated_data"]["estate.total_other"],
            "assets": doc["aggregated_data"]["assets.total"],
            "x": x,
            "y": y,
            "v": r,
            "flags": doc["flags"].length,
            "estate": estate,
          });
        }
      }

      for (var i = 0; i < data.length; i++) {
        data[i]["scaled_r"] = (data[i]["v"] + 0.1) / (max_r + 0.1);
        data[i]["scaled_estate"] = (Math.min(data[i]["estate"], 500) + 0.1) / (500 + 0.1);
      }

      if (typeof(chart) === "undefined") {
        chart = new Chart('tablo', {
          type: 'bubble',
          data: {
            datasets: [{
              "data": data
            }]
          },
          options: options
        });
      } else {
        chart.data.datasets = [{"data": data}];
        chart.update();
      }
    };

    $.getJSON("?format=json", function(data) {
      all_data = data;
      build_main_chart();
    });

    $('#year')
      .on('change', function() {
        build_main_chart();
      })
      .on('change', function() {
        $('.landing-page__declarants-table')
          .hide()
          .filter('#declarants-' + $(this).val())
          .show();
      });

    $(document.body).on("tooltip-shown", function(e) {
      var anchor = $(e.target),
        tooltip = anchor.find(".n-tooltip__body"),
        canvas = tooltip.html("<canvas>").find("canvas"),
        config = {
          type: 'line',
          data: {
            labels: anchor.data("labels"),
            datasets: [{
              label: anchor.data("family_label"),
              backgroundColor: "#7175D8",
              borderColor: "#7175D8",
              data: anchor.data("family_values"),
              fill: true,
            }, {
              label: anchor.data("declarant_label"),
              backgroundColor: "#5ECBA1",
              borderColor: "#5ECBA1",
              data: anchor.data("declarant_values"),
              fill: true,
            }]
          },
          options: {
            responsive: true,
            legend: {
              display: true,
              position: "right",
              labels: {
                boxWidth: 10,
                fontSize: 10
              }
            },
            tooltips: {
              mode: 'index',
              intersect: false,
            },
            hover: {
              mode: 'nearest',
              intersect: true
            },
            scales: {
              xAxes: [{
                display: true,
              }],
              yAxes: [{
                stacked: true,
                display: true,
              }]
            }
          }
        },
        chart = new Chart(canvas, config);
    });

    $("#sort").on("change", function(){
      var order = $(this).val();

      $(".landing-page__declarants-table").each(function(i, table) {
        table = $(table);
        var items = table.find('tbody tr');

        items.sort(function(a, b) {
          switch (order) {
            case "assets":
            case "flags":
              return parseFloat($(b).data(order)) - parseFloat($(a).data(order));
            case "name":
              return $(a).data(order).localeCompare($(b).data(order));
            break;
          }
        });

        items.appendTo(table.find("tbody"));
      });
    }).change();
  });
})(jQuery);
