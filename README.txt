Plantwaterer is a Flask webapp on python for controlling a plant watering system. The system utilizes SQLite to track users and watering events.
The program also simultaneously hosts an MQTT server for pushing watering commands and data to a subscribed ESP32 running MicroPython. The ESP32 is attached to a water pump and reservoir for absent watering.

User registration is limited to already active accounts.
Website displays past watering statistics and allows for scheduling future watering times.


Developed with love for Hannah W.

