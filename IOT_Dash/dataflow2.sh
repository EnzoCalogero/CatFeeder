
echo script starting...
/home/enzo_calogero/anaconda3/bin/python  /home/enzo_calogero/CatFeeder/IOT_Dash/apps/update_dataframe.py >> /home/enzo_calogero/log1.txt 2>&1

echo stopping nginex
systemctl stop nginx
echo restarting catfeeder service
systemctl restart catfeeder.service
echo starting nginex
systemctl start nginx
echo script finished

