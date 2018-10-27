let Profile = function(email, firstName, lastName, blurb, credentials) {
    this.email = ko.observable(email);
    this.firstName = ko.observable(firstName);
    this.lastName = ko.observable(lastName);
    this.blurb = ko.observable(blurb);
    this.credentials = ko.observable(credentials);
};

let SSHCredentials = function(username, privateKey) {
    this.username = ko.observable(username);
    this.privateKey = ko.observable(privateKey);
};

let Password = function() {
    this.newPassword = ko.observable();
    this.confirmPassword = ko.observable();
};

function ProfileViewModel() {
    let self = this;

    self.profile = ko.observable();
    self.loadingProfile = ko.observable(true);

    self.password = ko.observable();
    self.updatingPassword = ko.observable(false);

    self.credentials = ko.observable();
    self.updatingCredentials = ko.observable(false);

    self.getProfile = function() {
        $.ajax({
            url: "/api/accounts/profile",
			success: function(data) {
                let creds = new SSHCredentials(data.ssh_user);
                self.profile(new Profile(data.email, data.first_name, data.last_name, data.blurb, creds));
            }, 
            complete: function() {
                self.loadingProfile(false);
            }
        });
    }

    self.updateProfile = function() {
        self.loadingProfile(true);
        $.ajax({
            url: "/api/accounts/profile",
            contentType: "application/json",
            type: "PUT",
            data: JSON.stringify({
                first_name: self.profile().firstName(),
                last_name: self.profile().lastName(),
                blurb: self.profile().blurb()
            }),
            complete: function() {
                self.loadingProfile(false);
            }
        });
    }

    self.showPasswordModal = function() {
        self.password(new Password());
        self.updatingPassword(false);
	    $("#password-modal").modal({ 'backdrop': 'static'});
    }

    self.updatePassword = function() {
        if(self.password().newPassword() == self.password().confirmPassword()) {
            self.updatingPassword(true);
            $.ajax({
                url: "/api/accounts/password",
                contentType: "application/json",
                type: "PUT",
                data: JSON.stringify({
                    password: self.password().newPassword()
                }),
                success: function() {
                    $("#password-modal").modal('hide');
                },
                complete: function() {
                    self.updatingPassword(false);
                }
            });
        }        
    }

    self.showCredentialsModal = function() {
        self.credentials(self.profile().credentials());
        self.updatingCredentials(false);
	    $("#credentials-modal").modal({ 'backdrop': 'static'});
    }

    self.updateCredentials = function() {
        self.updatingCredentials(true);
        $.ajax({
            url: "/api/accounts/credentials",
            contentType: "application/json",
            type: "PUT",
            data: JSON.stringify({
                ssh_user: self.credentials().username(),
                ssh_private_key: self.credentials().privateKey()
            }),
            success: function() {
                $("#credentials-modal").modal('hide');
            },
            error: function(err) {
                $("#credentials-error").text(err.responseJSON.errorMessage);
            },
            complete: function() {
                self.updatingCredentials(false);
            }
        });
    }
}

var profile;
var question = new QuestionModal("question-dialog");

$(document).ready(function () {
    
    profile = new ProfileViewModel();
    ko.applyBindings(profile, document.getElementById("page-wrapper"));

    profile.getProfile();
});
