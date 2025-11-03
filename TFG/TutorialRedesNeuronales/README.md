# Tutorial Redes Neuronales
El fichero best_lata.pt contiene la configuración de una red neuronal entrenada por Yolov5 para reconocer latas de bebidas (Coca Cola, Fanta, etc.)    
      
El script detect.py usa un fichero de configuración .pt para detectar el objeto correspondiente en el stream de video. Es necessario importar las librerías que se indican en el propio script.      
       
El script downloadCOCO.py permite descargar imágenes etiquetadas de los datasets de la base de datos COCO (consultar en https://cocodataset.org). En el script hay que editar el tipo de imágenes que se quiere descargar (de entre las posibles que ofrece COCO) y el número de imágenes que se desea. Es necessario importar las librerías que se indican en el propio script.     

El script genera_etiquetas.py permite generar la estructura de carpetas que necesita YOLOv5 con las etiquetas correspondientes a imágenes en las que el objeto a reconocer ocupa prácticamente toda la imagen y, por tanto, la etiqueta en realidad es toda la imagen.      
        
En esta URL se accede a un cuadarno de Google Colab ya preparado para entrenar una red neuronal con Yolov5: [yolov5 en Google Colab](https://colab.research.google.com/drive/176VhxxlNbgM_pbAI3EU_MrrYsrIyPGwb?usp=drive_link)     

Este es el repositorio del software LabelImg, que puede usarse para etiquetar imágenmes: https://github.com/HumanSignal/labelImg

    
