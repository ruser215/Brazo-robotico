#  Brazo robótico controlado por movimiento de la mano

##  Descripción del proyecto

Este proyecto consiste en el desarrollo de un brazo/mano robótica capaz de replicar en tiempo real el movimiento de una mano humana, utilizando visión por ordenador y comunicación inalámbrica.

La idea surge tras asistir al Congreso de Inteligencia Artificial de Granada, donde se presentó una mano robótica que replicaba movimientos reales. Al ver esa demostración surgió el pensamiento de que era posible desarrollar un sistema similar. Coincidiendo con la propuesta de un proyecto de clase, se decidió llevar a cabo esta idea, que fue bien recibida desde el primer momento.

---

##  Objetivo

- Capturar el movimiento de una mano humana mediante una cámara.
- Interpretar la posición de los dedos usando visión por ordenador.
- Enviar los ángulos de los dedos de forma inalámbrica.
- Replicar el movimiento en una mano robótica mediante servomotores.
- Integrar hardware y software en un proyecto real.

---

##  Equipo y reparto de tareas

- **Autor principal**
  - Conexión y control del ESP32
  - Gestión de los servomotores
  - Comunicación entre Raspberry Pi y ESP32

- **Marta**
  - Selección del modelo del brazo (modelo de Vi)
  - Impresión 3D de las piezas
  - Montaje final del brazo
  - Pintado del guante
  - Colocación de servos y cuerdas

- **Alberto**
  - Investigación de librerías de Python
  - Desarrollo del primer prototipo de reconocimiento de la mano
  - Programación de la Raspberry Pi

---

##  Tecnologías utilizadas

### Hardware
- Raspberry Pi con cámara
- ESP32
- Servomotores
- Brazo/mano impreso en 3D
- Cables soldados (sin protoboard)

### Software
- Python 3
- OpenCV
- MediaPipe
- MicroPython
- Comunicación UDP

---

## ⚙️ Arquitectura del sistema

1. La Raspberry Pi captura vídeo en tiempo real.
2. Python, junto a MediaPipe, detecta la mano y calcula los ángulos de los dedos.
3. Los ángulos se envían mediante UDP al ESP32.
4. El ESP32 recibe los datos y controla los servomotores.
5. El brazo robótico replica el movimiento de la mano.

---

##  Reconocimiento de la mano (Raspberry Pi)

El script en Python se encarga de:

- Capturar vídeo en tiempo real desde la cámara.
- Detectar una mano utilizando MediaPipe Hands.
- Calcular el ángulo de cada dedo.
- Aplicar suavizado para evitar movimientos bruscos.
- Enviar los ángulos por UDP al ESP32.
- Mostrar una interfaz visual con barras de los ángulos.
- Guardar un log de los movimientos en un archivo CSV.

### Características
- Seguimiento de una mano.
- Control independiente de los cinco dedos.
- Envío de datos a 2 Hz para mayor estabilidad.

---

##  Control de servos (ESP32)

El ESP32 ejecuta un programa en MicroPython que:

- Se conecta por Wi-Fi a la red creada por la Raspberry Pi.
- Usa una IP estática para asegurar la comunicación.
- Escucha paquetes UDP con los ángulos de los dedos.
- Convierte los ángulos en señales PWM.
- Mueve los servos correspondientes.

### Pines de los servos
- Pulgar → GPIO 15
- Índice → GPIO 16
- Medio → GPIO 17
- Anular → GPIO 18
- Meñique → GPIO 4

---

##  Problemas encontrados y soluciones

### Problema
Los servomotores no se movían todos a la vez o funcionaban de forma inestable.

### Solución
Inicialmente se pensó que el problema era la falta de voltaje. Tras investigar y gracias a la ayuda de Manolo Hidalgo, se determinó que la protoboard no transmitía correctamente la energía.  
La solución fue soldar directamente los cables, lo que solucionó completamente el problema.

---

##  Impresión 3D

- El brazo fue impreso en 3D a partir del modelo de Vi.
- El proceso requirió muchas horas de impresión.
- Hubo numerosos fallos iniciales, algo habitual al comenzar con impresión 3D.
- Finalmente se lograron imprimir todas las piezas necesarias.
- El brazo fue ensamblado y ajustado manualmente.

---

##  Resultados

- Replicación en tiempo real del movimiento de los dedos.
- Movimiento estable gracias al suavizado de ángulos.
- Integración completa de visión artificial, electrónica y control.
- Proyecto funcional y operativo.

---

##  Posibles mejoras futuras

- Mayor precisión en el reconocimiento de la mano.
- Más grados de libertad en el brazo.
- Mejor gestión de la alimentación.
- Aplicaciones en prótesis, robótica educativa o rehabilitación.

---

##  Conclusión

Este proyecto ha permitido aplicar conocimientos de programación, electrónica, visión por ordenador y redes, además de fomentar el trabajo en equipo y la resolución de problemas reales.

Ha sido una experiencia práctica y completa que ha permitido desarrollar un sistema funcional desde cero.
