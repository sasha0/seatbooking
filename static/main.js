var ws;
var template = '{{#rows}}';
    template += '   <div class="custom-label">{{id}}</div>';
    template += '       {{#row}}';
    template += '           {{#is_available}}';
    template += '                           <div class="ui primary button" onclick="book_seat(\'{{id}}\', \'{{row_id}}\', \'{{event_id}}\');">';
    template += '                               {{id}}';
    template += '                           </div>';
    template += '{{/is_available}}';
    template += '{{^is_available}}';
    template +=  '<div class="ui grey button">{{id}}</div>';
    template += '{{/is_available}}';
    template += '{{/row}}<br><br>';
    template += '{{/rows}}';

var booked_seats;

function check_if_seat_available(row_id, seat_id) {
    for (var item in booked_seats) {
        var seat = booked_seats[item];
        if (parseInt(seat.row_id) == row_id && parseInt(seat.seat_id) == seat_id) {
            return false;
        }
     }
    return true;
}

function get_available_seats() {
    var event_id = $('#event-container').data('eventid');
    var url = "ws://localhost:5000/events/" + event_id + "/book/";
    ws = new WebSocket(url);
    ws.onopen = function() { };
    ws.onmessage = function(event) {
        var data = JSON.parse(event.data);
        booked_seats = data.booked_seats;
        var rows = new Array();
        for (var i=0;i<=data.event.rows;i++) {
            var row = new Array();
            for (var j=0;j<=data.event.seats;j++) {
                var is_available = check_if_seat_available(i+1, j+1);
                var seat = {'id': j+1, 'row_id': i+1, 'is_available': is_available};
                row.push(seat);
            }
            rows.push({'row': row, 'id': i+1});
        }
        var html = Mustache.render(template, {'rows': rows, 'event_id': event_id});
        $('#seats').html(html);
    };
}

function book_seat(seat_id, row_id, event_id) {
    var data = {'seat_id': seat_id, 'row_id': row_id, 'event_id': event_id};
    ws.send(JSON.stringify(data));
}