import os, urllib, jinja2, webapp2, models
from google.appengine.ext import db
from google.appengine.api import images

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GALLERY_NAME = 'default_gallery'

def gallery_key(gallery_name=DEFAULT_GALLERY_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return db.Key('Gallery', gallery_name)

class MainPage(webapp2.RequestHandler):
    def get(self):
        galleries = models.Gallery.all()
        keys = [{'key':x.key(),'name':x.name} for x in galleries]
        print keys
        template_values = {
            'keys': keys,
            'length': len(keys)
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Gallery(webapp2.RequestHandler):
    def get(self):
        gallery = db.get(self.request.get('gallery_id'))
        images = models.Image.all().ancestor(gallery)
        keys = [x.key() for x in images]
        template_values = {
            'keys': keys,
            'length': len(keys)
        }
        template = JINJA_ENVIRONMENT.get_template('gallery.html')
        self.response.write(template.render(template_values))

class Upload(webapp2.RequestHandler):
    def get(self):
        data = models.Gallery.all()
        galleries = [{'name':x.name,'key':x.key()} for x in data]
        template_values = {
            'galleries': galleries
        }
        #gallery_name = self.request.get('gallery_name')
        template = JINJA_ENVIRONMENT.get_template('upload.html')
        self.response.write(template.render(template_values))

class ImageUpload(webapp2.RequestHandler):
    def post(self):
        pics = self.request.get_all('img')
        gallery_name = self.request.get('gallery')
        q = db.Query(models.Gallery)
        q.filter('name =', gallery_name)
        gallery = q.get()
        for x in pics:
            image = models.Image(parent=gallery)
            image.pic = db.Blob(x)
            image.thumbnail = db.Blob(images.resize(x, 300))
            image.put()
        self.redirect('upload')

class GalleryUpload(webapp2.RequestHandler):
    def post(self):
        gallery = models.Gallery()
        gallery.name = self.request.get('name')
        pic = self.request.get('img')
        gallery.pic = db.Blob(pic)
        gallery.thumbnail = db.Blob(images.resize(pic, 300))
        gallery.put()
        self.redirect('upload')

class GalleryDelete(webapp2.RequestHandler):
    def post(self):
        gallery = db.get(self.request.get('gallery'))
        db.delete(models.Image.all().ancestor(gallery))
        db.delete(gallery)
        self.redirect('upload')

class Img(webapp2.RequestHandler):
    def get(self):
        img = db.get(self.request.get('img_id'))
        view = self.request.get('view')
        thumb = self.request.get('thumb')
        if view == 'True':
            self.response.out.write('<img src="img?img_id=%s&&view=False&&thumb=False">' %
                        img.key())
        else:
            if thumb == 'True':
                self.response.out.write(img.thumbnail)
            else:
                self.response.out.write(img.pic)

application = webapp2.WSGIApplication([
    ('/*', MainPage),
    ('/gallery', Gallery),
    ('/img', Img),
    ('/upload', Upload),
    ('/gallery-upload', GalleryUpload),
    ('/gallery-delete', GalleryDelete),
    ('/image-upload', ImageUpload),
], debug=True)
