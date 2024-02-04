# AIReality

# World 1: Harry Potter 

## Overview

This project simulates the events occurring in the Harry Potter world in real-time, aligning with the real world (1 minute in the Harry Potter world equals 1 minute in the real world). It also simulates Harry Potter's thought processes. The simulation specifically focuses on the characters Ron, Hermione, and Harry, providing updates on their activities and interactions.

## Features

- **Real-Time World Simulation**: Experience the Harry Potter world as it unfolds in real time.
- **Character Focus**: The simulation centers on the key characters - Ron, Hermione, and Harry.
- **User Interaction**: Users can query the current status of the Harry Potter world or interact with Harry through text messages.

## Developer Guide
1. clone the repo and then cd into the local repo in your computer
2. run ```python3 main.py```
3. open another terminal and run ```ngrok http http://localhost:8080```
4. Copy the forward URL that looks something like this : https://5d90-128-12-123-216.ngrok-free.app
5. Go to Twilio and find the automation, paste the URL into Sandbox Configuration here: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn. Make sure to add /receive-messages as endpoint
6. Send messages to the test number via WhatsApp

## User Guide

...


## Installation

...

## Usage

The following environment variables will be needed: 
1. TWILIO_AUTH_TOKEN
2. TWILIO_ACCOUNT_SID
3. WORLD_UPDATE_INTERVAL
4. OPENAI_API_KEY

...

## License

...



