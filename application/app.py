import os
from flask import Flask, render_template
from flask import jsonify, request, session, redirect
import warnings, csv

app = Flask(__name__, template_folder="htmltemplates")

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'XYZ')

@app.route("/")
def hello():

    return render_template('index.html')

@app.route("/about")
def about():
    return "<h1>About page</h1>"


"""
@app.route("/update",methods= ['GET'])
def update():

    final_string = str(main())
    return jsonify(keke=final_string)
"""

@app.route("/calculate",methods= ['POST'])
def calculate():

    items = request.form.getlist("x[]")
    print(items)


    the_list_of_items = []
    the_list_of_items.append("")
    the_list_of_items.extend(items[1:]) # so that the id requirement gets fufilled.
    print(the_list_of_items)

    return jsonify(str(main(the_list_of_items,items[0])))#THIS ALREADY RETURNS MAIN!!! JUST PUT ARGS IN!

@app.route("/upload",methods=['POST'])
def upload():

    items = request.files['file'].read()


    file = open("raw.csv","wb")

    file.write(items)

    file.close()


    print(items)

    return jsonify(str("hi"))


@app.route("/login", methods= ['POST'])
def login():
    username= request.form['username']
    password= request.form['password']
    if username=="username" and password=="password":
        session['username'] = 'admin'
        return redirect('/dashboard')
    else:
        return render_template('index.html', message="Wrong username/password!")



@app.route("/dashboard", methods= ['GET'])
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect('/')



@app.route("/logout", methods= ['GET'])
def logout():
    session.pop('username', None)
    return redirect('/')

#this function computes the amount of people in the specified list then emails it to the user
def main(input, email):

    for i in range(len(input)):
        input[i] = input[i].replace(" ","").lower()#this removes spaces and caps



    print("this",input)

    #Record ID,Family Resource Center,Age,Race / Ethnicity,Gender,Primary Language,Geography,Poverty Level
    #98653,La Manzana Community Resources,0-5,Multi-racial,Female,Other,Monterey County,Below 100%
    #be able to add more than one option

    #test_category = ["","La Manzana Community Resources|Live Oak Community Resources","","Multi-racial","Female","","Monterey County","Below 100%"]

    #reads in csv file then outputs data to all_data and creates categories which hold all of the categories
    try:
        with open('raw.csv') as csvfile:

            readCSV = csv.reader(csvfile, delimiter=',')
            #print(readCSV)
            temp_data = []
            for row in readCSV:
                temp_data.append(row)
            organizations = temp_data[0] #FIXME need to find a way to determine which row has categories
    except:
        print("[There is currently no raw.csv, try uploading one]")
        return "[There is currently no raw.csv, try uploading one]"
    all_data = temp_data[1:]
    user_category = input
    list_of_users = Get_Specific_People(user_category, all_data)

    with open('newRawEmail.csv', 'w') as outfile:
        wtr = csv.writer(outfile,delimiter=',', lineterminator='\n')
        wtr.writerow(organizations)
        for users in list_of_users:
            wtr.writerow(users)


    try:
        sendMail(email)
    except:
        warnings.warn("No email selected or email didn't send")


    print(list_of_users)
    print(len(list_of_users))
    return len(list_of_users)


def Get_Specific_People(user_category, all_data):
    for i in range(len(user_category)):
        all_data = Look_For_Category(i, user_category[i], all_data)

    return all_data


def Look_For_Category(index, category_name, data_array):

    '''
    # this is code to find the categories
    names = []
    for data in data_array:
        if data[index] not in names:
            names.append(data[index])
    print(names)
    return data_array
    '''

    if category_name == "":
        return data_array

    new_array = []

    category_names = category_name.split("|")
    print(category_names)

    for data in data_array:
        if data[index].replace(" ","").lower() in category_names:#this removes spaces and caps
            new_array.append(data)

    if new_array == []:
        warnings.warn("Applying "+category_name+" does not work or exist in the index "+str(index)+ " Check spelling, or possibly ignore if there are no people that match the criteria")

    return new_array


def Get_Category_List(user_category,all_data):
    the_list = []
    for data in all_data:
        if data[0].lower() == user_category:
            the_list.append(data)
    return the_list


def Get_Category_Indicies(user_category_list, organizations):
    user_category_indicies = []
    for categories in user_category_list:
        user_category_indicies.append(Organization_Selected(categories, organizations))
    return user_category_indicies

def Organization_Selected(user_org, organizations):
    for i in range(len(organizations)):
        print(organizations[i].lower())
        print(user_org)
        if organizations[i].lower().strip() == user_org:#strip removes beginning and ending spaces, in other languages this may not be smart because of ==
            return i

    #if not reached
    raise Exception("Not Valid ORG")



def sendMail(recipient):
    import smtplib, time
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "cBridgesStatistics@gmail.com"
    toaddr = recipient

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Requested CSV " + str(time.ctime())

    # string to store the body of the mail
    body = "Below is the requested csv"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = "newRawEmail.csv"
    attachment = open("newRawEmail.csv", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "CommunityBridges1")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()



#a test run if this file is run
if __name__ == "__main__":
    test_category = ["", "LaManzana Community Resources|Live Oak Community Resources            ", "", "multi-racial", "Female",
                     "", "Monterey County", "Below 100%"]
    #test_category = ["","","","","","","",""]
    main(test_category,"")