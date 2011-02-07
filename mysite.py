from flask import Flask, request, flash, redirect, url_for, render_template
from flaskext.wtf import Form, TextField, HiddenField, Required
from flaskext.cache import Cache
from sforce.partner import SforcePartnerClient

sfdc_connection = 1

app = Flask(__name__)
app.config.from_pyfile('mysite.cfg')
cache = Cache(app)

class SignupForm(Form):
    firstname = TextField("First Name", validators=[Required()])
    lastname = TextField("Last Name", validators=[Required()])
    company = TextField("Company", validators=[Required()])

@cache.cached(timeout=60*10, key_prefix='get_salesforce_lead_companies')
def get_salesforce_lead_companies():
    result = sfdc().query('SELECT Company FROM Lead limit 10')
    companies = []
    for record in result.records:
        companies.append( record.Company )
    return companies
    
@app.route('/', methods=['GET','POST'])
def hello_world():
    form = SignupForm()
    if form.validate_on_submit():
        lead = sfdc().generateObject('Lead')
        lead.FirstName = form.firstname.data
        lead.LastName = form.lastname.data
        lead.Company = form.company.data
        try:
            result = sfdc().create(lead)
        except Exception as e:
            flash(result)
        if result.success:
            return redirect(url_for("thank_you"))
    companies = get_salesforce_lead_companies()
    return render_template("index.html",companies=companies, form=form)

@app.route('/thank_you', methods=['GET'])
def thank_you():
    return render_template("thank_you.html")
    
def sfdc():
    h = SforcePartnerClient('partner.wsdl')
    h.login(app.config['SALESFORCE_USERNAME'], app.config['SALESFORCE_PASSWORD'], app.config['SALESFORCE_TOKEN'])
    return h
    
if __name__ == '__main__':
    app.run()