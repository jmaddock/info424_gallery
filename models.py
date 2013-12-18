from google.appengine.ext import db

class Image(db.Model):
    pic = db.BlobProperty()
    thumbnail = db.BlobProperty()

class Gallery(db.Model):
    name = db.StringProperty()
    pic = db.BlobProperty()
    thumbnail = db.BlobProperty()
