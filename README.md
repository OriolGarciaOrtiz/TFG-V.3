# Contribución al Dron Engineering Ecosysten

---

## 1. Descripción General
Este proyecto ha sido desarroyado por Joel Gallego Martínez y Oriol Garcia Ortiz con el fin de contribuir
al DEE y poder realizar el Trabajo de Fin de Grado. Los objetivos principales de este proyecto son el 
aprendizaje de mecánicas de vuelo del dron Tello y Hexsoon. Adicionamente, el funcionamiento, entrenamiento y 
uso de una red neuronal usando la librería YOLO, de ultralytics.

> El funcionamiento de todos los modos de juego se puede visualizar en esta lista de reproducción de YouTube: 
  https://youtube.com/playlist?list=PLEDvvJLAUGwQ_S-6sIdhHBwzNW8z98UUb&si=ZSrLJ2k3TwoOOod7

---

## 2. Arquitectura del Proyecto
Este proyecto se ha dividido en dos fases principales. Una primera en la cual se desarroyaron modos de juego relacionados
con el dron Tello, los cuales se basan en el seguimiento automático de una raqueta de color o con el uso de una red neuronal 
el seguimiento de un coche teledirigido. Y en la segundo fase, se implementaron dos de los modos de juego previos al dron
Hexsoon, con la principal diferencia de que las librerías usadas para el control del dron son distintas, adicionalmente, se usará 
Mission Planner como aplicación principal para la comunicación con el dron.


- **Lenguajes:** ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) 
  ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)

- **Protocolos y Comunicación:** ![MQTT](https://img.shields.io/badge/MQTT-3C3C3C?style=flat&logo=mqtt&logoColor=white) 
  ![WebRTC](https://img.shields.io/badge/WebRTC-333333?style=flat&logo=webrtc&logoColor=white)


### 2.1 Tello Dron
Se han diseñado e implementado cuatro modalidades de juego principales que combinan la visión por computador clásica con técnicas de inteligencia artificial modernas. Estas modalidades se ejecutan procesando la señal de video del Tello en tiempo real:

* **Seguimiento por Color (Raqueta):** Utiliza algoritmos de visión por computador (OpenCV) para detectar contornos y colores específicos (verde y azul). El dron ajusta su posición (yaw y altura) para mantener el objeto centrado.
* **Seguimiento de Coche RC (YOLO):** Implementación de una red neuronal entrenada con YOLOv8 para detectar un coche de radiocontrol. El sistema calcula el centroide del objeto detectado y envía comandos de vuelo para perseguirlo.
* **Seguimiento Dinámico (Web App):** Variación del modo anterior donde el objetivo (coche RC) cambia de color dinámicamente controlado por una aplicación web. El dron reacciona realizando acciones específicas según el color detectado.
* **Seguimiento de Animales (Web App, YOLO):** Uso de una red neuronal entrenada para clasificar entre cuatro tipos de animales diferentes, desencadenando maniobras de vuelo distintas según la clase identificada.

Adicionalmente algunos de estos modos de juego se han podido reutilizar en el circo de drones (https://github.com/dronsEETAC/TelloDroneCircus), un repositorio con un efoque pedagógico en el cual se pueden encontrar
varios modos de juego los cuales se basan en distintas arquitecturas, como el reconocimiento de una pose con el cuerpo, juegos como ping-pong, reconocimiento de imagenes...

### 2.2 Hexsoon Dron
La integración con el dron Hexsoon EDU-450 representa la adaptación del sistema para vuelos en exteriores y plataformas de mayor envergadura. Las características principales de esta fase incluyen:

* **Adaptación de Algoritmos:** Migración de los modos de seguimiento de color y seguimiento con red neuronal probados en el Tello.
* **Integración con Mission Planner:** Se utiliza Mission Planner como estación de tierra principal para la telemetría y supervisión, estableciendo la comunicación mediante protocolos estándar para drones basados en ArduPilot/Pixhawk.

En este caso, únicamente se incorporaron los modos de juego seguimiento de un color en una raqueta y seguimiento de un coche RC a pratir de una red neuronal.

#### 2.2.1 Raspberry pi
Adicionalmente, se desarroyó la opción de poder ejecutar el código en una Raspberry Pi, para poder ejecutar todos los códigos a bordo del dron, de esta manera se mejorará la eficiencia de cálculo. Este se encontrará en la 
carpeta Hexsoon/Raspberry Pi. Para este modo es imprescindible tener conexión Wifi. Fara facilitar las pruebas en tierra, se puede ejecutar el siguiente comando:
```bash
ssh raspberrypi@ip
```
donde raspberrypi es el nombre el cual se ha usado para registrarse en la raspberry al instalar el sistema operativo, y ip es la dirección para poder conectarse de forma remota. Por ejemplo:
```bash
ssh oriolgarciaortiz@192.168.1.101
```

Gracias a esto nos podreos conectar a la Raspberry remotamente, con la condición de que se debe estar conectadó al mismo Wifi. También es importante remarcar que esta conecxión solo permite comandos 
por terminal, por lo tanto, es recomendable realizar todas las pruebas en el ordenador, y posteriormente clonar el repositorio directamente en la Raspberry. Para poder ejecutar el codigo de la raspberry
se debe ir hasta la carpeta Hexsoon/'Raspberry Pi' y ejecutar el codigo **main.py** con el comando. 
```bash
python main.py
```

## 2.3 Material Adicional
Durante el proceso de la realización de este proyecto, hubo momentos en los cuales había tareas pesadas o mecánicas como crear un dataset de imagenes para el entrenamiento de la red neuronal que requería de muchas fotos,
por lo tanto se crearon varios scripts que ayudaron a la automatización de estas tareas. Y se decidió que todos estos scripts se incluyeran en una carpeta própia.

## 2.4 WebApp Flask
Para los modos de juego de Tello que requieren que más de un usuario pueda participar, se creo una webapp senzilla. Esta contiene fotos de colores animales, las cuales el dron debe detectar y seguir a partir del centro de la imagen detectada. Es importante mencionar que los dos usuarios que usen la webbapp deben estar conectados al mismo Wifi

## 2.5 Modelos Yolo
Finalmente, se podrá observar una carpeta llamada Yolo Models, en la cual se pueden encontrar distintos modelos entrenados para la red neuronal con extesión .pt. Es recomendable que en caso de que se quieran agregar más modelos, depositarlos todos en esta carpeta.

---

## 3. Requisitos Técnicos e Instalación

Para ejecutar este proyecto en un entorno local, es necesario disponer de las siguientes herramientas y librerías.

### 3.1 Requisitos Previos
* Python 3.8 o superior.
* Conexión Wi-Fi para la comunicación con el dron Tello.
* Antena de telemetría o conexión directa para el dron Hexsoon.

### 3.2 Librerías Principales
El proyecto depende de los siguientes paquetes de Python, listados en el archivo `requirements.txt`:

* **opencv-python:** Para el procesamiento de imágenes, conversión a espacios de color HSV y detección de contornos.
* **ultralytics:** Para la implementación, carga y ejecución de los modelos de redes neuronales YOLOv8.
* **djitellopy:** SDK para la comunicación y envío de comandos al dron Tello.
* **pymavlink / dronekit:** Para la comunicación vía protocolo MAVLink con el dron Hexsoon.
* **paho-mqtt:** Para la gestión de la mensajería en la arquitectura del Drone Engineering Ecosystem.

---

## 4. Control y Algoritmos

### 4.1 Control PID
Para garantizar un movimiento fluido y evitar oscilaciones bruscas durante el seguimiento de objetos, se han implementado controladores PID (Proporcional-Integral-Derivativo).

* El controlador calcula el error entre el centro de la imagen y el centroide del objeto detectado.
* Se ajustan las velocidades de *yaw* (rotación), *pitch* (avance/retroceso) y *throttle* (altura) en tiempo real para minimizar dicho error.

### 4.2 Redes Neuronales (YOLOv8)
El entrenamiento de los modelos se ha realizado utilizando datasets personalizados y pre-etiquetados (por ejemplo, mediante COCO).
* **Entrenamiento:** Se han ajustado los hiperparámetros (épocas, tamaño de lote) para optimizar la precisión de detección en tiempo real.
* **Detección:** El sistema procesa cada *frame* capturado por la cámara del dron, dibuja las *bounding boxes* y extrae las coordenadas para el sistema de control.

---

## 5. Ejecución

1.  Clonar el repositorio.
    ```bash
    git clone https://github.com/OriolGarciaOrtiz/TFG-V.3.git
    ```

2. Crear un entorno virtual y activarlo.
    ```bash
    python -m venv venv
    ```
    
    ```bash
    Si se está usando Windows:
    
    venv/Scripts/activate
    ```
    ```bash
    Si se está usando Linux/Raspberry Pi:
    
    source venv/bin/activate
    ```

3.  Instalar las librerías.
    ```bash
    pip install -r requirements.txt
    ```

4.  Conectar el dispositivo a la red Wi-Fi del Tello o establecer conexión telemétrica con el Hexsoon.

5.  Ejecutar el script principal **main.py**, dependiendo del dron que se quiera usar.

---

## 6. Autores y Agradecimientos
Este trabajo ha sido realizado por **Joel Gallego Martínez** y **Oriol Garcia Ortiz** bajo la tutela de **Miguel García Valero**. Agradecimientos especiales al entorno DEE por proporcionar la infraestructura y soporte necesarios para el desarrollo de estas aplicaciones.
