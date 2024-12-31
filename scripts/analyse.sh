#!/bin/bash
#this file allows us to rerun our shiny app daily 
#we suppose ShinyDashboard was cloned in dashboard file

cd  $HOME/dashboard/ShinyDashboard

# Kill any existing Shiny app processes 
pkill -f "shiny run app.py"


source  $HOME/dashboard/ShinyDashboard/env/bin/activate

#run the shiny app
shiny run $HOME/dashboard/ShinyDashboard/dashboard/app.py >> $HOME/dashboard/ShinyDashboard/dashboard/shiny_app.log 2>&1 &
