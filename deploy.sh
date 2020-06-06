scp -r waveshare_epd/ pi@pi-zero-display.local:/home/pi/waveshare_epd/
scp -r fonts pi@pi-zero-display.local:/home/pi/fonts/
scp -r tools pi@pi-zero-display.local:/home/pi/tools/
scp settings.py pi@pi-zero-display.local:/home/pi/settings.py

scp mappyboi.py pi@pi-zero-display.local:/home/pi/mappyboi.py
scp cowsay.py pi@pi-zero-display.local:/home/pi/cowsay.py
echo "******************** Deployed **********************"
