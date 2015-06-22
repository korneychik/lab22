var lab2 = lab2 || {};
(function (lab) {

    //**********************   AJAX   **************************

    lab.xmlHttp = null;
    lab.callback = null;

    lab.getXmlHttp = function () {
        if (lab.xmlHttp === null) {
            lab.xmlHttp = new XMLHttpRequest();
            lab.xmlHttp.onreadystatechange = function () {
                if (lab.xmlHttp.readyState === 4 && lab.xmlHttp.status === 200) {
                    lab.callback(lab.xmlHttp.responseText);
                }
            };
        }

        return lab.xmlHttp;
    };

    lab.callback = null;

    lab.doGet = function (url, callback) {
        lab.xmlHttp.open("GET", url, true);
        lab.callback = callback;
        lab.xmlHttp.send();
    };

    lab.doPost = function (url, data, callback) {
        lab.xmlHttp.open("POST", url, true);
        lab.callback = callback;
        lab.xmlHttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
        lab.xmlHttp.send(data);
    };

    lab.worker = null;

    //**********************   WORKER   **************************

    lab.startWorker = function () {

        if (typeof (Worker) !== "undefined") {
            lab.worker = new Worker("/lab2/res/js/worker.js");
        } else {
            console.log("Sorry, no workers available =(");
        }
    };

    lab.checkIntervalID = null;
    lab.checkIntervalDelay = 500;

    //**********************   INIT   **************************

    lab.getIntervals = function() {

        var res = [];

        $(".interval").toArray().forEach(function (item) {

                var obj = {};

                obj.a = Number($(item).find(".a").val());
                obj.b = Number($(item).find(".b").val());
                obj.s = Number($(item).find(".s").val());

                res.push(obj);
        });

        return res;
    };

    lab.setResult =  function(res) {

        var html = "";
        res.forEach(function (item) {

            html += "<tr>"+
                    "<td>" + item.result + "</td>"+
                    "<td>" + item.interval.a + "</td>"+
                    "<td>" + item.interval.b + "</td>"+
                    "<td>" + item.interval.s + "</td>"+
                    "</tr>";
        });

        document.getElementById("result").innerHTML = html;
    };

    window.addEventListener("load", function () {

        lab.getXmlHttp();
        lab.startWorker();

        document.getElementById("post").addEventListener("click", function () {
            var data = "intervals=" + JSON.stringify(lab.getIntervals());

            lab.doPost("/lab2/api/set-task", encodeURI(data), function (data) {
                var json = JSON.parse(data);
                console.log("doPOST", json);
                if (json.isComplete) {
                    lab.setResult(json.result);
                } else {
                    document.getElementById("result").value = "Зачекайте будь ласонька...";

                    clearInterval(lab.checkIntervalID);
                    lab.checkIntervalID = setInterval(function (id) {
                        lab.doGet("/lab2/api/get-task/" + id, function (data) {
                            var json = JSON.parse(data);
                            console.log("doGET", json);
                            if (json.isComplete) {
                                clearInterval(lab.checkIntervalID);
                                lab.setResult(json.result);
                            }
                        });
                    }, lab.checkIntervalDelay, json.taskId);
                }
            });
        });

    });

})(lab2);
