# coding=utf-8
import json
import taskmanager
from bottle import get, post, run, static_file, hook, request


@hook('before_request')
def any_request():
    """
    Удаляет воркеры превысили интервал ожидания, выполняет перед каждым запросом
    """
    taskmanager.removeLostWorkers()


@get('/lab2')
@get('/lab2/')
def show_index():
    """
    Возвращает главную страницу
    """
    return static_file("index.html", root="pages")


@get('/lab2/admin')
def show_admin():
    """
    Возвращает админку
    """
    return static_file("admin.html", root="pages")


@get('/lab2/res/<filepath:path>')
def server_static(filepath):
    """
    Возвращает ресурсы (css, js, img ...)
    """
    return static_file(filepath, root='pages/resources')


@get('/lab2/api/worker-ping/<workerId>/<state>')
def getPing(workerId, state):
    """
    Принимает сообщение от воркера и обновляет его состояние
    """
    worker = taskmanager.getWorker(workerId)

    if worker is None:
        taskmanager.addWorker(workerId)
        worker = taskmanager.getWorker(workerId)

    if int(state) == 0:
        anyTask = taskmanager.getAnyTask()

        if anyTask is not None:
            anyChunk = anyTask.getAnyChunk()

            if anyChunk is not None:
                worker.setChunkId(anyChunk.getChunkId())
                worker.setTaskId(anyTask.getTaskId())
                worker.updateLastPing()

                return json.dumps({'hasTask': True,
                                   'taskId': worker.getTaskId(),
                                   'chunkId': worker.getChunkId(),
                                   'chunk': anyChunk.getJson()})

        worker.setTaskId(None)
        worker.setChunkId(None)

    worker.updateLastPing()

    return json.dumps({'hasTask': False})


@get('/lab2/api/worker-post/<workerId>/<taskId>/<chunkId>/<result>')
def updateTask(workerId, taskId, chunkId, result):
    """
    Устанавливает результат для выполненого кусочка
    """
    taskmanager.getWorker(workerId).updateLastPing()
    taskmanager.getTask(taskId).setResult(chunkId, result)
    return json.dumps({'isOk': True})


@get('/lab2/api/get-task/<taskId>')
def check(taskId):
    """
    Возвращает состояние задания с заданным ID
    """
    task = taskmanager.getTask(taskId)

    if task.isComplete():
        return json.dumps({'isComplete': True,
                           'taskId': task.getTaskId(),
                           'result': task.getChunksResult()})

    return json.dumps({'isComplete': False,
                       'taskId': task.getTaskId()})


@get('/lab2/api/admin/get-tasks')
def adminGetTasks():
    """
    Возвращает подробное состояние всех заданий
    """
    return json.dumps({'tasks': [{'taskId': t.getTaskId(),
                                  'intervals': t.getIntervals(),
                                  'result': t.getChunksResult(),
                                  'time': t.getTotalTime(),
                                  'state': t.getChunksState()} for t in taskmanager.getTaskList()]})


@get('/lab2/api/admin/get-workers')
def adminGetWorkers():
    """
    Возвращает подробное состояние всех воркеров
    """
    return json.dumps({'workers': [{'workerId': w.getWorkerId(),
                                    'taskId': str(w.getTaskId()),
                                    'chunkId': str(w.getChunkId()),
                                    'lastPing': w.getLastPing()} for w in taskmanager.getWorkerList()]})


@post('/lab2/api/set-task')
def calcTask():
    """
    Добавляет новое задание для вычисление.
    Если задание уже было вычислено то сразу возвращает результат.
    """
    intervals = json.loads(request.forms.get('intervals'))

    task = taskmanager.getTaskByInput(intervals)

    if task is None:
        taskmanager.addTask(intervals)
        task = taskmanager.getTaskByInput(intervals)

    if task.isComplete():
        return json.dumps({'isComplete': True,
                           'taskId': task.getTaskId(),
                           'result': task.getChunksResult()})

    return json.dumps({'isComplete': False,
                       'taskId': task.getTaskId()})


# run(host='localhost', port=8080, debug=True)