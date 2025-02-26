
# Project "Mini App on telegram for mentoring"

@MentorsCalendarBot - bot which allow to open miniApp.
If user uses this app first time or if user doesn't register, he/she can see modules: "My calendar" and "Mentors". If user registers, he/she can see one more module - "My profile". Admin can see module - "Admin".

## Code description 

1. All files for telegram in folder 'telegram_bot'
2. All files for web-application in folder 'webapp'
3. There are folders for each module on website like 'Admin', 'Calendar', 'Mentors', 'Profile'. File 'Views.py' has routes for specific module, 'Models.py' has classes for specific module(Module 'Mentors' doesn't have this file because the module uses class - 'User' like a 'Profile' module)
4. There are HTML pages in webapp.templates
5. DataBase was created in file db.py 
6. There are technical functions for application functioning
