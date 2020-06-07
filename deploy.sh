rm **/**/*.pyc

scp -r waveshare_epd pi@pi-zero-display.local:/home/pi/
scp -r fonts pi@pi-zero-display.local:/home/pi/
scp -r tools pi@pi-zero-display.local:/home/pi/
scp settings.py pi@pi-zero-display.local:/home/pi/

scp mappyboi.py pi@pi-zero-display.local:/home/pi/
scp cowsay.py pi@pi-zero-display.local:/home/pi/
echo "******************** Deployed **********************"
