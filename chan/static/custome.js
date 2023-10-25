<script type="text/javascript">
      $(document).ready(function () {
        // Code for form validation
        $("form[name=register]").validate({
          rules: {
            s_name: {
              required: true,
            },
            s_email: {
              required: true,
              email: true,
            },
            s_password: {
              required: true,
              minlength: 5,
            },
            s_password2: {
              required: true,
              minlength: 5,
              equalTo: "#s_password",
            },
          },
          messages: {
            s_name: {
              required: "Name: this field is required.",
            },
            s_email: {
              required: "Email: this field is required.",
              email: "Invalid email address.",
            },
            s_password: {
              required: "Password: this field is required.",
              minlength: "Password: enter at least 5 characters.",
            },
            s_password2: {
              required: "Second password: this field is required.",
              minlength: "Second password: enter at least 5 characters.",
              equalTo: "Passwords don't match.",
            },
          },
          errorLabelContainer: "#error_list",
          wrapper: "li",
          invalidHandler: function (form, validator) {
            $("html,body").animate({ scrollTop: $("h1").offset().top }, { duration: 250, easing: "swing" });
          },
          submitHandler: function (form) {
            $("button[type=submit], input[type=submit]").attr("disabled", "disabled");
            form.submit();
          },
        });
      });
    </script>