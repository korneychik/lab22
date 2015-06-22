var xhrTasks = new XMLHttpRequest();
var xhrWorkers = new XMLHttpRequest();

var templateTasks = "<tr><td>%taskId%</td>" +
        "<td><p class=\"clip\">%intervals%</p></td>" +
        "<td><p class=\"clip\">%result%</p></td>" +
        "<td>%time%</td>" +
        "<td>%progress%</td></tr>";

xhrTasks.onreadystatechange = function () {
    if (xhrTasks.readyState === 4 && xhrTasks.status === 200) {
        var json = JSON.parse(xhrTasks.responseText);

        var html = "";
        json.tasks.forEach(function (item) {

            var progress = item.state.filter(function (item) {
                if (item.state === 2) {
                    return item;
                }
            }).length / item.state.length;

            console.log(item);

            html += templateTasks
                    .replace("%taskId%", item.taskId)
                    .replace("%intervals%", JSON.stringify(item.intervals))
                    .replace("%result%", JSON.stringify(item.result.map(function (item) { return item.result})))
                    .replace("%time%", item.time + "мс")
                    .replace("%progress%", (progress * 100).toFixed(2) + "%");
        });

        document.getElementById("tasks").innerHTML = html;
    }
};

var templateWorkers = "<tr><td>%workerId%</td>" +
        "<td>%taskId%</td>" +
        "<td>%chunkId%</td>" +
        "<td>%lastPing%</td></tr>";

xhrWorkers.onreadystatechange = function () {
    if (xhrWorkers.readyState === 4 && xhrWorkers.status === 200) {
        var json = JSON.parse(xhrWorkers.responseText);

        var html = "";
        json.workers.forEach(function (item) {
            html += templateWorkers
                    .replace("%workerId%", item.workerId.substr(0, 13))
                    .replace("%taskId%", item.taskId)
                    .replace("%chunkId%", item.chunkId.substr(0, 8))
                    .replace("%lastPing%", (Date.now() - item.lastPing) + "мс");
        });

        document.getElementById("workers").innerHTML = html;
    }
};

function updateWorkers() {
    xhrWorkers.open("GET", "api/admin/get-workers", true);
    xhrWorkers.send();
}

function updateTasks() {
    xhrTasks.open("GET", "api/admin/get-tasks", true);
    xhrTasks.send();
}

setInterval(updateWorkers, 500);
setInterval(updateTasks, 750);