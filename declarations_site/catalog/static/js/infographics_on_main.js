$(function() {
    var rootUrl = '/declaration/';
    var regionsArr = [
        'Харківська область',
        'Львівська область',
        'Чернівецька область',
        'Донецька область',
        '!не визначено',
        'м. Київ',
        'Миколаївська область',
        'Дніпропетровська область',
        'Житомирська область',
        'Рівненська область',
        'Одеська область',
        'Київська область',
        'Закарпатська область',
        'Запорізька область',
        'Черкаська область',
        'Чернігівська область',
        'Сумська область',
        'Волинська область',
        'Івано-Франківська область',
        'Херсонська область',
        'Хмельницька область',
        'Тернопільська область',
        'Полтавська область',
        'Кіровоградська область',
        'Луганська область',
        'Вінницька область',
        'Кримська Автономна Республіка'
    ];
    var allData = {};
    var format = function(d) {
        return d3.format(",d")(d).replace(/\,/gi, ' ')
    };
    var vizContainers = $('.viz');
    var year_filter = $("#filter-year");

    year_filter.on("change", function(e) {
        getDataAndDraw();
    });

    $("#filter-region").on("change", function(e) {
        switchSelectionByRegions($(this).val());
    });

    $("#filter-category").on("change", function(e) {
        switchSelectionByPosition($(this).val());
    });
    
    function getDataAndDraw() {
        var year = year_filter.val();

        vizContainers.each(function(i, viz) {
            viz = $(viz);
            viz.toggleClass("isLoading", true);
            var parameter = viz.data("source");

            if (!allData[parameter]) {
                d3.csv('/static/data/viz_' + parameter + '.' + year + '.csv', formatRow).then(
                    function(data) {
                        allData[parameter + "/" + year] = data;
                        rerenderCharts(viz, parameter, year);
                    }
                );
            } else {
                rerenderCharts(viz, parameter, year);
            }

        })
    }

    function draw(id, data, limit, highlightParameter) {
        d3.selectAll(id + " > g > *").remove();
        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .html(
                function(d) {
                    return generateTooltipContent(d, highlightParameter)
                }
            )
            .direction('se')
            .offset([0, 3]);

        $(id).siblings('.loading').remove();

        var normalWidth = ($(id).closest(".container").width() - 10) / 2;
        var windowWidth = normalWidth < 300 ? window.innerWidth - 20 : normalWidth;
        var svg = d3.select(id);
        svg
            .attr("width", windowWidth)
            .attr("height", windowWidth)
            .call(tip);

        var width = height = windowWidth;
        var pack = d3.pack()
            .size([width - 2, height - 2])
            .padding(3);

        var root = d3.hierarchy({
                children: data
            })
            .sum(function(d) {
                return d[highlightParameter];
            })
            .sort(function(a, b) {
                return b.value - a.value;
            });

        root.children = root.children.filter(function(i, n) {
            return (n < (limit || 100))
        });

        pack(root);

        var node = svg.select("g")
            .selectAll("g")
            .data(root.descendants())
            .enter().append("g")
            .attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
            })
            .attr("class", "node");

        node.append("circle")
            .attr("class", function(d) {
                return d.data.organization_group + '-job circle region-' + d.data.region + ' depth-' + d.depth;
            })
            .attr("r", function(d) {
                return d.r;
            })
            .on('mouseover', function(d){ return d.depth ? tip.show(d) : null})
            .on('mouseout', tip.hide)
            .on('click', function(d) {
                window.open(rootUrl + d.data.id);
            });

        node.append("text")
            .text(function(d) {
                return d.data.shortName
            })
            .style("font-size", function(d) {
                return d.data.name ? 0.35 * Number(d.r) + 'px' : '10px'
            })
            .on('mouseover', tip.show)
            .on('mouseout', tip.hide);

        d3.select(id + '-wrapper').classed('isLoading', false);
        switchSelectionByPosition("j");
    }

    function rerenderCharts(viz, parameter, year) {
        var d3_target = viz.data("d3-target")
        setTimeout(function() {
            draw(d3_target, allData[parameter + "/" + year], 100, parameter)
        }, 0);
    }

    function generateTooltipContent(d, activeKey) {
        var html = '';
        var auto = d.data.vehicles_names ? d.data.vehicles_names.split('/').filter(function(i) {return i !== 'null'}) : [];
        if (d.data.name) {
            html = "<div class='tip-inner " + activeKey + "'><div class='name'>" + d.data.name + "</div><div>" +
                regionsArr[Number(d.data.region) - 1] + "</div><hr/><div>" +
                d.data.name_post + "</div><hr/><div><b>Рухоме майно (разом з готівкою):</b><nobr> " +
                format(d.data["assets.total"]) + " грн.</nobr></div>" +
                "<div><b>Готівка (окремо):</b><nobr> " + format(Number(d.data["assets.cash.total"])) + " грн.</nobr></div>" +
                "<div><b>Надходження за 2016р.:</b><nobr> " +
                format(d.data["incomes.total"]) + " грн.</nobr></div><div><b>Земля у власності:</b><nobr> " +
                format(d.data["estate.total_land"] / 10000) + " га.</nobr></div><div><b>Нерухомість у власності:</b><nobr> " +
                format(d.data["estate.total_other"]) + " м2.</nobr></div></div>" +
                (!auto.length ? "" : "<hr/><div><b>Наявні автомобілі (" + auto.length + "):</b></div>" +
                    auto.map(function(i) { return "<div class='auto-row'>" + i.toUpperCase() + "</div>" }).join(''))
        } else {}
        return html
    }

    function formatRow(d) {
        if (d.organization_group === 't') d.organization_group = 'b';
        if (~'dr'.indexOf(d.organization_group)) d.organization_group = 'j';

        var nameArr = d.name.split(' ');
        d.shortName = nameArr[0].slice(0, 9);
        return d;
    }

    function switchSelectionByRegions(value) {
        d3.selectAll(".circle").classed("region-active", false);
        d3.selectAll(".region-" + value).classed("region-active", true);
    }

    function switchSelectionByPosition(value) {
        d3.selectAll(".circle").classed("position-active", false);
        d3.selectAll("." + value + '-job').classed("position-active", true);
    }
});