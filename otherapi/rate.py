#!/usr/bin/env python

#https://github.com/jzempel/fedex

#workon fedex-second-api

from fedex.services import (FedexService, AddressService, RateService, ShipmentService, TrackingService)
from datetime import datetime

from fedex.services import FedexService
from fedex.config import FedexConfiguration
import os.path

file_path = os.path.abspath(__file__)
dir_name = os.path.dirname(file_path)
file_name = os.path.join(dir_name, "cred.cfg")

CONF = FedexConfiguration(wsdls='beta', file_name='cred.cfg') #file_name)



#serv = FedexService



def set_from_address(address):
    """Set a test 'from' address.
    :param address: The address to populate.
    """
    address.StreetLines = ["300 Brannan St.", "Suite 405"]
    address.City = "San Francisco"
    address.StateOrProvinceCode = "CA"
    address.PostalCode = "94107"
    address.CountryCode = "US"

def set_label(label):
    """Set a test label.
    :param label: The label specification to populate.
    """
    label.LabelFormatType = "COMMON2D"
    label.LabelStockType = "PAPER_4X6"
    label.LabelPrintingOrientation = "TOP_EDGE_OF_TEXT_FIRST"
    label.LabelOrder = "SHIPPING_LABEL_FIRST"
    label.ImageType = "PNG"

def set_package(package):
    """Set a test package.
    :param package: The package line item to populate.
    """
    package.PhysicalPackaging = "BOX"
    package.Weight.Value = 1.0
    package.Weight.Units = "LB"

def set_selection_details(selection_details):
    """Set test selection details.
    :param selection_details: The tracking selection details to populate.
    """
    selection_details.CarrierCode = "FDXG"
    selection_details.OperatingCompany = "FEDEX_GROUND"
    selection_details.PackageIdentifier.Type = "TRACKING_NUMBER_OR_DOORTAG"
    selection_details.PackageIdentifier.Value = "800026015050023"

def set_shipment(shipment, package):
    """Set a test shipment.
    :param shipment: The shipment to populate.
    :param package: The package to add.
    """
    shipment.DropoffType = "REGULAR_PICKUP"
    shipment.ServiceType = "FEDEX_GROUND"
    shipment.PackagingType = "YOUR_PACKAGING"
    shipment.Shipper.Contact.CompanyName = "Pickwick & Weller"
    shipment.Shipper.Contact.PhoneNumber = "8777386171"
    set_from_address(shipment.Shipper.Address)
    shipment.Recipient.Contact.PersonName = "POTUS"
    shipment.Recipient.Contact.PhoneNumber = "1234567890"
    set_to_address(shipment.Recipient.Address)
    shipment.RateRequestTypes = ["NONE"]
    shipment.RequestedPackageLineItems.append(package)
    shipment.PackageCount = len(shipment.RequestedPackageLineItems)
    shipment.ShippingChargesPayment.PaymentType = "SENDER"
    shipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber =\
        CONF.account_number

def set_to_address(address):
    """Set a test 'to' address.
    :param address: The address to populate.
    """
    address.StreetLines = ["1600 Pennsylvania Avenue NW"]
    address.City = "Washington"
    address.StateOrProvinceCode = "DC"
    address.PostalCode = "20500"
    address.CountryCode = "US"

class FedexTestCase:

    def test_address_service(self):
        """Test the address service.
        """
        service = AddressService(CONF)
        address = service.create_address()
        set_to_address(address.Address)
        result = service.validate([address])
        print result

    def test_rate_service(self):
        """Test the rate service.
        """
        service = RateService(CONF)
        shipment = service.create_shipment()
        package = service.create_package()
        package.GroupPackageCount = 1
        set_package(package)
        set_shipment(shipment, package)
        result = service.get_rates(shipment)
        print result

    def test_shipment_service(self):
        """Test the shipment service.
        """
        service = ShipmentService(CONF)
        shipment = service.create_shipment()
        shipment.ShipTimestamp = datetime.now()
        set_label(shipment.LabelSpecification)
        package = service.create_package()
        set_package(package)
        set_shipment(shipment, package)
        result = service.process(shipment)
        print result
        details = result.CompletedShipmentDetail.CompletedPackageDetails[0]
        image = details.Label.Parts[0].Image
        binary = a2b_base64(image)

        with NamedTemporaryFile() as png_file:
            png_file.write(binary)

            if Image:
                png_file.seek(0)
                Image.open(png_file.name).show()

        tracking_id = details.TrackingIds[0]
        result = service.delete(tracking_id)
        print result

    def test_tracking_service(self):
        """Test the tracking service.
        """
        service = TrackingService(CONF)
        selection_details = service.create_selection_details()
        set_selection_details(selection_details)
        result = service.track(selection_details)
        print result

    def test_fedex_service(self):
        """Test the fedex service.
        """
        service = FedexService(CONF)
        # Addresses
        address = service.address_service.create_address()
        set_to_address(address.Address)
        result = service.get_addresses([address])
        print result
        # Rates
        shipment = service.rate_service.create_shipment()
        package = service.rate_service.create_package()
        package.GroupPackageCount = 1
        set_package(package)
        set_shipment(shipment, package)
        result = service.get_rates(shipment)
        print result
        # Shipments
        shipment = service.shipment_service.create_shipment()
        shipment.ShipTimestamp = datetime.now()
        set_label(shipment.LabelSpecification)
        package = service.shipment_service.create_package()
        set_package(package)
        set_shipment(shipment, package)
        result = service.get_shipment(shipment)
        print result
        tracking_id = result.CompletedShipmentDetail.\
            CompletedPackageDetails[0].TrackingIds[0]
        result = service.remove_shipment(tracking_id)
        print result
        # Tracking
        selection_details = service.tracking_service.create_selection_details()
        set_selection_details(selection_details)
        selection_details.PackageIdentifier.Value = tracking_id.TrackingNumber
        result = service.get_tracking(selection_details)
        print result

def main():
   f = FedexTestCase()
   f.test_address_service()
   #f.test_rate_service()
   #f.test_shipment_service()
   #f.test_tracking_service()
   #f.test_fedex_service()
main()
