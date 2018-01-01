$(function() {
    var height1 = $('#vizpannel').position().top;
    var height2 = document.getElementById('vizpannel').clientHeight;
    var filterPanel = document.getElementById('filterpanel');

    window.addEventListener('scroll', handleScroll);
    handleScroll(); //For first time
    function handleScroll() {
        var scrolled = document.body.scrollTop || document.documentElement.scrollTop;
        if (scrolled > height1 && scrolled < 6000) {
            filterPanel.className = "fixed"
        } else {
            filterPanel.className = "relative"
        }
    };
    var rootUrl = 'https://declarations.com.ua/declaration/';
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
    var format = (d) => d3.format(",d")(d).replace(/\,/gi, ' ');
    var radiobuttons = document.forms.filters.showParameter;
    var vizContainers = d3.selectAll('.viz');

    for (var i = 0; i < radiobuttons.length; i++) {
        radiobuttons[i].onclick = function(e) {
            getDataAndDraw(e.target.value);
        }
    }

    // Add options to regional selector
    var regionSelector = d3.select("#regionSelector");
    regionsArr.forEach(function(i, n) {
        regionSelector
            .append("option")
            .attr("value", n + 1)
            .text(i)
    });
    getDataAndDraw('assets.total');
    console.log("Oh lord");

    function getDataAndDraw(parameter) {
        console.log(parameter);
        vizContainers.classed('isLoading', true);
        if (!allData[parameter]) {
            d3.csv('http://www.liga.net/static/data/set-' + parameter + '.csv', formatRow, function(error, data) {
                console.log(arguments);
                if (error) throw error;
                allData[parameter] = data;
                splitDataOnGroups(data, parameter);
                rerenderCharts(parameter);
            });
        } else {
            rerenderCharts(parameter);
        }
    }

    function draw(id, data, limit, highlightParameter) {
        d3.selectAll("#" + id + " > g > *").remove();
        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .html((d) => generateTooltipContent(d, highlightParameter))
            .direction('se')
            .offset([0, 3]);

        var loadingIndicatorElement = document.getElementById(id + '-loading-indicator');

        if (loadingIndicatorElement) {
            loadingIndicatorElement.parentNode.removeChild(loadingIndicatorElement)
        };

        var isLargeChart = id === "vse";
        var normalWidth = isLargeChart ? 700 : 700;
        var windowWidth = window.innerWidth < normalWidth ? window.innerWidth - (isLargeChart ? 20 : 20) : normalWidth;
        var svg = d3.select("#" + id);
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
            .on('mouseover', (d) => d.depth ? tip.show(d) : null)
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

        d3.select('#' + id + '-wrapper').classed('isLoading', false);
        switchSelectionByPosition("j");
        var selectedRegion = regionSelector.node().value;

        if (selectedRegion) {
            switchSelectionByRegions(selectedRegion)
        };
    }

    function splitDataOnGroups(data, key) {
        data.forEach(function(d) {
            switch (d.organization_group) {
                case "p":
                    allData[key + 'Suddi'] = allData[key + 'Suddi'] || [];
                    allData[key + 'Suddi'].push(d);
                    break;
                case "h":
                    allData[key + 'Prokurory'] = allData[key + 'Prokurory'] || [];
                    allData[key + 'Prokurory'].push(d);
                    break;
                case "b":
                    allData[key + 'miscevaVlada'] = allData[key + 'miscevaVlada'] || [];
                    allData[key + 'miscevaVlada'].push(d);
                    break;
                case "j":
                    allData[key + 'centralnaVlada'] = allData[key + 'centralnaVlada'] || [];
                    allData[key + 'centralnaVlada'].push(d);
                    break;
                case "n":
                    allData[key + 'likari'] = allData[key + 'likari'] || [];
                    allData[key + 'likari'].push(d);
                    break;
                case "e":
                    allData[key + 'inspectory'] = allData[key + 'inspectory'] || [];
                    allData[key + 'inspectory'].push(d);
                    break;
            }
        });
    }

    function rerenderCharts(key) {
        setTimeout(function() {
            draw("vse", allData[key], 300, key)
        }, 0);
        draw("suddi", allData[key + 'Suddi'], 100, key);
        draw("prokurory", allData[key + 'Prokurory'], 100, key);
        draw("likari", allData[key + 'likari'], 100, key);
        draw("misceva_vlada", allData[key + 'miscevaVlada'], 100, key);
        draw("centr_vlada", allData[key + 'centralnaVlada'], 100, key);
        draw("inspector", allData[key + 'inspectory'], 100, key);
    }

    function generateTooltipContent(d, activeKey) {
        var html = '';
        var auto = d.data.vehicles_names ? d.data.vehicles_names.split('/').filter(i => i !== 'null') : [];
        if (d.data.name) {
            html = "<div class='tip-inner " + activeKey + "'><div class='name'>" + d.data.name + "</div><div>" +
                regionsArr[Number(d.data.region) - 1] + "</div><hr/><div>" +
                d.data.name_post + "</div><hr/><div><b>Рухоме майно (разом з готівкою):</b><nobr> " +
                format(d.data.assets) + " грн.</nobr></div>" +
                "<div><b>Готівка (окремо):</b><nobr> " + format(Number(d.data.cash)) + " грн.</nobr></div>" +
                "<div><b>Надходження за 2016р.:</b><nobr> " +
                format(d.data.incomes) + " грн.</nobr></div><div><b>Земля у власності:</b><nobr> " +
                format(d.data.land / 10000) + " га.</nobr></div><div><b>Нерухомість у власності:</b><nobr> " +
                format(d.data.apartments) + " м2.</nobr></div></div>" +
                (!auto.length ? "" : "<hr/><div><b>Наявні автомобілі (" + auto.length + "):</b></div>" +
                    auto.map(i => "<div class='auto-row'>" + i.toUpperCase() + "</div>").join(''))
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