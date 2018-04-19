# FeelsLike - An Alexa Skill for Wind Chill / Heat Index
AFeelsLike is an Amazon Alexa skills app, designed to be run only within the Alexa family of products. 

This skill reports either the wind chill or the heat index, depending on temperature, for either your current location or for a designated city/location.

To use this application as a starting point for your Alexa project, you will need to incorporate the following modules into your Amazon Lambda container, as it does not provide this in it's Python environent.

* **[PYOWM](https://github.com/csparpa/pyowm)** - A fantastic weather API (Github)
* **certifi** - Validates SSL certs (_pip install certifi_)
* **[chardet](https://github.com/chardet/chardet)** - Character encoding detector (Github)
* **idna** - Domain name handler (_pip install idna_)
* **[requests](https://github.com/requests/requests)** - HTTP requests REST package (Github)
* **urllib3** - HTTP client (_pip install urllib3_)

Since I am new to Python, there are many things here that are not as Pythonistic as they probably need to be. The goal of the project was to learn the Alexa development environment and improve my python skills - not provide great code for others to model. I provide this here predominantly as an example of many of the Alexa environment interfaces and complexities.

Note that there are some suboptimal techniques that are used due to my desire to keep the package small - most notably the use of archaic Debug/Print statements. Typically I would use the Python logger services, but there is just too much overhead and complexity to include the library. I may change my mind in the future.

Also note that you will need to supply your own google geocode api key. I have stubbed it out of here.

Note: if you are not familiar with the Alexa development environment, A Cloud Guru has a great free [introductory course](https://acloud.guru/course/intro-alexa-free/dashboard) that is fantastic.