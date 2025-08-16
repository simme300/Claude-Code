# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 5.2.5 project named "claude_code" with a basic structure. The project contains:

- Main Django project configuration in `claude_code/` directory
- A single Django app called `main/`
- SQLite database (default Django setup)
- Standard Django project layout

## Development Commands

### Running the Development Server

```bash
python manage.py runserver
```

### Database Operations

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Testing

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test main
```

### Django Management Commands

```bash
# Start Django shell
python manage.py shell

# Collect static files (for production)
python manage.py collectstatic
```

## Project Structure

- `claude_code/` - Main Django project configuration
  - `settings.py` - Django settings (currently using development settings with DEBUG=True)
  - `urls.py` - Root URL configuration (includes main app URLs)
  - `wsgi.py` / `asgi.py` - WSGI/ASGI application entry points
- `main/` - Primary Django app with standard Django structure
  - `models.py` - Database models
  - `views.py` - View functions (includes basic index view)
  - `forms.py` - Django forms
  - `urls.py` - App-specific URL configuration
  - `admin.py` - Django admin configuration
  - `tests.py` - Test cases
  - `templates/main/` - App-specific templates
  - `static/main/` - App-specific static files (CSS, JS, images)
- `templates/` - Project-level templates (includes base.html)
- `static/` - Project-level static files
- `manage.py` - Django management script

## Architecture Notes

- Standard Django project with proper separation of templates and static files
- Uses SQLite database for development
- Main app is configured in INSTALLED_APPS
- Templates directory configured in settings
- Static files properly configured with STATICFILES_DIRS
- Basic URL routing set up between project and app levels
