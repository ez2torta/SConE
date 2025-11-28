"""
Aquí la idea es mostrar qué podría ser un cliente AI.
en este caso se le consulta a un modelo estocástico entrenado en supercomputadoras para elegir la mejor secuencia de inputs según el estado anímico del oponente y la situación.
el modelo aun no está entrenado asi que tampoco se que cosas va a necesitar.

lo que si va a necesitar va a ser la posición actual del jugador y del oponente, la vida de ambos, y el estado anímico del oponente.
luego el modelo va a devolver una secuencia de inputs que el cliente AI debe enviar al controlador (controller.py) para que el jugador controlado por AI ejecute esos inputs.

finalmente este cliente AI debe tener la capacidad de grabar las secuencias de inputs generadas por el modelo en un archivo json
y luego reproducir esas secuencias desde el mismo cliente AI.
"""
