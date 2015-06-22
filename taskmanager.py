# coding=utf-8
import uuid
import time


class Worker:
    """
    Класс Воркер является отражением реального воркера.
    Класс содержит в себе информацию про свою занятость и время последнего отклика.
    """
    TIME_OUT = 5000

    def __init__(self, workerId):
        self.workerId = workerId
        self.chunkId = None
        self.taskId = None
        self.lastPing = 0

    def getWorkerId(self):
        """
        Возвращает ID воркера
        """
        return self.workerId

    def getChunkId(self):
        """
        Возвращает ID кусочка которым занят воркер
        """
        return self.chunkId

    def getTaskId(self):
        """
        Возвращает ID задания которым занят воркер
        """
        return self.taskId

    def setChunkId(self, chunkId):
        """
        Устанавливает ID кусочка которым будет занят воркер
        """
        self.chunkId = chunkId

    def setTaskId(self, taskId):
        """
        Устанавливает ID задания которым будет занят воркер
        """
        self.taskId = taskId

    def getLastPing(self):
        """
        Возвращает время последнего отклика
        """
        return self.lastPing

    def updateLastPing(self):
        """
        Обновляет время последнего отклика(устанавливает текущее)
        """
        self.lastPing = int(time.time() * 1000)

    def isTimeOut(self):
        """
        Возвращает True если воркер не отвечал слишком долго
        """
        return self.lastPing + Worker.TIME_OUT < int(time.time() * 1000)


class Chunk:
    """
    Класс Кусочек является отраженим небольшой части большого задания.
    """

    def __init__(self, interval):
        self.result = -1
        self.inProgress = False
        self.complete = False
        self.chunkId = str(uuid.uuid4())
        self.json = {'interval': interval}
        self.interval = interval

    def isComplete(self):
        """
        Возвращает True если кусочек вычислен
        """
        return self.complete

    def isInProgress(self):
        """
        Возвращает True если кусочек в процессе вычисления
        """
        return self.inProgress

    def getJson(self):
        """
        Возвращает JSON представление кусочка
        """
        return self.json

    def getResult(self):
        """
        Возвращает результат вычисления кусочка
        """
        return self.result

    def setResult(self, result):
        """
        Устанавливает результат вычисления кусочка
        """
        self.result = result

    def getChunkId(self):
        """
        Возвращает ID кусочка
        """
        return self.chunkId

    def getInterval(self):
        """
        Возвращает интервал вычисления
        """
        return self.interval

    def setComplete(self, complete):
        """
        Устанавливает состояние законченности вычисления (законченно или нет)
        """
        self.complete = complete

    def setInProgress(self, inProgress):
        """
        Устанавливает состояние вычисления (в процессе или нет)
        """
        self.inProgress = inProgress


class Task:
    """
    Класс Задание является отражением реального задания.
    Класс содержит в себе информацию про свою законченность, состояние каждого кусочка, методы для удобной работы.
    """
    def __init__(self, intervals):
        self.intervals = intervals
        self.taskId = "%x" % str(intervals).__hash__()
        self.startTime = int(time.time() * 1000)
        self.totalTime = -1
        self.chunks = [Chunk(interval) for interval in intervals]

    def getIntervals(self):
        """
        Возвращает интервалы вычисления
        """
        return self.intervals

    def getChunk(self, chunkId):
        """
        Возвращает кусочек с заданым ID
        """
        return next((c for c in self.chunks if c.chunkId == chunkId), None)

    def getAnyChunk(self):
        """
        Возвращает первый кусочек готовый к вычислению на воркере
        """
        chunk = next((c for c in self.chunks if
                      not (c.isComplete() or c.isInProgress())), None)

        if chunk is not None:
            chunk.setInProgress(True)

        return chunk

    def setResult(self, chunkId, value):
        """
        Устанавливает результат вычисления кусочка с заданым ID
        """
        chunk = self.getChunk(chunkId)
        chunk.setComplete(True)
        chunk.setInProgress(False)
        chunk.setResult(value)

    def setInProgress(self, chunkId, flag):
        """
        Устанавливает состояния вычисления кусочка с заданым ID
        """
        self.getChunk(chunkId).setInProgress(flag)

    def isComplete(self):
        """
        Возвращает состояние законченности вычисления задания (законченности или нет)
        """
        chunk = next((c for c in self.chunks if not c.isComplete()), None)

        if chunk is None and self.totalTime == -1:
            self.totalTime = int(time.time() * 1000) - self.startTime

        return chunk is None

    def getTotalTime(self):
        """
        Возвращает время затраченное на выполение задания
        """
        return self.totalTime

    def getChunksResult(self):
        """
        Возвращает список результатов каждого кусочка
        """
        return list({'chunkId': c.getChunkId(),
                     'interval': c.getInterval(),
                     'result': c.getResult()} for c in self.chunks)

    def getChunksState(self):
        """
        Возвращает список состояний каждого кусочка
        0 - не выполнен и не в процессе
        1 - в процессе
        2 - выполнен
        """
        return list({'chunkId': c.getChunkId(),
                     'state': (1 if c.isInProgress() else 0) | (
                     2 if c.isComplete() else 0)} for c in self.chunks)

    def equal(self, intervals):
        """
        Возврашает True если интервалы этого задания совпадают с аргументом
        """
        return self.intervals == intervals

    def getTaskId(self):
        """
        Возвращает ID задания
        """
        return self.taskId

# TaskManager

taskList = []
workerList = []


def getWorker(workerId):
    """
    Возвращает воркер с заданным ID
    """
    return next((w for w in workerList if w.getWorkerId() == workerId), None)


def addWorker(workerId):
    """
    Создает новый воркер(с заданным ID) и добавляет его в общий список воркеров
    """
    workerList.append(Worker(workerId))


def removeWorker(worker):
    """
    Удаляет конкретный воркер из общего списка воркеров
    """
    workerList.remove(worker)


def removeLostWorkers():
    """
    Удаляет из обшего списка воркеры которые превысили интервал ожидания.
    Если воркер находился в процессе выполнения то кусочек который он выполнял возвращает в состояние ожидания.
    """
    for w in [w for w in workerList if w.isTimeOut()]:
        if w.getTaskId() is not None:
            getTask(w.getTaskId()).setInProgress(w.getChunkId(), False)
        workerList.remove(w)


def getTask(taskId):
    """
    Возвращает задание с заданным ID, или None если такого задания нет
    """
    return next((t for t in taskList if t.getTaskId() == taskId), None)


def getTaskByInput(intervals):
    """
    Возвращает задание по заданным интервалам, или None если такого задания нет
    """
    return next((t for t in taskList if t.equal(intervals)), None)


def getAnyTask():
    """
    Возвращает первое задание готовое к вычислению на воркерах
    """
    return next((t for t in taskList if not t.isComplete()), None)


def addTask(intervals):
    """
    Создает новое задание с заданными интервалами и добаляет его в список всех заданий
    """
    taskList.append(Task(intervals))


def getTaskList():
    """
    Возвращает список заданий
    """
    return taskList


def getWorkerList():
    """
    Возвращает список воркеров
    """
    return workerList