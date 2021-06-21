cd /home/takis/Desktop/sckool/my-crypto-app
script=crypto_daily_populate.py
startdate=$(date +'%Y-%m-%d %H:%M:%S')
/home/takis/anaconda3/bin/python $script
enddate=$(date +'%Y-%m-%d %H:%M:%S')
echo $script execution : $startdate - $enddate