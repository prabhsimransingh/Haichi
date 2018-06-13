from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms import Form, TextField, RadioField, TextAreaField, validators, StringField, SubmitField
from redis import Redis, RedisError
import os
import socket
import k8sclient
 
# App config.
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'super mega secret key'

 
class ReusableForm(Form):
    name = TextField('k8s Cluster Name:', validators=[validators.required()])
    cloudProvider = RadioField('Select your cloud provider', validators=[validators.required()], 
        choices=[('aws', 'AWS EKS'), ('google', 'Google GKE')])
    deployName = TextField('Deployment Name:', validators=[validators.required()])
    # images = 

    def reset(self):
        blankData = MultiDict([ ('csrf', self.reset_csrf() ) ])
        self.process(blankData)
 
 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
    
 
    print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        cloud = request.form['cloudProvider']
 
        if form.validate():
            flash('k8s cluster, ' + name + ', spinning up in ' + cloud)
            return redirect(url_for('hello'))
        else:
            flash('Error: All the form fields are required. ')
 
    return render_template('hello.html', form=form)
 
@app.route("/deploy", methods=['GET'])
def deploy():
    return render_template("deploy.html")

@app.route("/deploy/create", methods=['POST'])
def dep_create():
    k8sclient.init()
    print('deployment started')
    k8sclient.create_deployment(request.form['name'], request.form['namespace'], "nginx:1.9.1" , 2)
    return redirect("/")

@app.route("/deployments", methods=['GET'])
def dep_list():
    k8sclient.init()    
    li = k8sclient.get_deployment_list()
    print(li)
    return redirect("/")


@app.route("/deploy/delete", methods=['POST'])
def dep_delete():
    print('deployment delete initalized')
    k8sclient.init()
    k8sclient.delete_deployment(request.form['name'])
    return redirect("/deployments")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9990)