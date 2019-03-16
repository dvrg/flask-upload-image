import os
from flask import Flask, request, redirect, render_template, url_for, flash, abort, g
from flask_uploads import UploadSet, config_for_set, IMAGES, UploadNotAllowed, configure_uploads

app = Flask(__name__)
app.config['UPLOADS_DEFAULT_DEST'] = 'static/var/uploads'

photos = UploadSet('photos', IMAGES)
#media = UploadSet('media', default_dest=lambda app: app.instance_root)
configure_uploads(app, (photos))

@app.route('/', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        rec = Photo(filename=filename)
        rec.store()
        flash("Photo saved.")
        return redirect(url_for('show', id=rec.id))
    return render_template('upload.html')

@app.route('/photo/<id>')
def show(id):
    photo = Photo.load(id)
    if photo is None:
        abort(404)
    url = photos.url(photo.filename)
    return render_template('show.html', url=url, photo=photo)

if __name__ == "__main__":
    app.run(debug=True)