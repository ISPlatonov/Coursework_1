def update_settings():
    import pandas as pd
    data = pd.read_excel('ex_students.xlsx')
    greentime = int(data['Green'][0])
    redtime = int(data['Red'][0])
    time_s = int(data['Sdvig'][0])
    part_screen = 480 - int(data['Part'][0]*0.01*480)
    return greentime,redtime,time_s,part_screen
    
def cam_1(face_id):
    import os
    import cv2

    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # установка ширины видео
    cam.set(4, 480) # установка высоты видео

    path = os.getcwd() + '/..' # директория приложения

    # Детектор лиц в библиотеке opencv
    face_detector = cv2.CascadeClassifier(path + '/libraries/opencv/build/etc/haarcascades/haarcascade_frontalface_default.xml')   

    print("Initializing face capture. Look the camera and wait ...")
    # Инициализация переменной для подсчёта количества фото
    count = 0

    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)     
            count += 1

            # Сохранение изображения лица в базу данных
            cv2.imwrite(path + "/dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

            cv2.imshow('image', img)

        k = cv2.waitKey(100) & 0xff # 'ESC' для остановки
        if k == 27:
            break
        elif count >= 30: # остановка записи при сделанных 30 фото
             break

    # Закрытие окон записи
    print("Exiting Capure program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()

    trainer_0() # Перезапись файла распознавания

def cam_2():
    import cv2
    import numpy as np
    import os
    import time
    import pandas as pd

    path = os.getcwd() + '/..' # директория приложения

    names = UpdateNames()   # Загрузка имён из списка студентов Excel
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(path + '/trainer/trainer.yml')
    cascadePath = path + '/libraries/opencv/build/etc/haarcascades/haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascadePath);

    font = cv2.FONT_HERSHEY_SIMPLEX

    id = 0  # Объявление переменной id

    # Начало видеозахвата
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height

    # Минимальный размер окна, который может быть распознан как лицо
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    # Время горения
    greentime,redtime,time_s,part_screen = update_settings()
    
    
    #greentime = 20  # зелёный свет
    #redtime = 10   # красный свет
    #time_s = 1583769600    # Время начала (18:00 09.03.2020) в секундах
    itrn = 0    # Количество итераций за цикл
    timedict = {}   # Список нарушений (количество итераций в зоне) за период горения красного
    
    while True:
        ret, img = cam.read()
        if (time.time() - time_s) % (greentime + redtime) < redtime:
            #print(time.time())
            itrn += 1
            
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            
            faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 5, minSize = (int(minW), int(minH)),)

            for(x,y,w,h) in faces:
                # Координаты центра лица
                center_x = x + w / 2    # X
                center_y = y + h / 2    # Y
                
                # Запись при расположении лица ниже середины экрана (дописать)
                if center_y > part_screen:  
                    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                    id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                    
                    # Проверка уверенности (меньше 100 - опознан, 0 - совершенная уверенность)
                    if (confidence < 100):
                        name = names[id]
                        confidence = "  {0}%".format(round(100 - confidence))
                        if id in timedict:
                            timedict[id] += 1
                        else:
                            timedict[id] = 1
                    else:
                        name = "unknown"
                        confidence = "  {0}%".format(round(100 - confidence))
                    
                    cv2.putText(img, str(name) + ' ' + str(id), (x+5,y-5), font, 1, (255,255,255), 2)
                    cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)

        else:
            # Время горения красного света вышло,
            # запускается цикл записи нарушивших в БД
            if itrn > 30:   # Нижний порог для запуска записи (30)
                data = pd.read_excel('ex_students.xlsx')
                #print(itrn)
                porog = itrn * 3 // redtime     # Нижний порог для записи нарушения (около 3 секунд в зоне)
                for key in timedict:
                    if timedict[key] >= porog:
                        for i in range(len(data['id'])):
                            if data['id'][i]==key:
                                data['Deviations'][i] = int(data['Deviations'][i])+1 
                                #print(key)     # id нарушавего
                                break
        
                data.to_excel('ex_students.xlsx', index = False)     # Запись нарушений в базу данных 
            #Сброс счётчиков
            if itrn != 0:   
                itrn = 0
            timedict = {}
        
        cv2.imshow('camera', img) 

        k = cv2.waitKey(10) & 0xff # 'ESC' для остановки
        if k == 27:
            break

    # Закрытие окон
    #print("Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()

def trainer_0():
    import cv2
    import numpy as np
    from PIL import Image
    import os

    path = os.getcwd() + '/..' # Директория приложения
    path_ds = path + '/dataset'   # Путь к базе изображений лиц

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(path + '/libraries/opencv/build/etc/haarcascades/haarcascade_frontalface_default.xml');

    # Функция записи лица с созданием ярлыка
    def getImagesAndLabels(path_ds):
        imagePaths = [os.path.join(path_ds, f) for f in os.listdir(path_ds)]   # Изображения лиц
        faceSamples=[]
        ids = []
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L')    # Конвертирование изобр. в чёрно-белое
            img_numpy = np.array(PIL_img,'uint8')
            #print(os.path_ds.split(imagePath)[-1].split(".")[1])
            face_id = int(os.path.split(imagePath)[-1].split('.')[1])
            faces = detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(face_id)
        #print(ids)
        return faceSamples, ids

    print ("Training faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(path_ds)
    recognizer.train(faces, np.array(ids))

    # Сохранение лица в trainer/trainer.yml
    recognizer.write(path + '/trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi

    # Вывод числа записаннх лиц
    print("{0} faces trained. Exiting Program".format(len(np.unique(ids))))

def UpdateNames():
    import pandas as pd
    data = pd.read_excel('ex_students.xlsx')
    #print(data)

    names = {}  # names[id] = smbds_name
    for i in range(len(data['id'])):
        names[data['id'][i]] = data['Name'][i]
    #print(names)
    return names
