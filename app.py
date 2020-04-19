import dialogflow_handler
try:
    import requests
    import urllib
    import json
    import os
    from flask import (Flask,request, make_response)

except Exception as e:

    print("Some modules are missing {}".format(e))


# Flask app should start in global layout
app = Flask(__name__)


# whenever you make request /webhook
# Following calls are made
# webhook ->
# -----------> Process requests
# ---------------------------->get_data()


@app.route('/webhook', methods=['POST'])
def webhook():
    ihandler = dialogflow_handler.intent_handler(request.get_json())
    intent = ihandler.get_intent()
    if request.method == "POST":
        req = request.get_json(silent=True, force=True)
        if intent == "covid_cases":
            res = processRequest(req, 0)
        elif intent == "active_india":
            res = processRequest(req, 1)
        res = json.dumps(res, indent=4)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r


def processRequest(req, i):
    
    # Get all the Query Parameter
    query_response = req["queryResult"]
    print(query_response)
    text = query_response.get('queryText', None)
    parameters = query_response.get('parameters', None)
    result = req.get("result")
    if i == 0:
        city=parameters.get("geo-city")
        state=parameters.get("geo-state")
        res = check(city, state, "nn")
    elif i == 1:
        country=parameters.get("geo-country")
        res = check("nn", "nn", country)
    return res


def check(text, text2, text3):
    if text3 =="nn":
        city = text
        if city == "Kanpur":
            city = "Kanpur Nagar"
        state = text2
        r = requests.get('https://api.covid19india.org/state_district_wise.json')
        data = r.json()
        text = 'confirmed cases in '+city+f': {data[state]["districtData"][city]["confirmed"]} \n' + f'Rescent cases: {data[state]["districtData"][city]["delta"]["confirmed"]}'

    if text == "nn":
        country = text3
        r = requests.get('https://api.apify.com/v2/key-value-stores/toDWvRj1JpTXiM8FF/records/LATEST?disableRedirect=true')
        data = r.json()
        text = 'Active cases in India 'f': {data["activeCases"]}\n'+'Total Deaths' +f': {data["deaths"]}\n'+'Recovered' +f': {data["recovered"]}\n'+'Total Cases' +f': {data["totalCases"]}'

    speech = text

    return {
        "fulfillmentText": speech,
    }
    return text


def get_data():

    r = requests.get('http://www.google.com')
    return r.text







if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print ("Starting app on port %d" %(port))
    app.run(debug=True, port=port, host='0.0.0.0')

