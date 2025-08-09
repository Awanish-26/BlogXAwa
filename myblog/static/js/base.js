const toggleButton = document.getElementsByClassName('toggle-button')[0]
const navbarLinks = document.getElementsByClassName('navlist')[0]
const alerts = document.querySelectorAll('.alert');

toggleButton.addEventListener('click', () => {
    navbarLinks.classList.toggle('active');
});

setTimeout(() => {
    alerts.forEach(alert => {
        alert.remove();
    });
}, 6000);