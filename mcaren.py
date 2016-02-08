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
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['DEBUG'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


class RenameDataForm(Form):
	dbfile = FileField('Select the Access database', validators=[Required()])

	submit = SubmitField('Submit')



@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
	form = RenameDataForm()
	if form.validate_on_submit():
		old_dbfile = session.get('dbfile')
		if old_dbfile is not None and old_dbfile != form.dbfile.data.filename:
			flash('New database file selected.')
		session['dbfile'] = form.dbfile.data.filename
		session['dbpath'] = os.path.realpath(form.dbfile.data.filename)
		# session['dbpath'] = os.path.dirname(os.path.realpath(form.dbfile.data.filename))
		session['dirname'] = request.files['file']
		# session['dirname'], filename = os.path.split(os.path.abspath(form.dbfile.data.filename))
		return redirect(url_for('index'))
	return render_template(
			'index.html', 
			form=form, 
			dbfile=session.get('dbfile'), 
			dbpath=session.get('dbpath'),
			dirname=session.get('dirname'))


@app.route('/rename_data', methods=['GET', 'POST'])
def rename_data():
	if session['dbfile'] and session['dbpath']:
		dbpath = session['dbpath']
		mca = MCAImage(dbpath)
		filelist = mca.get_file_list()
	return render_template('rename_data.html', filelist=filelist)


@app.route('/stats', methods=['GET','POST'])
def stats():
	mca = MCAImage("C:\PythonDevel\mca_rename\Export02032016")
	filelist = None
	if mca:
		filelist = mca.get_file_list()

	stats = mca.stats()

	return render_template('stats.html', filelist=filelist, stats=stats)


if __name__ == '__main__':
	manager.run()