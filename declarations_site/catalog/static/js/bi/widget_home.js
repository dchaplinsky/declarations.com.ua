var obj_names = ['income', 'income_family', 'flat_area', 'flat_area_family'];

var ascending =  function(_name) {
  return function(a, b){ return a[_name] < b[_name] ? -1 : a[_name] > b[_name] ? 1 : a[_name] >= b[_name] ? 0 : NaN; }
}


//d3.csv("/static/data/states.csv", function(error, rows) {
  d3.csv("/static/data/states.csv", function(error, rows) {
  if (error) throw error;
  
  var barwidth = 150;  
  var income_max = 0;
/*
  var states = d3.nest()
    .key(function(d){return d.region;})
    .rollup(function(leaves) { 
              var a = leaves.map(function(d){return d.income; });  a.sort(d3.ascending); var end = d3.quantile(a, 0.75);
              var median = d3.median(a);
              income_max = income_max > median ? income_max : median;

              var a1 = leaves.map( function(d){return d.income_family;} );  a1.sort(d3.ascending); var end1 = d3.quantile(a1, 0.75);
              var median_fam = d3.median(a1);
              income_max = income_max > median_fam ? income_max : median_fam;

              return [{"median": median,  "start": d3.quantile(a, 0.25), "end": end},
                      {"median": median_fam, "start": d3.quantile(a1, 0.25), "end": end1},
                     ]   })
    .entries(persons);

*/
  var states = rows.map(function(r){ income_max = income_max > +r.m_inc ? income_max : +r.m_inc;  return {key: r.category, values: [{ median: +r.m_inc},{ median: +r.m_finc}]};           } )

  states = states.sort(function(a, b) { return b.values[0].median - a.values[0].median; }).slice(0, 15) ;

console.log(states)

  var colnames = [0,1];

  d3.selectAll(".first thead td").data(colnames)

    .on("click", function(k) {
      tr.sort(function(a, b) { return b.values[k].median - a.values[k].median; });
    });

  var tr = d3.select("tbody").selectAll("tr")
      .data(states)
    .enter().append("tr");

  tr.on('click', function (e){ window.location.href = "/BI/?year=''&income=''&region=" + e.key  });  

  tr.append("th")
      .text(function(d) { return d.key; });

  var svg = tr.selectAll("td")
      .data(function(d) { return d.values; })
    .enter().append("td").append("svg")
      .attr("width", barwidth + 20)
      .attr("height", 14);

var rad = 5;
var lh = 14;

svg.append("circle")
      .attr("class", "median")
      .attr("r", rad)
      .attr('cy', lh/2)
      .attr("cx", function(d) {  return   rad + d.median / income_max * barwidth ; }) 
      .style("display", function(d){ return d.median === 0 ? 'none' : 'inline';} )         

svg.append("circle")
      .attr("class", "median")
      .attr("r", 2)
      .attr('cy', lh/2)
      .attr("cx", rad) 

      

 svg.append("line")
      .attr("x1", rad)
      .attr('y1', lh/2)
      .attr("x2", function(d) {  return   d.median / income_max * barwidth ; }) 
      .attr('y2', lh/2)
      .style("stroke", "#e95000")
      .style("stroke-width", "1px")
      .style("display", function(d){ return d.median === 0 ? 'none' : 'inline';} )         
     
  
});
