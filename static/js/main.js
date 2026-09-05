const themes = ['light', 'dark', 'neon'];
let currentThemeIndex = 0;

function toggleTheme() {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length;
    const selectedTheme = themes[currentThemeIndex];
    document.documentElement.setAttribute('data-theme', selectedTheme);
    
    const btn = document.getElementById('theme-btn');
    let icon = 'fa-moon';
    if(selectedTheme === 'dark') icon = 'fa-sun';
    if(selectedTheme === 'neon') icon = 'fa-wand-magic-sparkles';

    btn.innerHTML = `<i class="fa-solid ${icon}"></i> ${selectedTheme.toUpperCase()} MODE`;
}
