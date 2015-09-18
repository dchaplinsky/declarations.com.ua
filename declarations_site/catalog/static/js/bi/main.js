
var state = {
  cross_data: [],
  current: [],
  clipboard: [],
  table: null,

  filters: { // select filters
    region_options: {v:null, accessor:function(d){ return d.region }, dimension: null, param: 'region'},
    office_options: {v:null, accessor:function(d){ return d.off }, dimension: null, param: 'office'},
    year_options: {v:2014,  accessor:function(d){ return +d.year  }, dimension: null, param: 'year'},
    range_options: {v:[0, 100000], accessor:function(d){ return +d.income }, dimension: null, param: 'income'}
  },
  
  set_all_by_url: function(){
    for(k in this.filters){
        var p = get_url_param( this.filters[k].param ); 
        p = p ? decodeURI(p) : p;
        if(p){
          this.filters[k].v = p;
          change_select("#"+k, p);
        }
        

    }
  },

  set_value:  function(filter, val){
    var fil = this.filters[filter];
    fil.v = val;
    fil.v = fil.v === '' ? null : fil.v;
    //console.log(k) 
    //console.log(fil.dimension.top(Infinity).length)   
    fil.dimension.filter(fil.v);
    this.current = fil.dimension.top(Infinity) 
    
    this.redraw();
    //tbl();
  },

  init_crossfilters: function(){
    
   //console.log(this.current) 
    for( k in this.filters ){
      var fil = this.filters[k]; 
      fil.dimension = this.cross_data.dimension(fil.accessor);
      fil.v = fil.v === '' ? null : fil.v;
      fil.dimension.filter(fil.v);

    }

    this.current = this.filters[k].dimension.top(Infinity) ;
  },

  redraw: function (){

    change_text( '#total_records'  , this.current.length);
    this.table.clear();
    this.table.rows.add(this.current).draw();
    csv_link(this.current);

  },

  add_table: function (data_table){
    this.table = data_table;
  },


  to_clipboard: function(id){

    if(this.clipboard.indexOf(id) === -1) {
      this.clipboard.push(id);
      change_text('#clipboard', this.clipboard.length);
      dash_link(state.clipboard);
    }  


  }

}; // global state 


function change_text(id, l){
  d3.select(id).text(l);
}


function csv_link(current){
//console.log(current)  
  current = current.map(function(d){d.link = 'http://declarations.com.ua/declaration/' + d.id; return d;});
  d3.select("#download a").on("click", function(){ console.log('click'); export_csv( current.map(function(d){return d3.values(d) }), 
                                                              d3.keys(current[0]),  'declarations_'+ new Date().toString().replace(/ /g, '_') +'.csv') });  
}

function dash_link(ids){
 
  var data = state.current;
  var objects = {};
  var exp = [];

  data.forEach(function(d){ objects[d.id] = d; });
  ids.forEach(function(id){ exp.push(objects[id]) });  
//console.log(objects)

  exp = exp.map(function(d){d.link = 'http://declarations.com.ua/declaration/' + d.id; return d;});
  d3.select("#clipboard").on("click", function(){ export_csv( exp.map(function(d){return d3.values(d) }), 
                                                              d3.keys(exp[0]),  'history_'+new Date().toString().replace(/ /g, '_')+'.csv') });  
}

  

d3.selectAll("select").on("change", change)  // select form input callback
function change() {
    var sel = d3.select(this);
    var val = sel.node().value;
    var filter = sel.attr("id"); // select name is an id
    //var val = node.options[node.selectedIndex].value(); 
    if(filter === 'range_options') { val = eval(val);} // eval array with limits for income range
    state.set_value(filter, val);

}


function create_select(id, data, selected){

  data = data.map(function(d){ return  typeof d === "object" && d.length === 2 ? d : [d, d]})  // [v, n] - value and name of each option

  d3.select(id).selectAll("option")
  .data(data)
    .enter()
    .append("option")
    .attr("value", function(d){return d[0];})
    .attr('selected', function(d){return d[0] === selected ? "selected" : null;})
    .text(function(d){return d[1];})
}


function change_select(id, selected){
  d3.select(id).selectAll("option")
    .attr('selected', function(d){ var v = d3.select(this).attr('value'); return v == selected ? "selected" : null; })
}





var off_opts = d3.set(d3.values(office_list)).values().sort();
off_opts.unshift(['', 'всі установи']);

//console.log(off_opts)
create_select("#office_options", off_opts, 'всі установи');

var obj_names = ['income', 'income_family', 'flat_area', 'flat_area_family'];



var millions_format = function ( val, type, full )  {
                return  d3.round(+val / 1000000, 3);
}  

var ratio_format = function(limit, how_to_compare, inf_message) {

    return function ( val, type, full )  {
      
                
                val = d3.round(+val, 1);
                //if(display == "sort"){ console.log(display); return val; }

                if(type === 'display' && val > 0){  
                  /*if(val === Infinity) return '<span style="color: crimson; font-weight: 800; font-size: 0.9em">'+inf_message+'</span>';      */
                  if(val === almost_infinity)
                      return '<span style="color: maroon; font-weight: 400">' + "р" + '</span>';
                  return eval("val"+how_to_compare+"limit") ? 
                      '<span style="color: crimson; font-weight: 800">' + val + '</span>' : val;
                }      
                return val; 
                //return  d3.round(+val, 2);

    } 
 }

function simple_ratio(val){
  return d3.round(+val, 1);
}


var get_url_param = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return results[1] || 0;
    }
}

function format_nan(val){
   return isNaN(val) ? 0 : val;
}


var almost_infinity = 1000000;
var tab;
d3.csv("/static/data/declarations.csv", function(error, persons) {
  if (error) throw error;
  
  var barwidth = 150;  
  var income_max = 0;

  persons.forEach(function(d){d.off = office_list[d.office]; // shortened names
                              d.income_vs_salary = d.income_salary == 0 ? 0 : d.income / d.income_salary;
                              d.income_vs_family = d.income == 0 ? (d.income_family > 0 ? almost_infinity : 0) : d.income_family / d.income;  
                              d.land_vs_family = d.land_area == 0 ? (d.land_area_family > 0 ? almost_infinity : 0) :  d.land_area_family / d.land_area; 
                              d.flat_vs_family = d.flat_area == 0 ? (d.flat_area_family > 0 ? almost_infinity : 0) :  d.flat_area_family / d.flat_area;
                              d.house_vs_family = d.house_area == 0 ? (d.house_area_family > 0 ? almost_infinity : 0) :  d.house_area_family / d.house_area;
                              d.cars_vs_family = d.cars == 0 ? (d.cars_family > 0 ? almost_infinity : 0) : d.cars_family / d.cars;
                              });  


  var states = d3.nest()
    .key(function(d){return d.region;})
    .entries(persons);

  var reg_opts = states.map(function(d){return d.key;}).filter(function(d){ return d != ''}).sort();
  reg_opts.unshift(['', 'всі регіони']);
  //console.log(reg_opts);

  create_select("#region_options", reg_opts, "всі регіони");    
  


  var forms = crossfilter(persons);
  state.cross_data = forms;
  state.set_all_by_url();
  state.init_crossfilters();
  change_text('#total_records',state.current.length);
  

   state.add_table ( 

     $('#example').DataTable( {

        info:     false,
        searching: false,
        bLengthChange: false,
        
        lengthMenu: [25],
        data: state.current,
        aoColumns: [
          { "data": "name", title: "Ім'я", 
            mRender: function ( name, type, full )  {
                return  '<a onclick="state.to_clipboard(\''+full['id']+'\')" target="_blank" href="http://declarations.com.ua/declaration/'+ full['id'] +'">' +name + 
                '</a>' +
                '<span class="plus" style=" font-family: Arial; font-size: 1.2em; margin-left: 10px; cursor: copy" onclick="state.to_clipboard(\''+full['id']+'\')" >' +'+'+ '</span>';
            }
          },
          /*{ "data": "id", title: "", 
            mRender: function ( id, type, full )  {
                return  '<span onclick="state.to_clipboard(\''+id+'\')" >' +'+'+ '</span>';
            }
          },*/
          { "data": "income", title: "Дохід, млн",
              mRender: millions_format
          },
          { "data": "income_salary", title: "ЗП, млн",
              mRender: millions_format 
          },
          { "data": "income_help", title: "Допомога, млн",
              mRender: millions_format 
          },
          { "data": "income_vs_salary", title: "Дохід/<br>ЗП", 
            mRender: ratio_format(2, '>', '&infin;')
          },
          { "data": "income_vs_family", title: "Дохід родини/<br>Дохід",
            mRender: ratio_format(2, '>', 'на родині')
          },
          { "data": "flat_vs_family", title: "Квартири родини/<br>Квартири",
            mRender: ratio_format(2, '>', 'на родині')
          },
          { "data": "house_vs_family", title: "Будинки родини/<br>Будинки",
            mRender: ratio_format(2, '>', 'на родині')
          },
          { "data": "land_vs_family", title: "Земля родини/<br>Земля",
            mRender: ratio_format(2, '>', 'на родині')
          },
          { "data": "cars_vs_family", title: "Машини родини/<br>Машини",
            mRender: ratio_format(2, '>', 'на родині')
          }
          
        ]
    } )

  );
  
});


