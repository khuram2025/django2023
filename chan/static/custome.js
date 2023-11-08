< script type = "text/javascript" >
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
        $("html,body").animate({
          scrollTop: $("h1").offset().top
        }, {
          duration: 250,
          easing: "swing"
        });
      },
      submitHandler: function (form) {
        $("button[type=submit], input[type=submit]").attr("disabled", "disabled");
        form.submit();
      },
    });
  });
$(document).ready(function () {
  // Function to update the options for a select element
  function updateOptions(selectElementId, options, defaultOptionText) {
    var selectElement = $('#' + selectElementId);
    selectElement.empty(); // Clear all existing options
    selectElement.append($('<option>', {
      value: '',
      text: defaultOptionText,
      selected: true
    }));
    $.each(options, function (index, item) {
      selectElement.append($('<option>', {
        value: item.pk_i_id,
        text: item.s_name_native || item.s_name // Use native name if available
      }));
    });
    selectElement.prop('disabled', options.length === 0);
  }

  // Listen for changes in the country dropdown
  $("#countryId").on("change", function () {
    var countryId = $(this).val();
    var url = "https://epsilon.mb-themes.com/index.php?page=ajax&action=regions&countryId=" + countryId;

    if (countryId) {
      $("#regionId").prop('disabled', false);
      $("#cityId").prop('disabled', true).empty().append($('<option>', {
        value: '',
        text: 'Select a city...'
      }));

      // Fetch regions for the selected country
      $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        success: function (data) {
          updateOptions('regionId', data, 'Select a region...');
        }
      });
    } else {
      updateOptions('regionId', [], 'Select a region...');
      updateOptions('cityId', [], 'Select a city...');
      $("#regionId, #cityId").prop('disabled', true);
    }
  });

  // Listen for changes in the region dropdown
  $("#regionId").on("change", function () {
    var regionId = $(this).val();
    var url = "https://epsilon.mb-themes.com/index.php?page=ajax&action=cities&regionId=" + regionId;

    if (regionId) {
      $("#cityId").prop('disabled', false);
      // Fetch cities for the selected region
      $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        success: function (data) {
          updateOptions('cityId', data, 'Select a city...');
        }
      });
    } else {
      updateOptions('cityId', [], 'Select a city...');
      $("#cityId").prop('disabled', true);
    }
  });

  // Initialize with the country dropdown if it has a selected value
  if ($("#countryId").val()) {
    $("#countryId").trigger('change');
  }

  // Dynamic subcategory selection
  document.getElementById('catId').addEventListener('change', function () {
    var mainCategory = this.value;
    var subcategorySelect = document.getElementById('subcategory-select');
    var subcatIdSelect = document.getElementById('subcatId');

    if (mainCategory === "for-sale") {
      subcategorySelect.style.display = 'block';
      subcatIdSelect.innerHTML = `
      <option value="">Select subcategory</option>
      <option value="electronics">Electronics</option>
    `;
    } else if (mainCategory === "vehicles") {
      subcategorySelect.style.display = 'block';
      subcatIdSelect.innerHTML = `
      <option value="">Select subcategory</option>
      <option value="cars">Cars</option>
    `;
    } else {
      subcategorySelect.style.display = 'none';
    }
  });
});


function toggleDescription() {
  var visibleText = document.querySelector('.desc-text .visible');
  var hiddenText = document.querySelector('.desc-text .hidden');
  if (visibleText.style.display === 'none') {
    visibleText.style.display = 'block';
    hiddenText.style.display = 'none';
  } else {
    visibleText.style.display = 'none';
    hiddenText.style.display = 'block';
  }
}

</script>