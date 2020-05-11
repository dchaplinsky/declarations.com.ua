(function($) {
  var ranges = [
    { divider: 1e18, suffix: 'E' },
    { divider: 1e15, suffix: 'P' },
    { divider: 1e12, suffix: 'T' },
    { divider: 1e9, suffix: 'G' },
    { divider: 1e6, suffix: 'M' },
    { divider: 1e3, suffix: 'k' }
  ];

  function formatNumber(n) {
    for (var i = 0; i < ranges.length; i++) {
      if (n >= ranges[i].divider) {
        return '₴' + Math.round((100 * n / ranges[i].divider)) / 100 + ranges[i].suffix;
      }
    }

    return n.toString();
  }

  function format_uah(value, precision, withSuffix) {
    if (withSuffix) {
      return formatNumber(value);
    }

    return accounting.formatMoney(value, "₴", precision !== undefined ? precision : 2);
  }

  function format_sqm(value) {
    return accounting.formatMoney(value, {symbol: "м²",  format: "%v %s"}, 2 )
  }

  function formatter(format, x) {
    if (format == 'area'){
      return format_sqm(x);
    } else {
      return format_uah(x, 0, true);
    }
  }

  $(function() {
    var all_data,
      chart,
      back_button = $(".search-card__back"),
      dog_tag = $(".search-card__name span"),
      bird_view_data = [];

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

    function buildMainChart() {
      var year = parseInt($("#year").val());
      var param_x = {
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
                  return format_uah(value, 0, true);
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
                    return format_uah(value, 0, true);
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
          },
          onClick: function(event, objs) {
            if (objs.length > 0) {
              try {
                var person_bubble = this.config.data.datasets[objs[0]._datasetIndex].data[objs[0]._index],
                  person_id = person_bubble.id,
                  person = all_data["persons"][person_id],
                  detailed_data = [];

                if (!person_bubble.drilldown) {
                  return;
                }

                for (var year in person["documents"]) {
                  var doc = person["documents"][year],
                    x = doc["aggregated_data"][param_x.name],
                    y = doc["aggregated_data"][param_y.name],
                    r = doc["aggregated_data"][param_r.name],
                    estate = doc["aggregated_data"]["estate.total_other"];

                  detailed_data.push({
                    "id": person_id,
                    "name": year + ", " + person["name"],
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
                    "drilldown": false
                  });

                }

                $('.chartjs-tooltip').css({
                  opacity: 0,
                });

                for (var i = 0; i < detailed_data.length; i++) {
                  detailed_data[i]["scaled_r"] = (detailed_data[i]["v"] + 0.1) / (max_r + 0.1);
                  detailed_data[i]["scaled_estate"] = (Math.min(detailed_data[i]["estate"], 500) + 0.1) / (500 + 0.1);
                }

                $(".landing-page__declarants-table tr").hide().filter(".person-" + person_id).show();
                chart.data.datasets = [
                  {"data": detailed_data, "type": "bubble"},
                  {"data": detailed_data, "type": "line", "backgroundColor": "transparent"}
                ];
                chart.update();
                back_button.show();
                dog_tag.html(person["name"]);
              } catch(error) {
                  console.error(error);
              }
            };
          }
        };

      bird_view_data = [];
      for (var i in all_data["persons"]) {
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

          bird_view_data.push({
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
            "drilldown": true
          });
        }
      }

      for (var i = 0; i < bird_view_data.length; i++) {
        bird_view_data[i]["scaled_r"] = (bird_view_data[i]["v"] + 0.1) / (max_r + 0.1);
        bird_view_data[i]["scaled_estate"] = (Math.min(bird_view_data[i]["estate"], 500) + 0.1) / (500 + 0.1);
      }

      if (typeof(chart) === "undefined") {
        chart = new Chart('tablo', {
          type: 'bubble',
          data: {
            datasets: [{
              "data": bird_view_data
            }]
          },
          options: options
        });
      } else {
        chart.data.datasets = [{"data": bird_view_data}];
        chart.update();
      }
    };

    function buildPersonCharts() {
      ['#incomes', '#assets', '#estate', '#land', '#liabilities', '#expenses'].forEach(function(selector) {
        var container = $(selector),
          data = container.data(),
          canvas = container.find('canvas'),
          fmt = formatter.bind(null, data.format),
          familyDataset = {
            label: data.family_label,
            backgroundColor: '#7175D8',
            borderColor: '#7175D8',
            data: data.family_values,
            fill: true,
          },
          declarantDataset = {
            label: data.declarant_label,
            backgroundColor: '#5ECBA1',
            borderColor: '#5ECBA1',
            data: data.declarant_values,
            fill: true,
          },
          config = {
            type: 'line',
            data: {
              labels: data.labels,
              datasets: data.family_values ?
                [familyDataset, declarantDataset]
                : [declarantDataset]
            },
            options: {
              responsive: true,
              legend: {
                display: true,
                position: 'bottom',
                labels: {
                  boxWidth: 16,
                  fontSize: 14
                }
              },
              tooltips: {
                mode: 'index',
                intersect: false,
                custom: function(tooltip) {
                  $(this._chart.canvas).css('cursor', 'pointer');

                  var positionY = this._chart.canvas.offsetTop;
                  var positionX = this._chart.canvas.offsetLeft;

                  $('.chartjs-tooltip').css({
                    opacity: 0,
                  });

                  if (!tooltip || !tooltip.opacity) {
                    return;
                  }

                  var $tooltip = $(selector + '-chart-tooltip');

                  if (tooltip.dataPoints.length) {
                    var hasFamilyData = tooltip.dataPoints.length === 2;
                    var family = hasFamilyData ? tooltip.dataPoints[0] : null;
                    var declarant = hasFamilyData ? tooltip.dataPoints[1] : tooltip.dataPoints[0];

                    $tooltip.find('.chartjs-tooltip__name .value').html(declarant.label);

                    if (hasFamilyData) {
                      $tooltip.find('.chartjs-tooltip__family-value .value').html(fmt(family.value));
                      $tooltip.find('.chartjs-tooltip__family-value .chartjs-tooltip__legend-color').css({
                        backgroundColor: familyDataset.backgroundColor,
                        height: 16,
                        width: 16,
                      });
                    }

                    $tooltip.find('.chartjs-tooltip__declarant-value .value').html(fmt(declarant.value));
                    $tooltip.find('.chartjs-tooltip__declarant-value .chartjs-tooltip__legend-color').css({
                      backgroundColor: declarantDataset.backgroundColor,
                      height: 16,
                      width: 16,
                    });

                    var tooltipPositionY = hasFamilyData && family.y - declarant.y > $tooltip.height() ?
                      (family.y + declarant.y) / 2 - $tooltip.height() / 2
                      : declarant.y;

                    $tooltip.css({
                      opacity: 1,
                      top: positionY + tooltipPositionY + 'px',
                      left: positionX + declarant.x + 'px',
                    });
                  }
                },
                enabled: false,
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
                  ticks: {
                    callback: function(value, index, values) {
                      return fmt(value);
                    }
                  }
                }]
              }
            }
          },
          chart = new Chart(canvas, config);
      });
    };

    if ($(document.body).hasClass('landing-page__details')) {
      $.getJSON("?format=json", function(data) {
        all_data = data;
        buildMainChart();
      });
    } else {
      buildPersonCharts();
    }

    function restore_nav() {
      back_button.hide();
      dog_tag.html(dog_tag.data("default"));
      $(".landing-page__declarants-table tr").show();
    }

    back_button.on("click", function(e) {
      e.preventDefault();
      restore_nav();
      chart.data.datasets = [{"data": bird_view_data}];
      chart.update();
    });

    $('#year')
      .on('change', function() {
        buildMainChart();
        restore_nav();

        $('.landing-page__declarants-table')
          .hide()
          .filter('#declarants-' + $(this).val())
          .show();
      });

    $(document.body).on("tooltip-shown", function(e) {
      var anchor = $(e.target),
        tooltip = anchor.find(".n-tooltip__body"),
        canvas = tooltip.html('<canvas height="220">').find("canvas"),
        fmt = formatter.bind(null, anchor.data('format')),
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
              position: "bottom",
              labels: {
                boxWidth: 10,
                fontSize: 10
              }
            },
            tooltips: {
              mode: 'index',
              intersect: false,
              bodySpacing: 5,
              callbacks: {
                label: function(tooltipItem, data) {
                  var point = data.datasets[tooltipItem.datasetIndex];
                  return (point.label || '') + ': ' + fmt(tooltipItem.value);
                }
              }
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
                ticks: {
                  callback: function(value, index, values) {
                    return fmt(value);
                  }
                }
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

    var connections_graph = $("#connections").on("activated", function(e) {
      var viz = $("#cy");

      if (viz.length) {
        var graph = viz.data("graph_data"),
          edge_length = Math.max(50, 3 * graph["nodes"].length);


        var cy = cytoscape({
          container: viz,

          boxSelectionEnabled: false,
          autounselectify: true,

          style: [ // the stylesheet for the graph
            {
              selector: 'node',
              style: {
                'height': 50,
                'width': 50,
                'border-color': '#000',
                'border-width': 0,
                'border-opacity': 0.5,
                "content": "data(label)",
                "background-color": "#2F80ED",
                "text-wrap": "wrap",
                "text-max-width": 100,
                "text-valign": "bottom",
                "text-halign": "center",
              }
            },
            {
              selector: 'node.person',
              style: {
                "background-color": "#5ECBA1",
              }
            },
            {
              selector: 'node.root',
              style: {
                'height': 70,
                'width': 70,
                "background-color": "#7175D8",
                'border-width': 4,
                'border-color': '#2F80ED',
                "background-fill": "radial-gradient",
                "background-gradient-stop-colors": "#7175D8 #7175D8 #ffffff #ffffff",
              }
            },
            {
              selector: 'node.company',
              style: {
                "background-color": "#FF6B69",
              }
            },
            {
              selector: 'edge',
              style: {
                'curve-style': 'bezier',
                'width': 3,
                'target-arrow-shape': 'triangle',
                'line-color': '#ffaaaa',
                'target-arrow-color': '#ffaaaa'
              }
            }
          ],

          elements: graph,
          layout: {
            name: 'cose',
            animate: "end",
            fit: true,
            padding: 10,
            initialTemp: 100,
            animationDuration: 500,
            nodeOverlap: 6,
            maxIterations: 3000,
            idealEdgeLength: edge_length,
            nodeDimensionsIncludeLabels: true,
            springLength: edge_length * 3,
            gravity: -15,
            theta: 1,

            padding: 10
          }
        }); // cy init
      }
    });

    if (document.location.hash == "#connections") {
      connections_graph.trigger("activated");
    }
  });
})(jQuery);
