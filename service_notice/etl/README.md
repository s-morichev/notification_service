# Сервис ETL
Стандартный ETL
Очередь - rabbitmq http://localhost:15672
Из общего сообщения с несколькими получателями создает очередь одиночных сообщений. Если все удачно обработалось - 
удаляет сообщение из очереди. 
При начале обработки проверяет (состояние хранится в базе редис): 
1)Обрабатывалось ли ранее данное сообщение.
2)Если обрабатывалось - проверяет обрабатывался ли сообщение для каждого пользователя. Если да - то повторно не обрабатывается

