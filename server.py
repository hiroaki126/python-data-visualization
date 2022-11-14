import os
from time import sleep
import json
from flask import Flask, request, jsonify

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return "Scrapping Rest API Server"

@app.route('/scrap', methods=['POST'])
def scrap():
    body = json.loads(request.data)

    EqCategory = body['EqCategory']
    Url = body['Url']

    session = requests.Session()
    options = Options()
    options.headless = False

    options.add_argument("user-data-dir=C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")
    options.add_argument("--window-size=1920,1200")
    # driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
    # webdriver.Firefox(executable_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'geckodriver.exe'))
    # driverlocation = executable_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/chromedriver.exe')
    driverlocation = executable_path = 'c:/Project/Rodolfo/Machinery/webdriver/chromedriver.exe'

    print(driverlocation.replace('\\', '/'))
    s = Service(driverlocation)
    driver = webdriver.Chrome(service=s)

    driver.get(Url)
    sleep(12)

    assert "No results found." not in driver.page_source
    html = driver.page_source
    driver.close()

    soup = BeautifulSoup(html, 'lxml')
    images = []
    response = {
        "StartDate": "",
    }

    def getPropertyText(name, attr):
        element = soup.find(name, attr)
        return element.text if element is not None else ""

    def getProertyByDataKey(dataKey, index=0):
        parent = soup.find('div', {"data-key": dataKey})
        if parent is not None:
            child = parent.findAll("", {"class": "static-value"})
            return child[0].text if child is not None and len(child) > index else ""
        return ""

    if html.find("rba-product-details-container") > -1:
        gallery = soup.find("div", {'data-testid': 'GalleryItemGrid'})
        galleryItems = gallery.findAll('object', {"data-testid": "Image"})
        for galleryItem in galleryItems:
            images.append(galleryItem['data'])

    elif html.find('item-details-carousel-container') > -1:
        galleryItems = soup.findAll("img", {"class": "rba-carousel-slide-image"})
        for galleryItem in galleryItems:
            images.append(galleryItem['data-loadsrc'])

    else:
        pass

    response['PrimaryImage'] = images

    response['StartDate'] = getPropertyText('time', {"class": "auction-date"})

    htmlLocation = getPropertyText('a', {"class": "auction-location-link"})
    if htmlLocation == "":
        meterNode = soup.find('div', {"data-testid": "meter-table"})
        if meterNode is not None:
            meterColumnNodes = meterNode.findAll('div', {"data-testid": "meter-column"})
            if meterColumnNodes is not None and len(meterColumnNodes) > 0:
                meterDataEntry = meterColumnNodes[0].find('div', {'class': 'data-entry'})
                if meterDataEntry is not None:
                    htmlLocation = meterDataEntry.find('div', {'data-testid': 'Box'}).text

    response['Location'] = htmlLocation

    htmlYear = getPropertyText('a', {"class": "year"})
    htmlModel = getProertyByDataKey("BoomModel")
    htmlMake = getProertyByDataKey("BoomManufacturer")
    htmlVIN = getProertyByDataKey("AS400SerialOrVehicleIdNumber")

    if htmlYear == "" or htmlModel == "" or htmlMake == "" or htmlVIN == "":
        accordionNode = soup.find('div', {'data-testid': 'accordion'})
        if accordionNode is not None:
            accordionDescription = accordionNode.findAll('div', {'data-testid': 'Description'});
            if accordionDescription is not None and len(accordionDescription) > 0:
                for accordionItem in accordionDescription:
                    accordionTextNode = accordionItem.findAll('p', {'data-testid': 'Text'})
                    if accordionTextNode is not None and len(accordionTextNode) == 2:
                        if accordionTextNode[0].text == 'Year' and htmlYear == "":
                            htmlYear = accordionTextNode[1].text
                        elif accordionTextNode[0].text == 'Model' and htmlModel == "":
                            htmlModel = accordionTextNode[1].text
                        elif accordionTextNode[0].text == 'Manufacturer' and htmlMake == "":
                            htmlMake = accordionTextNode[1].text
                        elif accordionTextNode[0].text == 'VIN' and htmlVIN == "":
                            htmlVIN = accordionTextNode[1].text

    response['EqYear'] = htmlYear
    response['EqModel'] = htmlModel
    response['EqMake'] = htmlMake
    response['EqSN'] = htmlVIN

    response['TruckYear'] = getProertyByDataKey("AS400YearOfManufacture")
    response['TruckMake'] = getProertyByDataKey("AS400ManufacturerName")
    response['TruckCondition'] = getProertyByDataKey("AS400Odometer")
    response['Engine'] = getProertyByDataKey("Manufacturer", 1)
    response['TruckTrans'] = getProertyByDataKey("Manufacturer")
    response['Capacity'] = getProertyByDataKey("BoomWeight")
    response['Length'] = getProertyByDataKey("MaxLength")

    response['4WD'] = getProertyByDataKey("AxleConfiguration")
    response['CW'] = getProertyByDataKey("CW")

    response['CabCanopy'] = getProertyByDataKey("CabCanopy")
    response['RearAuxiliaryHydraulics'] = getProertyByDataKey("RearAuxiliaryHydraulics")

    response['AS400Odometer'] = getProertyByDataKey("AS400Odometer")
    response['Meters'] = 0
    response['Ripper'] = 0

    if EqCategory == 'Dozer':
        response['AS400AssetType'] = getProertyByDataKey("AS400AssetType")

    return json.dumps(response)

app.run(host='0.0.0.0')

