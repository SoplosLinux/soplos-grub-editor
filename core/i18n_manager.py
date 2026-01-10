"""
Internationalization (i18n) manager for Soplos Repo Selector.
Handles GNU Gettext translation loading, language detection, and string management.
"""

import os
import locale
import gettext
from pathlib import Path
from typing import Dict, List, Optional, Union


class I18nManager:
    """
    Manages internationalization using GNU Gettext.
    Provides automatic language detection and translation services.
    """
    
    # Supported languages with their locale codes
    SUPPORTED_LANGUAGES = {
        'es': 'Spanish',
        'en': 'English', 
        'fr': 'French',
        'de': 'German',
        'pt': 'Portuguese',
        'it': 'Italian',
        'ro': 'Romanian',
        'ru': 'Russian'
    }
    
    # Language fallback chain
    FALLBACK_CHAIN = ['en', 'es']
    
    def __init__(self, locale_dir: str, domain: str = 'soplos-grub-editor'):
        """
        Initialize the i18n manager.
        
        Args:
            locale_dir: Path to locale directory containing .mo files
            domain: Translation domain name
        """
        self.locale_dir = Path(locale_dir)
        self.domain = domain
        self.current_language = None
        self.translations = {}
        self.fallback_translation = None
        
        # Ensure locale directory exists
        self.locale_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize translations
        self._load_translations()
        
        # Detect and set system language
        detected_lang = self.detect_system_language()
        self.set_language(detected_lang)
    
    def _load_translations(self):
        """Load all available translations."""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            mo_file = self.locale_dir / lang_code / 'LC_MESSAGES' / f'{self.domain}.mo'
            
            if mo_file.exists():
                try:
                    with open(mo_file, 'rb') as f:
                        translation = gettext.GNUTranslations(f)
                        self.translations[lang_code] = translation
                except Exception as e:
                    print(f"Error loading translation for {lang_code}: {e}")
        
        # Set fallback translation (English)
        if 'en' in self.translations:
            self.fallback_translation = self.translations['en']
        else:
            # Create a null translation if English is not available
            self.fallback_translation = gettext.NullTranslations()
    
    def detect_system_language(self) -> str:
        """
        Detect system language with multiple fallback methods.
        
        Returns:
            Detected language code
        """
        # Method 1: Environment variables (in order of preference)
        env_vars = ['SOPLOS_REPO_SELECTOR_LANG', 'LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG']
        
        for env_var in env_vars:
            env_value = os.environ.get(env_var)
            if env_value:
                # Extract language code from locale string (e.g., 'es_ES.UTF-8' -> 'es')
                lang_code = env_value.split('_')[0].split('.')[0].split('@')[0].lower()
                if lang_code in self.SUPPORTED_LANGUAGES:
                    return lang_code
        
        # Method 2: Python locale module
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                if lang_code in self.SUPPORTED_LANGUAGES:
                    return lang_code
        except Exception as e:
            print(f"Error detecting locale: {e}")
        
        # Default fallback
        return 'en'
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the current language for translations.
        
        Args:
            language_code: Language code to set
            
        Returns:
            True if language was set successfully, False otherwise
        """
        if language_code not in self.SUPPORTED_LANGUAGES:
            print(f"Unsupported language: {language_code}")
            return False
        
        if language_code in self.translations:
            self.current_language = language_code
            self.translations[language_code].install()
            print(f"Language set to: {language_code}")
            return True
        else:
            # Try fallback languages
            for fallback_lang in self.FALLBACK_CHAIN:
                if fallback_lang in self.translations:
                    self.current_language = fallback_lang
                    self.translations[fallback_lang].install()
                    return True
            
            # Use null translation as last resort
            self.current_language = 'en'
            self.fallback_translation.install()
            return False
    
    def get_translation(self, message: str, **kwargs) -> str:
        """Get translated message with optional formatting."""
        if self.current_language and self.current_language in self.translations:
            try:
                translated = self.translations[self.current_language].gettext(message)
            except Exception:
                translated = message
        else:
            translated = message
        
        # If translation failed, try fallback
        if translated == message and self.fallback_translation:
            try:
                translated = self.fallback_translation.gettext(message)
            except Exception:
                pass
        
        # Apply formatting if provided
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except Exception:
                pass
        
        return translated
    
    def get_plural_translation(self, singular: str, plural: str, count: int, **kwargs) -> str:
        """Get translated message with plural support."""
        if self.current_language and self.current_language in self.translations:
            try:
                translated = self.translations[self.current_language].ngettext(singular, plural, count)
            except Exception:
                translated = singular if count == 1 else plural
        else:
            translated = singular if count == 1 else plural
        
        # If translation failed, try fallback
        if translated in (singular, plural) and self.fallback_translation:
            try:
                translated = self.fallback_translation.ngettext(singular, plural, count)
            except Exception:
                pass
        
        # Apply formatting if provided
        kwargs['count'] = count  # Always include count in formatting
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except Exception:
                pass
        
        return translated
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with translations."""
        available = {}
        for lang_code, lang_name in self.SUPPORTED_LANGUAGES.items():
            if lang_code in self.translations:
                available[lang_code] = lang_name
        return available
    
    def get_current_language(self) -> str:
        """Get current language code."""
        return self.current_language or 'en'
    
    def get_current_language_name(self) -> str:
        """Get current language name."""
        current = self.get_current_language()
        return self.SUPPORTED_LANGUAGES.get(current, 'English')
    
    def _(self, message: str, **kwargs) -> str:
        """Convenience method for translation."""
        return self.get_translation(message, **kwargs)


# Global i18n manager instance
_i18n_manager = None

def get_i18n_manager(locale_dir: str = None, domain: str = 'soplos-repo-selector') -> I18nManager:
    """Returns the global i18n manager instance."""
    global _i18n_manager
    if _i18n_manager is None:
        if locale_dir is None:
            # Default path relative to this file
            current_dir = Path(__file__).parent.parent
            locale_dir = current_dir / 'locale'
        _i18n_manager = I18nManager(str(locale_dir), domain)
    return _i18n_manager

def _(message: str, **kwargs) -> str:
    """Convenience function for translation."""
    manager = get_i18n_manager()
    return manager.get_translation(message, **kwargs)

def ngettext(singular: str, plural: str, count: int, **kwargs) -> str:
    """Convenience function for plural translation."""
    manager = get_i18n_manager()
    return manager.get_plural_translation(singular, plural, count, **kwargs)

def set_language(language_code: str) -> bool:
    """Set current language."""
    manager = get_i18n_manager()
    return manager.set_language(language_code)

def get_current_language() -> str:
    from core.i18n_manager import get_i18n_manager
    return get_i18n_manager().get_current_language()

def initialize_i18n(locale_dir: str = None, domain: str = 'soplos-repo-selector') -> str:
    """Initialize the internationalization system."""
    manager = get_i18n_manager(locale_dir, domain)
    return manager.get_current_language()
