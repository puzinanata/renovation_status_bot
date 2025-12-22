# Description

This project automates checking the renovation status in the AIMA personal account on the renovation portal.

Before running project on other mashine:  chmod +x run_script.sh

Create timetable for running script and save logs:
 - crontab -e
 - 0 8,11,14,17,20 * * * /path_to_project_folder/renovation_status_bot/run_script.sh /path_to_project_folder/renovation_status_bot/run_script.log 2>&1
