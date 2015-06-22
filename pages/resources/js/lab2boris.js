$('#add').click(function() {
    var el = document.getElementById('intervals');
    var interval = document.createElement('div');
    interval.className = "interval";

    var a = document.createElement('input');
    a.type = "number";
    a.placeholder = "a";
    a.className = "a";
    a.value = "1";

    var b = document.createElement('input');
    b.type = "number";
    b.placeholder = "b";
    b.className = "b";
    b.value = "10";

    var step = document.createElement('input');
    step.type = "number";
    step.placeholder = "кроків";
    step.className = "s";
    step.value = "10";

    var del = document.createElement('button');
    del.className = "btn btn-danger delete";
    del.innerHTML = "Видалити"
    
    interval.appendChild(a);
    interval.appendChild(b);
    interval.appendChild(step);
    interval.appendChild(del);
    el.appendChild(interval);
});

$(document).on("click",'.delete',function(e) {
    $(this).parent().remove();
});
