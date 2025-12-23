# Description

This project automates checking the renovation status in the AIMA personal account on the renovation portal.

 - Copy project to your local machine
 - Open terminal and go to project folder
 - Create file with name ".env" and put into project folder
 - Content this file copy from file env.txt and put your credentials
 - Before running project:  chmod +x run_script.sh
 - Run project: ./run_script.sh

If you want to create timetable for running script and save logs:
 - crontab -e
 - check status every 3 hours from 8-00 to 20-00 to put this line into opened file, change path to your project: 0 8,11,14,17,20 * * * /path_to_project_folder/renovation_status_bot/run_script.sh /path_to_project_folder/renovation_status_bot/run_script.log 2>&1
 - ctrl+ O (capital letter O) to write changes
 - enter to save changes
 - ctrl+X  to exit crontab file
