const navbarLinks = document.getElementsByClassName('navlist')[0]
const alerts = document.querySelectorAll('.alert');


setTimeout(() => {
    alerts.forEach(alert => {
        alert.remove();
    });
}, 6000);


document.addEventListener('keydown', function (event) {
    const activeTag = document.activeElement?.tagName;
    const isTyping =
        activeTag === 'INPUT' ||
        activeTag === 'TEXTAREA' ||
        document.activeElement?.isContentEditable;

    const isSlash = event.key === '/' && !event.shiftKey && !event.ctrlKey && !event.metaKey && !event.altKey;

    if (isSlash && !isTyping) {
        event.preventDefault();
        const searchInput = document.getElementById('navbar-search');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});