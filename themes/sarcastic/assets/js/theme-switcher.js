(function() {
  'use strict';
  
  const STORAGE_KEY = 'gishe-theme';
  const THEMES = ['light', 'dark', 'system'];
  
  // Initialize theme switcher
  function init() {
    const savedTheme = localStorage.getItem(STORAGE_KEY) || 'system';
    applyTheme(savedTheme);
    updateButtons(savedTheme);
    
    // Add click listeners to theme buttons
    const buttons = document.querySelectorAll('[data-theme-toggle]');
    buttons.forEach(button => {
      button.addEventListener('click', handleThemeChange);
    });
    
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', () => {
      const currentTheme = localStorage.getItem(STORAGE_KEY);
      if (currentTheme === 'system') {
        applyTheme('system');
      }
    });
  }
  
  // Handle theme change button clicks
  function handleThemeChange(event) {
    const button = event.currentTarget;
    const theme = button.getAttribute('data-theme-toggle');
    
    if (THEMES.includes(theme)) {
      localStorage.setItem(STORAGE_KEY, theme);
      applyTheme(theme);
      updateButtons(theme);
    }
  }
  
  // Apply theme to document
  function applyTheme(theme) {
    let activeTheme = theme;
    
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      activeTheme = systemTheme;
    }
    
    document.documentElement.setAttribute('data-theme', activeTheme);
  }
  
  // Update button states
  function updateButtons(activeTheme) {
    const buttons = document.querySelectorAll('[data-theme-toggle]');
    buttons.forEach(button => {
      const buttonTheme = button.getAttribute('data-theme-toggle');
      const isActive = buttonTheme === activeTheme;
      
      button.setAttribute('aria-pressed', isActive.toString());
      
      if (isActive) {
        button.classList.add('bg-blue-100', 'text-blue-600');
      } else {
        button.classList.remove('bg-blue-100', 'text-blue-600');
      }
    });
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
