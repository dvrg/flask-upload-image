import os, uuid
from io import BytesIO
from flask import Flask, render_template, redirect, url_for, request, send_file, make_response, send_from_directory
from wtforms import SubmitField, StringField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from base64 import b64encode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/db-images'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'a-random-string'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

target = os.path.join(app.static_folder, 'uploads/photos')

def unique_name(data):
    file = data.filename
    ext = file.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4().hex, ext)
    return filename

class PhotoModel(db.Model):
    __maxsize__ = 4096
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    photo_filename = db.Column(db.String(254))
    photo = db.Column(db.LargeBinary(__maxsize__))
    doc_filename = db.Column(db.String(254))
    doc = db.Column(db.LargeBinary)

    def __repr__(self):
        return '<ID %r>' % self.id

class PhotoForm(FlaskForm):
    name = StringField(u'Kategori', validators=[DataRequired()])
    photo = FileField(u'Photo', validators=[FileRequired(), FileAllowed(['jpeg','jpg','png'], 'Images only!')])
    doc = FileField(u'Dokumen Produk', validators=[FileRequired(), FileAllowed(['pdf'], 'PDF only!')])
    submit = SubmitField(u'Simpan')

@app.route('/', methods=['GET','POST'])
def unggah(): 
    form = PhotoForm()
    if form.validate_on_submit(): 

        photo = PhotoModel(photo_filename=unique_name(form.photo.data), photo=form.photo.data.read(), name=form.name.data, doc_filename=unique_name(form.doc.data), doc=form.doc.data.read())
        db.session.add(photo)
        db.session.commit()

        return redirect('lihat')

    return render_template('upload.html', form=form)

@app.route('/lihat')
def lihat():
    data = PhotoModel.query.all()
    return render_template('show.html', data=data)

@app.route('/images/<string:filename>', methods=['GET'])
def load_gambar3(filename):
    image_data = PhotoModel.query.filter_by(photo_filename=filename).first_or_404()
    return send_file(BytesIO(image_data.photo), mimetype='images/generic', as_attachment=True, attachment_filename=image_data.photo_filename)
    #return send_from_directory(directory=BytesIO(image_data.photo), filename=image_data.photo_filename, mimetype='images/generic')

@app.route('/lihat/<string:filename>', methods=['GET'])
def lihat_data(filename):
    file_data = PhotoModel.query.filter_by(doc_filename=filename).first_or_404()
    return send_file(BytesIO(file_data.doc), attachment_filename=file_data.doc_filename, mimetype='application/pdf')

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    form = PhotoForm()
    data = PhotoModel.query.filter_by(id=id).first_or_404()
    
    if form.validate_on_submit():
        data.name=form.name.data
        data.photo=form.photo.data.read()
        data.photo_filename=unique_name(form.photo.data)
        data.doc=form.doc.data.read()
        data.doc_filename=unique_name(form.doc.data)
        
        db.session.commit()
        return redirect('lihat')
    
    form.name.data = data.name
    #form.photo.data = send_file(BytesIO(data.photo), attachment_filename=data.photo_filename, as_attachment=True)
    #form.doc.data = data.doc
    
    return render_template('upload.html', form=form)

@app.route('/hapus/<int:id>', methods=['GET','POST'])
def hapus(id):
    data = PhotoModel.query.filter_by(id=id).first_or_404()
    filename = data.photo_filename
    destination_del = "/".join([target, filename])
    
    if os.path.isfile(destination_del):
        os.remove(destination_del)
    
    db.session.delete(data)
    db.session.commit()
    return redirect('lihat')

if __name__ == "__main__":
    app.run(debug=True)
