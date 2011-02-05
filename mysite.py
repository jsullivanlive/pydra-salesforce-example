

from flask import Flask, request, flash, redirect, url_for, render_template
from flaskext.wtf import Form, TextField, HiddenField, Required
from sforce.partner import SforcePartnerClient
from settings import *

app = Flask(__name__)
app.secret_key = 'make something long and complicated here - orange!'

h = SforcePartnerClient('partner.wsdl')
h.login(SALESFORCE_USERNAME, SALESFORCE_PASSWORD, SALESFORCE_TOKEN)


class SignupForm(Form):
    firstname = TextField("First Name", validators=[Required()])
    lastname = TextField("Last Name", validators=[Required()])
    company = TextField("Company", validators=[Required()])


@app.route('/', methods=['GET','POST'])
def hello_world():
    
    form = SignupForm()
    if form.validate_on_submit():
        lead = h.generateObject('Lead')
        lead.FirstName = form.firstname.data
        lead.LastName = form.lastname.data
        lead.Company = form.company.data
        result = h.create(lead)
        if result.success:
            return redirect(url_for("thank_you"))
    result = h.query('SELECT Company FROM Lead limit 10')
    companies = []
    for record in result.records:
        companies.append( record.Company )
    
    return render_template("index.html",companies=companies, form=form)

@app.route('/thank_you', methods=['GET'])
def thank_you():
    return render_template("thank_you.html")
    
    
    
    
if __name__ == '__main__':
    app.debug = True
    app.run()
