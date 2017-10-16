var currentDay = 0;
var currentMonth = 0;
var currentYear = 0;
var maxDays = 0;
var lastSelectedDate = 0;
var selectedDate = 0;
var monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];

function Initialize(){
    
    // Description: starts the calendar off with current month and year
    var currentDate = new Date();
    var year = document.getElementById('year');
    year.value = currentDate.getFullYear(); // year

    var intialMonth = currentDate.getMonth();
    var selectedMomth = document.getElementById('month').options.item(intialMonth);
    selectedMomth.selected = true; // month
    LoadCalendar();
}

Initialize();

function LoadCalendar(){
    
    // Description: validate year and month, if good then
    //              go ahead and draw calendar e.g. GetCalendarHTML(year, month)
    
    lastSelectedDate = 0;
    selectedDate = 0;
    
    document.getElementById('err').innerHTML = "";
    
    var month = document.getElementById('month').value;
    var year = Number(document.getElementById('year').value);
    
    // Validate month/year
    var goodDate = true;
    if (month < 0 || month > 11){
        goodDate = false;
        document.getElementById('err').innerHTML =
            "Input error; month must be between 0 and 11!"
    }
    
    if (isNaN(year)){
        goodDate = false;
        document.getElementById('err').innerHTML =
            "Input error; invalid year value (not even numeric)!"                    
    }
    
    if (year < 101 || year > 3000){
        goodDate = false;
        document.getElementById('err').innerHTML =
            "Input error; invalid year value!" + "<br />" +
            "Valid value range: 101 to 3000";
        
    }
    
    if (goodDate) { 
        GetCalendarHTML(year, month); // DRAW the Calendar!
        //
        var table = document.getElementById("tbl");
        var rows = table.rows
        var rowLenght = table.rows.length;
        for(var row=0; row<rowLenght; row++){
            cellLenght = rows[row].cells.length;
            for(var cell=0; cell<cellLenght; cell++){
            var td_id = rows[row].cells[cell].id;
            }
            
        }
        GetCalendarData(month, year);

    } else {
        document.getElementById('month_calendar').innerHTML = "";
    }
}

function GetCalendarHTML(year, month){
    
    // Description: main calendar drawing routine
    
    var todayDate = new Date(); // today's date

    var mainDate = new Date(year, month, 1); // main Calendar date

    var startDate = new Date(); // Calendar's start date
    startDate = GetCalendarStartDate(year, month);
    var hostName = window.location.hostname
    // Calendar startup parameters ********************
    currentDay = startDate.getDate();      // day
    currentMonth = startDate.getMonth();   // month
    currentYear = startDate.getFullYear(); // year
    maxDays = GetMonthDayCount(currentMonth, currentYear); // max month day count

    // setup Calendar table ***************************
    var calText = "<table class='table table-bordered table-hover table-responsive table-striped' id='tbl'>";
    calText += "<tr id='id_cal_table' class='thisMonth'><th colspan='7'>" + monthNames[month] + " " + year + "</th></tr>"; // table add month and year header
    calText += "<tr><td>Sun</td><td>Mon</td><td>Tue</td><td>Wed</td><td>Thu</td><td>Fri</td><td>Sat</td></tr>"; // table add weekday names header
    
    var sClass = ""; // class value for TD/cell
    
    for (var row = 0; row < 6; row++){ // row/week loop

        calText += "<tr>"; // begin table row
        for (var col = 0; col < 7; col++){ // column/weekday loop

            // SORT OUT THE CLASS NAME FOR TABLE CELL *********
            if (currentMonth == month){ 
                sClass = "thisMonth"; 
            } else { sClass = "notThis"; }
            
            if (todayDate.getMonth() == currentMonth && todayDate.getFullYear() == currentYear){
                if (currentDay == todayDate.getDate()){ sClass = "today"; }
            }
            
            // GET A DATE STRING FOR THIS DAY (e.g. cell.id) **
            var day = currentDay;
            var id_month = currentMonth+1;
            if (currentDay < 10){
                day = '0' + currentDay
            }
            if (id_month < 10){
                id_month = '0' + id_month
            }
            var cellDate = new Date(currentYear, currentMonth, currentDay);

            // ADD TD DEF. TO TABLE DEF. **********************
            var id = currentYear + '-' + id_month  + '-' + day
            calText += MakeMonthCalenderCell(sClass, cellDate.toDateString(), currentDay, id);

            // INCREMENT DAY TO NEXT DATE *********************
            if (currentDay < maxDays){
                currentDay++;
            } else {
                currentDay = 1;
                currentMonth++;
                if (currentMonth > 11){
                    currentMonth = 0; // reset current month to Jan.
                    currentYear++;    // then increment current year
                }
                // GET NEW MAX DAY COUNT FOR NEW MONTH ************
                maxDays = GetMonthDayCount(currentMonth, currentYear);
            }      

        } // column/weekday loop

        calText += "</tr>"; // end table row/week
        
        if (currentMonth > month) { break; } // if already past month break out of row loop
        
    } // row/week loop

    calText += "</table>"; // end Calendar table

    document.getElementById('month_calendar').innerHTML = calText; // draw Calendar
    if (hostName.startsWith('2.localhost') == true){
        $('#id_cal_table').addClass('table-success');
    }else{
        $('#id_cal_table').addClass('table-info');
    }
}

function GetCalendarStartDate(year, month){
    
    // Description: returns the Calendar start date
    //  for a given month and year combination...
    //  e.g. the date in the top left cell of the
    //  calendar grid/table
    
    var date1 = new Date(year, month, 1);
    
    var day1 = date1.getDay();
    
    if (day1 == 0){ 
        
        return date1; // e.g. 1st of month is a Sunday
        
    } else {
        
        // start of calendar is in previous month
        var m = month -1; // decrement month
        var y = year;
        if (m < 0){ // reset month to december
            m = 11; // and decrement year
            y--;
        }
        
        var maxDays = GetMonthDayCount(m, y);   // max days in prev. month
        var newDay = maxDays - day1 + 1;        // day of prev. month to start
                                                // the calendar
        
        var date2 = new Date(y, m, newDay);     // create start date
        
        return date2;
    }
}

function GetMonthDayCount(monthNumber, year){

    // Description: return the number of days in a month
    // monthNumber is expected to be between 0 and 11 re: JS
    // year is only really required when monthNumber is 1 (or February)

    var temp = 30;
    switch(monthNumber) {
        case 0:
        case 2:
        case 4:
        case 6:
        case 7:
        case 9:
        case 11:
            temp = 31;
            break;
        case 1:
            temp = GetFebruaryDayCount(year);
            break;
    }
    return temp;
}

function GetFebruaryDayCount(year){
    
    // Description: returns the number of days in the
    // month of February by year e.g. leap years have
    // an extra day

    var temp = 28;
    if ( (year%100!=0) && (year%4==0) || (year%400==0) ){
        temp = 29;
    }
    return temp;
}

function MakeMonthCalenderCell(className, title, day, id){
    var temp = "<td ";
    temp += "class='" + className + "' ";
    temp += "title='" + title + "' ";
    temp += "id='" + id + "'> "; 
    temp += "<a href='/"+BASE_URL+"date/?date="+id+"'><div style='height:100%;width:100%'>"
    temp += day;
    temp += "</div></a>"
    temp += "</td>";
    return temp;

}
function GetCalendarData(month, year){
    $.ajax({
      url:"/"+BASE_URL+"get-month-data/?month="+month+"&year="+year,
      method: 'GET',
      success: function(data) {
        data = JSON.parse(data).appointments;
        var out = "";
            for(var i = 0; i < data.length; i++) {
                out ='<span class="table-success"><a href="/'+BASE_URL+'date/?date='+data[i].date+'">'+data[i].summary+'</a></span>';
                document.getElementById(data[i].date).innerHTML=out
            }
      }
  });
}