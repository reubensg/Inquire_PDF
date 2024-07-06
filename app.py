from flask import Flask, request, redirect, url_for, render_template, send_from_directory,jsonify,flash,session
import json
import os
from main import add_data,user_input
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS=set(['pdf'])

def allowed_file(filename):
    return '.'in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/",methods=["GET","POST"])
def index():
    # flash("")
    return render_template('index.html')


@app.route("/upload",methods=["GET","POST"])
def upload():
   
    if request.method=='POST':
        if "file" in request.files:
            file = request.files["file"]
            # print(request.files)
            # print(file.filename)
            if file and allowed_file(file.filename):
                name=file.filename
                print(name)
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))   
                # file.save(name)   
                flash("File Uploaded Successfully")
               
                # location="C:\\Users\\reube\\OneDrive\\Desktop\\Mini Project\\PDF_Query\\static\\uploads\\"
                # path=os.path.join(location,name)
                # print(path)
                db_name=add_data(name)
                session['db_name']=db_name
                print(session)
                # os.remove("./" +name)
                print("Upload Clicked and databse created")
                return render_template('index.html', filename=filename)

    return render_template('index.html')

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    print(url_for('display_image', filename=filename))
    # return redirect(url_for(filename=filename), code=301)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/get",methods=['GET','POST'])
def chat():
    if request.method=='POST':
        question=request.form['text']
        print(question)
        db_name=session.get('db_name')
        print(session)
        result=user_input(question,db_name)
        print(result)
        return jsonify({"message": result})


    return render_template('index.html')

@app.route("/clear",methods=['GET','POST'])
def clear():
    session['db_name']=None
    print(session)
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)
    