# Topicos2
Servicio WEB que expone un modelo de red neuronal

![image](https://github.com/ivanDrapanti/Topicos2/assets/124262602/80660974-1203-4353-8d51-e7adae00a698)

# ADRs (Decisiones de diseño)
## Lenguaje de Programación
Debido a restricciones de la cátedra, el lenguaje utilizado es Python.
## Arquitectura de Microservicios
Se decidio darle a cada microservicio una única responsabilidad.
- Predictor: microservicio que se encarga de realizar la predición a partir de la red neuronal previamente entrenada
- DataBaseAPI: interfaz con la base de datos mongo. Encargada de realizar todas las consultas.
- Logger: microservicio encargado de generar los logs con el formato especifico.
- Authenticator: microservicio encargado de logear al usuario, devolverle el token y de validarlo.
- GateWay: microservicio de se encarga de recibir las requests y enviarlas a los respectivos endpoints.
## Caching
La llamada al predictor require mucho poder calculo. Para no llamar excesivamente a la red neuornal se decidio cashear esa llamada.
La key utilizada es la URL y el body.
## Limitación por segundo
La llamada al predictor tiene una limitacion de requests por segundo dependiendo del usuario que este ejecutando la consulta.
- Freemium: 5 request por segundo
- Preemium: 50 requests por segundo

