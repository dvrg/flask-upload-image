import os, uuid
from flask import Flask, render_template, redirect, url_for, request
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

    def __repr__(self):
        return '<Filename %r>' % self.photo_filename

class PhotoForm(FlaskForm):
    name = StringField(u'Kategori', validators=[DataRequired()])
    photo = FileField(u'Photo', validators=[FileRequired(), FileAllowed(['jpeg','jpg','png'], 'Images only!')])
    submit = SubmitField(u'Simpan')


@app.route('/')
def index():
    form = PhotoForm()
    return render_template('upload.html', form=form)

@app.route('/unggah', methods=['GET', 'POST'])
def unggah(): 
    form = PhotoForm()
    print("Target Folder : " + target)
    
    if not os.path.exists(target):
        print("Make Directory!")
        os.makedirs(target)
    
    if form.validate_on_submit(): 
        file = form.photo.data.filename
        #print(file)

        ext = file.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4().hex, ext)
        print('Nama File : ', filename)
        #filename = secure_filename(form.photo.data.filename)
        destination = "/".join([target, filename])
        #print("Filename : "+filename)
        print("Destination : "+destination)
        form.photo.data.save(destination)

        photo = PhotoModel(photo_filename=filename, name=form.name.data)
        db.session.add(photo)
        db.session.commit()

        return redirect('lihat')

    return render_template('upload.html', form=form)

@app.route('/lihat')
def lihat():
    photos = PhotoModel.query.all()
    return render_template('show.html', photos=photos)

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    print("Target Folder : " + target)

    form = PhotoForm()
    data = PhotoModel.query.filter_by(id=id).first_or_404()
    
    if form.validate_on_submit():
        
        old = data.photo_filename
        destination_del = "/".join([target, old])
        os.remove(destination_del)

        file = form.photo.data.filename
        ext = file.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4().hex, ext)
        destination_save = "/".join([target, filename])
        form.photo.data.save(destination_save)

        data.photo_filename=filename
        data.name=form.name.data

        db.session.commit()
        return redirect('lihat')
    #else:
        #filename = None
    
    form.name.data = data.name
    form.photo.data = data.photo_filename

    return render_template('update.html', form=form)

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
