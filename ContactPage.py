from Handler import *
from google.appengine.api import mail

class ContactPage(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        ads = self.chose_ads("contact")
        status = self.request.get("status")
        self.render("contact.html",
                    pagetitle="Probiotic Well | Contact Us",
                    ads=ads,
                    status=status)

    def post(self):
        contact_from = self.request.get("contact-from")
        contact_subject = self.request.get("contact-subject")
        contact_message = self.request.get("contact-message")
        if not contact_subject:
            contact_subject = "None"
        contact_from, contact_subject, contact_message = self.sanitize_email_inputs(email=contact_from,
                                                     subject=contact_subject,
                                                     message=contact_message)

        mail.send_mail("jennarecktenwald@gmail.com",
                       "jennarecktenwald@gmail.com",
                       contact_subject,
                       contact_from + "\n\n" + contact_message)
        self.redirect("/contact?status=success")
