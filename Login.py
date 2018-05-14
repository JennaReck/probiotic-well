from Handler import *

class Login(Handler):
    def get(self):
        error = self.request.get("error")
        if error:
            error = "Invalid login."
        self.render("login.html",
                    pagetitle="Login",
                    error=error)

    def post(self):
        if not self.locked_out():
            username = self.request.get("username")
            password = self.request.get("password")

            admin = AdminDB.get_by_id(5629499534213120)
            if username == admin.username and self.valid_password(admin.username,
                                                                  password,
                                                                  admin.password):
                user_cookie, user_hash = self.make_cookie(admin)
                self.response.headers.add_header("Set-Cookie","username=%s|%s; Path=/"
                                                    %(user_cookie, user_hash))
                self.redirect("/admin-panel")
            else:
                self.update_failed_logins()
                self.redirect("/back-login?error=y")
        else:
            self.redirect("/back-login?error=yes")

class Logout(Handler):
    def get(self):
        self.response.headers.add_header("Set-Cookie","username=; Path=/")
        self.redirect("/")

class AdminPanel(Handler):
    def get(self):
        if self.user_check():
            self.render("admin-panel.html",
                        pagetitle="Admin Panel")
        else:
            self.redirect("/back-login")
