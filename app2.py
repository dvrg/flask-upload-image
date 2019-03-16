import os
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
    target = os.path.join(app.static_folder, 'uploads/photos')
    print("Target Folder : " + target)
    
    if not os.path.exists(target):
        print("Make Directory!")
        os.makedirs(target)
    
    if form.validate_on_submit(): 
        file = form.photo.data.filename
        print(file)
        filename = secure_filename(form.photo.data.filename)
        destination = "/".join([target, filename])
        print("Filename : "+filename)
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

@app.route('/edit/<int:id>')
def edit(id):
    form = PhotoForm()
    data = PhotoModel.query.filter_by(id=id).first_or_404()
    form.name.data = data.name
    form.photo.data = data.photo_filename
    return render_template('upload.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
