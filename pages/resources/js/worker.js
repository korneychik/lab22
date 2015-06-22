var xmlHttp = new XMLHttpRequest();
var callback = null;
var state = 0; // 0 - idle, 1 - working
var workerId = (function generateUUID() {
    var d = performance.now();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
})();

xmlHttp.onreadystatechange = function () {
    if (xmlHttp.readyState === 4 && xmlHttp.status === 200) {
        callback(xmlHttp.responseText);
    }
};

function doGet(url, cback) {
    xmlHttp.open("GET", url, true);
    callback = cback;
    xmlHttp.send();
}

self.onmessage = function (event) {
    checkProgress(event.data);
};

function perform(taskId, chunkId, interval) {
    state = 1;

    function integral(f, a, b, step_count) {
        var sum = 0;
        if (0 == step_count) return sum;

        var step = (b - a) / (1.0 * step_count);
        for (var i = 1 ; i < step_count ; ++i ) {
            sum += f (a + i * step);
        }
        sum += (f(a) + f(b)) / 2;
        sum *= step;
        return sum;
    }

    var value = integral(function(x) { return Math.sin(x*x); }, interval.a, interval.b, interval.s);

    doGet("/lab2/api/worker-post/" + workerId + "/" + taskId + "/" + chunkId + "/" + value, function (data) {
        state = 0;
    });
}

function ping() {
    doGet("/lab2/api/worker-ping/" + workerId + "/" + state, function (data) {
        
        var json = JSON.parse(data);

        if (json.hasTask) {
            console.log(workerId, json);
            perform(json.taskId, json.chunkId, json.chunk.interval);
        }
    });
}

setInterval(ping, 100);