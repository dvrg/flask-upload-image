import os, uuid
from io import BytesIO
from flask import Flask, render_template, redirect, url_for, request, send_file
from wtforms import SubmitField, StringField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/db-images'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'a-random-string'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

target = os.path.join(app.static_folder, 'uploads/photos')

class PhotoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    photo_filename = db.Column(db.String(254))
    doc_filename = db.Column(db.String(254))
    doc = db.Column(db.LargeBinary)

    def __repr__(self):
        return '<Filename %r>' % self.photo_filename

class PhotoForm(FlaskForm):
    name = StringField(u'Kategori', validators=[DataRequired()])
    photo = FileField(u'Photo', validators=[FileRequired(), FileAllowed(['jpeg','jpg','png'], 'Images only!')])
    doc = FileField(u'Dokumen Produk', validators=[FileRequired(), FileAllowed(['pdf'], 'PDF only!')])
    submit = SubmitField(u'Simpan')

@app.route('/', methods=['GET','POST'])
def unggah(): 
    form = PhotoForm()
    print("Target Folder : " + target)
    
    if not os.path.exists(target):
        print("Make Directory!")
        os.makedirs(target)
    
    if form.validate_on_submit(): 
        doc = form.doc.data
        file = form.photo.data.filename
        ext = file.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4().hex, ext)
        destination = "/".join([target, filename])
        form.photo.data.save(destination)

        photo = PhotoModel(photo_filename=filename, name=form.name.data, doc_filename=doc.filename, doc=doc.read())
        db.session.add(photo)
        db.session.commit()

        return redirect('lihat')

    return render_template('upload.html', form=form)

@app.route('/lihat', methods=['GET'])
def lihat():
    photos = PhotoModel.query.all()
    return render_template('show.html', photos=photos)

@app.route('/lihat/<int:id>', methods=['GET'])
def lihat_data(id):
    file_data = PhotoModel.query.filter_by(id=id).first_or_404()
    return send_file(BytesIO(file_data.doc), attachment_filename=file_data.doc_filename, mimetype='application/pdf')

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    print("Target Folder : " + target)

    form = PhotoForm()
    data = PhotoModel.query.filter_by(id=id).first_or_404()
    
    if form.validate_on_submit():

        if data.doc_filename is not None:
            old_doc = data.doc_filename
            destination_del = "/".join([target, old_doc])
            if os.path.exists(destination_del):
                os.remove(destination_del)

        if data.photo_filename is not None:
            old = data.photo_filename
            destination_del = "/".join([target, old])
            if os.path.exists(destination_del):
                os.remove(destination_del)

        file2 = form.doc.data
        file = form.photo.data.filename
        ext = file.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4().hex, ext)
        destination_save = "/".join([target, filename])
        form.photo.data.save(destination_save)

        data.photo_filename=filename
        data.name=form.name.data
        data.doc_filename=file2.filename
        data.doc=file2.read()

        db.session.commit()
        return redirect('lihat')
    #else:
        #filename = None
    
    form.name.data = data.name
    form.photo.data = data.photo_filename

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
