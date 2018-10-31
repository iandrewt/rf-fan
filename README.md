#rf-fan

This is a Flask app functioning as a REST API, used to control the speed of an RF fan

##Installation
Make a copy of `sample-config.json` as `config.json` and modify it with the settings relevant to your fan(s). You'll need to use an RF receiver to find the binary codes for the different settings on your fan, the Mercator FRM98 (what this was based off of) has a authentication code and a instruction code in the one message.
