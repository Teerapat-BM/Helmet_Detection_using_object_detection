# Helmet_Detection using YOLOv8
First step : <br>
Create Python environment<br>
    > Python:Create Environment<br>
    > Choose : Python v. 3.7 --> 3.11 # if have error, try to use python version 3.8 <br><br>

First Command :<br>
    " .venv\Scripts\activate "<br><br>

Image Genarator :<br>
    - select your video<br>
    - change path in file img.py on line 17 to your folder which you select to save.<br>
    - use this command " pip install labelimg ultralytics " for install labelimg and cv2 framework.<br>
    - type " labelimg " in terminal for open labelimg framwork. <br>
    - create folder label and change save label in this folder.<br>
    - change model for use to YOLO and create rectangle to helmet,<br>
    - when finished this process create dataset folder.<br>
    - in dataset folder, create images and labels folder.<br>
    - in images and labels folder, create training and validation folder.<br>
    - copy all datas classes and images and paste to training and validation folder.<br>
    - zip this file.<br><br>

Train model(Colab) :<br>
    - upload zip file to your google drive<br>
    - open yolov8_trainmodel.ipynb in colab<br>
    - when conneted google drive, change path to your zip file and unzip it with code in colab<br>
    - create a new file name " data.yaml " in folder dataset and run<br>
    - when process was finished, check in folder runs\detect\train\weights<br>
    - download best.pt and last.pt to model folder<br><br>

Install framework libary : <br>
    " pip install fastapi[standard] sqlalchemy scipy requests"<br><br>

Run program :<br>
    " fastapi dev api.py "<br>
    " cd frontend "<br>
    " python -m http.server 8080 "<br>
    " python count.py "<br><br>

Checking api server and dastboard:<br>
    " http://localhost:8000/docs "<br>
    " http://localhost:8000 "<br><br>

Thanks!!
