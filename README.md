# Design Documentation – CPS Expertise Network

## Purpose
To create an easy-to-use and accessible digital space where CPS faculty, staff, and administrators can better understand the “Skills and Expertise” that exist across CPS.

## Primary Users
- CPS Faculty
- Administrators
- Staff

## Inspiration
- [UCL Profiles](https://profiles.ucl.ac.uk/)

## Required Functionality

### Database Configuration
The database is stored in PostgreSQL and should be configured as follows:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}
