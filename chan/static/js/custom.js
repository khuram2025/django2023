document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed");

    document.body.addEventListener('click', function (event) {
        if (event.target.matches('.location-elem')) {
            console.log("City element clicked:", event.target.textContent.trim());
            event.preventDefault();
            var selectedCity = event.target.textContent.trim().split(',')[0];
            console.log('City selected:', selectedCity);
            updateCity(selectedCity);
        }
    });
});

function updateCity(city) {
    console.log("Sending request to update city to:", city);
    fetch('/update_city/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ city: city })
    })
    .then(response => {
        console.log('Server response received:', response);
        return response.json();
    })
    .then(data => {
        console.log('Server data:', data);
        if (data.success) {
            console.log('City updated successfully, reloading the page.');
            window.location.reload(); // Reload the page
        } else {
            console.error('Update failed:', data.message);
        }
    })
    .catch(error => console.error('Error during fetch:', error));
}

function updateHomepageContent(cityData) {
    console.log('Updating homepage content with city data:', cityData);

    // AJAX request to get updated content
    fetch('/get_updated_homepage/', {
        method: 'GET', // or 'POST' if needed
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.text())
    .then(html => {
        // Assuming you have a container div with an ID 'homepage-content'
        document.getElementById('homepage-content').innerHTML = html;
    })
    .catch(error => console.error('Error updating homepage:', error));
}


function getCsrfToken() {
    let csrfToken = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                csrfToken = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                console.log('Found CSRF token:', csrfToken);
                break;
            }
        }
    }
    return csrfToken;
}
