from getpass import getpass
from mysql.connector import connect, Error
import numpy as np

class Fuzzy:
# Конструктор класса
    def __init__(self, inp: str, inFuncs: list, outFuncs: list, outRevFuncs: list) -> None:
        self. inp = inp # Вводная строка
        self. rules = list() # Выходной список
        self. inFuncs = inFuncs.copy() # Список функций, входящих в ФП входной переменной
        self. outFuncs = outFuncs.copy() # Список функций, входящих в ФП выходной переменной
        self. outRevFuncs = outRevFuncs.copy() # Список обратных функций (f(y)), входящих в ФП выходной переменной
        self. queryResult = list() # Результат запроса
        self. inData = list() # Преобразованные данные на вход алгоритма
        # Преобразование строки базы правил в список для дальнейшей работы
    def rulesStringToList(self) -> list:
    # Разбиение входной строки по символам переноса строки
        self. rules = self.__inp.split("\n")
        # Преобразование каждой строки в список чисел
        for i in range(len(self.__rules)):
            self. rules[i] = [int(x) for x in self. rules[i]]   
    # Генерация понятной базы правил
    def generateRules(self) -> None:
    
        """
            limit = [Небольшой, Средний, Высокий]
            time = [Мало, Средне, Много]
            raiting = [Низкий, Средний, Большой]
            class = [Плохо, Ниже среднего, Выше среднего, Отлично]
        """

        t = list()
        i = 0
        for element in self.__rules:
            t.clear()
            i += 1
            t.append(["Небольшой", "Средний", "Высокий"][element[0] - 1])
            t.append(["Мало", "Средне", "Много"][element[1] - 1])
            t.append(["Низкий", "Средний", "Большой"][element[2] - 1])
            t.append(["Плохо", "Ниже среднего", "Выше среднего", "Отлично"][element[3] - 1])
            print(f"ПРАВИЛО №{i}: ЕСЛИ limit=({t[0]}) И time=({t[1]}) И raiting=({t[2]}) ТОГДА class=({t[3]})")
    # Получение данных из БД
    def getDBData(self):
        try:
            # Подключение к БД
            with connect( 
                host="localhost", 
                user=input("Введите имя пользователя БД (default=root): "),
                password=getpass("Пароль пользователя: "),
                database="zp"
            ) as connection:
            # Выполняемый запрос
                dbQuery = "SELECT * FROM salaries"
            # Преобразование результата запроса в список
                with connection.cursor() as cursor:
                    cursor.execute(dbQuery)
                    for db in cursor:
                        self. queryResult.append(db)
        except Error as e:
            print(e)
    # Преобразование входных данных перед использованием
    def preProcess(self) -> None:
        for element in self.__queryResult:
            limit = (float(element[4]) - 8000) / 3200
            time = (float(element[5]) - 7) / 2.3
            raiting = (float(element[6]) - 6) / 0.4
            # Проверка что данные не выходят за интервал [0; 10]
            if not 0 <= limit <= 10 or not 0 <= time <= 10 or not 0 <= raiting <= 10:
                print([limit, time, raiting])
                print("Ошибка генерации входных значений")
                return self. inData.append([ (float(element[4]) - 8000) / 3200, (float(element[5]) - 7) / 2.3,
                    (float(element[6]) - 6) / 0.4])
    # Выполнение основного алгоритма
    def process(self) -> None:
        # Если на этапе преобразования данных произошла ошибка, то длина списков будет разной
        if len(self.__queryResult) != len(self.__inData):
            print("На этапе генерации входных данных произошла ошибка")
            return 
        i = 0
        print("\nРезультат выполнения алгоритма:\n")
        for inData in self. inData:
            upper = 0
            lower = 0
            funcs = self. inFuncs
            outFuncs = self. outFuncs 
            outRevFuncs = self. outRevFuncs 
            for rule in self. rules:
                fuzzy = [funcs[rule[i] - 1](inData[i]) for i in range(len(inData))]
                minFuzzy = min(fuzzy)
                z0 = outRevFuncs[rule[-1] - 1](minFuzzy)
                if z0 > 10:
                    z0 = 10
                if z0 < 0:
                    z0 = 0
                upper += (minFuzzy*z0) 
                lower += minFuzzy

            x = upper / lower
            temp = [f(x) for f in outFuncs] 
            answer = max(temp)
            print(f'[{self. queryResult[i][1]} {self. queryResult[i][2]}
            {self. queryResult[i][3]}] - {["Плохо", "Ниже среднего", "Выше среднего", "Отлично"][temp.index(answer)]}' )
            i += 1
    
    def run(self):
        self.generateRules()	# Вывод баз правил
        self.rulesStringToList()	# Преобразование правил из строки список
        self.getDBData()	# Получение данных из БД
        self.preProcess()	# Преобразование данных
        self.process()
    
    # Гауссовское (нормальное) распределение
gauss = lambda k, x, phi, sigma: k / (sigma*np.sqrt(2*np.pi)) * np.exp(- 1/2* np.power((x-phi)/sigma, 2))

# Обратная функция Гаусса (f(y)). "Left" и "Right" потому, что прямая y = k пересекает функцию дважды,
# Поэтому учитывается либо левый кусок функции, либо правый

revGaussLeft = lambda k, y, phi, sigma: -np.sqrt(-2 * np.power(sigma, 2)* np.log(y*sigma*np.sqrt(2*np.pi)/k)) + phi

revGaussRight = lambda k, y, phi, sigma: np.sqrt(-2 * np.power(sigma, 2)* np.log(y*sigma*np.sqrt(2*np.pi)/k)) + phi

# Входное нечеткое множество
inputM = lambda x: gauss(1 / gauss(1, 0, 0, 1.5), x, 0, 1.5)
inputS = lambda x: gauss(1 / gauss(1, 0, 0, 1.5), x, 5, 1.5)
inputD = lambda x: gauss(1 / gauss(1, 0, 0, 1.5), x, 10, 1.5)

# Выходное нечеткое множество
output1 = lambda x: gauss(1 / gauss(1, 0, 0, 3), x, 0, 3)
output2 = lambda x: gauss(1 / gauss(1, 0, 0, 3), x, 2, 3)

output5	=	lambda	x:	gauss(1	/	gauss(1,	0,	0,	3), x, 8, 3)
output6	=	lambda	x:	gauss(1	/	gauss(1,	0,	0,	3), x, 10, 3)
output7 =	lambda	x:	gauss(1	/	gauss(1,	0,	0,	2.2), x, 3, 2.2) if x >= 3 else 0
output8 =	lambda	x:	gauss(1	/	gauss(1,	0,	0,	2.2), x, 7, 2.2) if x <= 7 else 0

# Обратное выходное нечеткое множество
revOutput1 = lambda y: revGaussRight(1 / gauss(1, 0, 0, 3), y, 0, 3)
revOutput2 = lambda y: revGaussRight(1 / gauss(1, 0, 0, 3), y, 2, 3)
revOutput5 = lambda y: revGaussRight(1 / gauss(1, 0, 0, 3), y, 8, 3)
revOutput6 = lambda y: revGaussLeft(1 / gauss(1, 0, 0, 3), y, 10, 3)
revOutput7 = lambda y: revGaussRight(1 / gauss(1, 0, 0, 2.2), y, 3, 2.2)
revOutput8 = lambda y: revGaussLeft(1 / gauss(1, 0, 0, 2.2), y, 7, 2.2)

        # База правил
inp = """1111
1123
1134
2111
2123
2134
2212
2223
2234
3111
3123
3134
3211
3222
16
3234
3312
3322
3333"""
inFuncs = [inputM, inputS, inputD]
outFuncs = [output1, output2, output7,output8, output5, output6]
outRevFuncs = [revOutput1, revOutput2,revOutput7,revOutput8, revOutput5, 
revOutput6]
# Создание объекта основного класса
payload = Fuzzy(inp, inFuncs, outFuncs, outRevFuncs)
# Запуск
payload.run()




