# AIOT - Final Project

## Credits

* Raphael Heer [(RaphiHeer)](https://github.com/RaphiHeer)
* Maurin Thalmann [(madotha)](https://github.com/madotha)

## CasaGrama - The Telegram Smart Home Bot

This Repository contains all the files of the Final Project in the AIOT Module.

It was created during the AIOT course at the Hochschule Luzern IT Department Rotkreuz in 2019.

# Telegram Bot

## Access

To access the Telegram bot, search for `@CasaGramaBot` in Telegram and start a chat with said bot (while it's running).

## Set Up Telegram Bot

The source code for the Telegram Bot is found in the `CasaGramaBot` folder. To be able to run it, you must 
enter the `TOKEN` in a file called `TOKEN.txt` in the `CasaGramaBot` folder.

**Run the Bot:** simply open the Python file through the terminal by typing `python3 casagramabot.py` 


*(The bot can only be accessed while it's running. There can only be one instance with the same token running at the same time.)*

### Azure Requirements

To access the CosmosDB and the IotHub to control devices, some files need to be created which should be containing the following:

- **COSMOSDB_URI.txt:** contains the URL for the CosmosDB database which should be accessed
- **COSMOSDB_READKEY.txt:** contains the first key for your CosmosDB to grant access to the database
- **CONNECT_STRING.txt:** contains the connection string of your IoT Hub instance
- **LED_DEVICE.txt:** contains the name of the device whose LEDs should be controlled

### Requirements

There is also a requirements.txt which contains information about the required packages. 

**Install required packages:** open the terminal, move to the projekt folder and run `pip3 install -r requirements.txt`. 

(The requirements file has been created with `pipreqs` which can also be installed with pip: `pip3 install pipreqs`)

#### IMPORTANT SIDENOTE

The required `azure_iothub_service_client` can easily be installed through pip under Windows.
If you want to use it on Mac/Linux, consider [these](https://github.com/Azure/azure-iot-sdk-python) instructions to setup the environment.


# Documentation

To access the Documentation, access the .pdf File in the `AIOT Final Report` folder.
