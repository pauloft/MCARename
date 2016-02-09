from flask import Flask, render_template, session, redirect, url_for, flash,request
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import Required

import os

from mca_image import MCAImage 


app = Flask(__name__)
# app.config['SECRET_KEY'] = 'jJzKaZVeU8yoFNIlXK5qN9ksZDmzrpkwdm7TLhhIfitiAY5dcNNCQAC0j0L4n5Z'
app.config['SECRET_KEY'] = str(os.environ.get('SECRET_KEY'))
app.config['DEBUG'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


class RenameDataForm(Form):
	dbfile = FileField('Select the Access database', validators=[Required()])

	submit = SubmitField('Submit')


class DBFilePathForm(Form):
	"""Form to receive input path to the MS Access database file"""
	databasefile = StringField('What is the full path to the database file?',validators=[Required()])
	submit = SubmitField('Process')


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
	form = DBFilePathForm()
	if form.validate_on_submit():
		old_databasefile = session.get('databasefile')
		if old_databasefile is not None and old_databasefile != form.databasefile.data:
			flash('Ok. You have changed the database file!')
		session['databasefile'] = form.databasefile.data
		session['imagesfolder'] = os.path.dirname(form.databasefile.data)
		return redirect(url_for('index'))
	return render_template('index.html', form=form, 
		databasefile=session.get('databasefile'),
		imagesfolder=session.get('imagesfolder')
		)


@app.route('/rename_data')
def rename_data():
	databasefile = session.get('databasefile')
	imagesfolder = session.get('imagesfolder')
	filelist = []
	statistics = None
	if databasefile is not None and imagesfolder is not None:
		mca = MCAImage(imagesfolder)
		filelist = mca.get_file_list(True)
		statistics = mca.stats()
	return render_template('rename_data.html', filelist=filelist, statistics=statistics)


@app.route('/show_renames')
def show_renames():
	databasefile = session.get('databasefile')
	imagesfolder = session.get('imagesfolder')
	filelist = []
	statistics = None
	if databasefile is not None and imagesfolder is not None:
		mca = MCAImage(imagesfolder)
		# filelist = mca.get_file_list(True)
		adict = mca.list_by_inspection()
		statistics = mca.sort_by_key(adict)
	return render_template('show_renames.html', statistics=statistics)


@app.route('/stats', methods=['GET','POST'])
def stats():
	imagesfolder = session.get('imagesfolder')
	filelist = None
	stats = None
	if imagesfolder is not None:
		mca = MCAImage(imagesfolder)
		if mca:
			filelist = mca.get_file_list()

		stats = mca.stats()

	return render_template('stats.html', filelist=filelist, stats=stats)


if __name__ == '__main__':
	manager.run()