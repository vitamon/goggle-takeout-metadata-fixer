create pyhon script which will fix google takeout photos metadata.

Given input_path:
scan recursively for image files (*.jpg) and corresponding (*.jpg.json) metadata files with same name.

example metadata:
{
  "title": "P3100766.JPG",
  "description": "",
  "imageViews": "128",
  "creationTime": {
    "timestamp": "1425226812",
    "formatted": "Mar 1, 2015, 4:20:12 PM UTC"
  },
  "photoTakenTime": {
    "timestamp": "1425215613",
    "formatted": "Mar 1, 2015, 1:13:33 PM UTC"
  },
  "geoData": {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "latitudeSpan": 0.0,
    "longitudeSpan": 0.0
  },
  "geoDataExif": {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "latitudeSpan": 0.0,
    "longitudeSpan": 0.0
  },
  "people": [{
    "name": "Maxim"
  }],
  "url": "https://lh3.googleusercontent.com/itZLsOZBsFoZHaXlr3EfyE0hShBKiXE_X5B6aq8urKpwOp2VWhr-gmq3OOfXWsaHjOdYkfaO_GD4fwC2eOSJqz3Hnhp3sKEOjsRB4-Qn"
}

your task to fix image creation time to photoTakenTime, and image location to geoData or geoDataExif if it is defined.
Do not recreate images, only update the image in place. 

to test, run on "Google Фото" folder.
