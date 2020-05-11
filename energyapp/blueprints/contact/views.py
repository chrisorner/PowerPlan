from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    url_for,
    render_template)

from energyapp.blueprints.contact.forms import ContactForm

contact = Blueprint('contact', __name__, template_folder='templates')


@contact.route('/contact', methods=['GET', 'POST'])
def index():
    form = ContactForm()

    if form.validate_on_submit():
        # This prevents circular imports.
        from energyapp.blueprints.contact.tasks import deliver_contact_email
        
        #calls the celery task, .delay tells celery that we want the task to happen in the background
        deliver_contact_email.delay(request.form.get('email'),
                                    request.form.get('message'))

        flash('Thanks, expect a response shortly.', 'success')
        return redirect(url_for('contact.index'))

    return render_template('contact/index.html', form=form)