from Handler import *
from google.appengine.api import mail

class EmailSubscribe(Handler):
    def get(self):
        domain_redirect = self.domain_redirect(self.request.url)
        if domain_redirect:
            #if on .appspot domain instead of custom domain, do 301 redirect
            self.redirect(domain_redirect, permanent=True)
            
        referred_email = self.request.get("referring-email")
        if referred_email:
            referred_email = self.sanitize_email_inputs(message=referred_email)[0]
            email_body = "email: " + referred_email + "\n\nunsubscribe: True"
            mail.send_mail(sender = "jennarecktenwald@gmail.com",
                           to = "jennarecktenwald@gmail.com",
                           subject = "subscription change",
                           body = email_body)
            self.redirect("/email-alert-settings?success=ys")
        else:
            success = self.request.get("success")
            if success == "ys":
                success_message = "You have been successfully unsubscribed."
            elif success == "y":
                success_message = "Your subscription settings have been saved."
            else:
                success_message = ""
            ads = self.chose_ads("subscribe")
            self.render("email-alert-settings.html",
                        pagetitle="Probiotic Well | Email Alert Settings",
                        ads=ads,
                        success_message=success_message)
        
    def post(self):
        email = self.request.get("subscribe-email")
        articles = self.request.get("subscribe-articles")
        reviews = self.request.get("subscribe-reviews")
        sales = self.request.get("subscribe-sales")
        unsubscribe = self.request.get("unsubscribe")
        email = self.sanitize_email_inputs(message=email)[0]

        email_body = ("email: " + email + "\n\narticles: " + articles +
                "\n\nreviews: " + reviews + "\n\nsales: " + sales +
                "\n\nunsubscribe: " + unsubscribe)
        
        mail.send_mail(sender = "jennarecktenwald@gmail.com",
                       to = "jennarecktenwald@gmail.com",
                       subject = "subscription change",
                       body = email_body)
        if unsubscribe != "undefined":
            if unsubscribe:
                self.redirect("/email-alert-settings?success=ys")
            else:
                self.redirect("/email-alert-settings?success=y")
