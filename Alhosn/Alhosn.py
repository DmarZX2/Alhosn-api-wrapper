import time
from typing import Union
import base64
import phonenumbers
import requests
import collections
from colorlog import ColoredFormatter
import logging
import sys
from phonenumbers.phonenumberutil import NumberParseException
from fake_useragent import UserAgent
import os
import re
import json

#<------Logging Section------>
logging.root.setLevel(logging.DEBUG)
formatter = ColoredFormatter("%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s")
stream = logging.StreamHandler()
stream.setFormatter(formatter)
log = logging.getLogger('Alhosn-api')
log.addHandler(stream)







class AlHosnGeneralERROR(Exception):
    """Exception raised when any error happens except for network errors"""

    def __init__(self, msg='An Error Has Occurred', *args):
        super().__init__(msg, *args)

class AlHosnNetworkERROR(Exception):
    """Exception raised when any network errors happens"""

    def __init__(self, msg='A Network Error Has Occurred', *args):
        super().__init__(msg, *args)



class Alhosn(object):
    """
        The heart of this wrapper, holds all methods to access the API


        Methods:

        - `sendsms()` --> Send sms to phone and recieve it automatically if adb is enabled.
        - `login()` --> retrieve otp, phone and eid and login to the API subsequently saving the TOKEN to use it in other functions.
        - `result()` --> The main method using all info gathered from sendsms, and login methods to retrieve all contents of the user, including person photo.
        - `pdfout()` --> save a pdf of user test or vaccination info

        """

    url = "https://m.alhosnapp.ae/greencode/{}/{}"
    def __init__(self, eid=None, phone=None, otp=None):

        self.eid = eid
        self.phone = self.__processphone(phone) if not phone is None else phone
        self.otp = otp
        self.token = None
        self.uid = None
        self.nameAr = None
        self.nameEn = None
        self.ut = None
        self.passlist = None
        self. results = None

    def __iter__(self):
        """
            Return an iterable list of all attributes
            with their values.

            Including: Phone Number, eid, etc...
        """
        return iter((self.__dict__.items()))

    def __setattr__(self, name, value):
        """
        Handles processing of phone numbers when accessing attributes by user, ex. phone =123.
        And checking if ID,eid is an integer
        """
        if name == 'phone':

            if value is not None:
                try:
                    self.__processphone(value)
                except AlHosnGeneralERROR:
                    raise
                finally:
                    return super().__setattr__(name, value)
        elif name == 'eid':
            if value is not None:
                try:
                    if not isinstance(value, int):
                        try:
                            int(value)
                        except ValueError:
                            sys.exit(log.warning("Please provide eid as an integer, and without -"))
                finally:
                    return super().__setattr__(name, value)
        else:
            return super().__setattr__(name, value)

    def __getattribute__(self, attr):
        """
            Handles user requesting already set attributes, and processing phone data and eid.
        """
        if attr == 'phone':
            return self.__processphone(super().__getattribute__('phone'))
        elif attr == 'eid':
            try:
                return int(super().__getattribute__('eid'))
            except ValueError:
                sys.exit(log.warning("Please provide eid as an integer, and without -"))

        else:
            return super(Alhosn, self).__getattribute__(attr)

    def __getattr__(self, attr):
        """
        If a user wrote a wrong method or attribute, this method will try to find similar ones, if it finds one it will

        alert the user and correct them, if it didn't find any it will tell the user that there is no such argument.
        """
        atrribs =  list(self.__dict__)
        from difflib import SequenceMatcher
        nearlist_attr = (list(map(lambda d: SequenceMatcher(a=attr, b=d).ratio(), atrribs)))
        method_list = [func.strip('__') for func in dir(Alhosn) if getattr(Alhosn, func)]
        nearlist_method = (list(map(lambda d: SequenceMatcher(a=attr, b=d).ratio(), method_list)))
        nearboolattr = self.__is_close(max(nearlist_attr), 0.8) or max(nearlist_attr) > 0.8
        nearboolmethod = self.__is_close(max(nearlist_method), 0.8) or max(nearlist_method) > 0.8
        if attr == 'phone':
            # print(attr)
            return log.error("Phone has no value")
        if attr == 'eid':
            return log.error("Please provide eid as an integer, and without -")
        if nearboolattr:
            return (log.error(
                "There is no attribute called '{}', Did you mean '{}'!".format(
                    attr, atrribs[nearlist_attr.index(max(nearlist_attr))])))
        else:
            if nearboolmethod:
                return (log.error(
                    "There is no method called '{}', Did you mean '{}'!".format(
                        attr, method_list[nearlist_method.index(max(nearlist_method))])))
            else:
                # print(atrribs)
                return log.warning("No method / attribute is called '{}' !".format(attr))

    def set_eid(self, eid):
        self.eid = eid

    def set_phone(self, phone):
        self.phone = self.__processphone(phone)

    @staticmethod
    def __adb_getotp(delay = 0):
        """
        Gaining control of the adb package with android devices, to gather latest otp code automatically
        """
        time.sleep(delay)
        try:
            os.chdir(r"adb")
        except FileNotFoundError:
            log.warning("Cant Find The folder ADB, trying global command")

        retrieve_sms = os.popen('adb shell content query --uri content://sms'
                                ' --projection _id,address,body,read,date,type').read()
        message = []

        for i in retrieve_sms.split('\n'):
            if "AlhosnApp" in i:
                # print(a.split('\n').index(i))
                full_row_content = retrieve_sms.split('\n')[
                                   retrieve_sms.split('\n').index(i):retrieve_sms.split('\n').index(i) + 2]
                otp_num = re.findall('\d{6}', full_row_content[1].split(',')[0])

                # d = re.findall('Row: \d{3}|Row: \d{2}|Row: \d', full_row_content[0])
                # e = re.findall('address=AlhosnApp', full_row_content[0])
                # f = re.findall('body=OTP', full_row_content[0])
                time_un_formatted = re.sub('date=', "", full_row_content[1])
                time_formatted = re.findall('\d{13}', time_un_formatted)
                message.extend((otp_num, time_formatted))
        act_message = [item.strip('Row: ') for sublist in message for item in sublist]
        # print(act_message)
        try:
            max_time = max(act_message[1::2])
        except ValueError:
            raise AlHosnGeneralERROR("adb service isn't enabled")
        
        return act_message[0::2][act_message.index(max_time) - 1]

    @staticmethod
    def __processphone(phone):
        """

        processing phone numbers that start with intn numbers, using phonenumbers library

        """
        phone = str(phone)

        if phone.startswith("+"):
            phoneplus = phone
        else:
            phoneplus = '+' + phone

        try:
            newphone = phonenumbers.is_possible_number(
                phonenumbers.parse(phoneplus))
        except NumberParseException as e:
            raise AlHosnGeneralERROR("Phone Number is formmated wrongly!," + " Possiple reason --> "+e.args[0])


        if newphone:
            return phone.strip('+')
        else:
            log.warning("Phone Number is formmated wrongly!")
            raise AlHosnGeneralERROR("Wrong Number Formmating")

    @staticmethod
    def __is_close(a, b):
        a_str = str(a)
        a_prec = len(a_str.split('.')[1]) if '.' in a_str else 0
        b_str = str(b)
        b_prec = len(b_str.split('.')[1]) if '.' in b_str else 0
        prec = min(a_prec, b_prec)
        return round(a, prec) == round(b, prec)

    @property
    def getphone(self):
        if not self.phone is None:
            return str(self.phone)
        else:
            log.warning("No phone number was given. use set_phone() method")
            return "No Phone provided"

    @property
    def geteid(self):
        return str(self.eid)


    def sendsms(self, phone=None, eid=None,adb = False, delay=0):
        """

        method to send otp to phone to use it to login

        :param phone: phone number
        :param eid: eid number
        :param adb: adb functionallity, True if you have an android phone
        :param delay: recommended to use preferably 3-5 seconds, delay used to wait before reading sms contents
        :return: status code
        """
        response_msg = None
        status = None


        if phone is None:
            phone = self.phone
            if phone is None:
                sys.exit(log.error("Please provide a valid phone number"))
        elif not phone is None:
            try:
                phone = self.__processphone(phone)
            except AlHosnGeneralERROR:
                sys.exit(log.error("Please provide a valid phone number"))

        if eid is None:
            eid = self.eid
            if eid is None:
                sys.exit(log.error("Please provide an eid value"))
        else:
            self.eid = eid

        smsurl = self.url.format("auth", "sendsms")

        data = {
            "eid": eid,
            "phone": phone
        }
        try:
            response = requests.post(smsurl, json=data, headers={'User-Agent': UserAgent().random})
        except requests.exceptions.RequestException as e:
            log.error(e)
            raise SystemExit()

        if response.status_code != 200:
            # log.error("Can't Connect to the network")
            raise AlHosnNetworkERROR("Can't Connect to the network")

        a_b = collections.OrderedDict(response.json()['responseHeader'])
        # print(a_b)

        for key, value in a_b.items():
            if key in {'msg'}:
                response_msg = value
            if key in {'status'}:
                status = value

        # 200: "pass",
        # 1047: "You are requesting OTP too frequently. Please try again later.",
        # 1006: "There is no record for this ID. Please double-check and try again.",
        # 1020: "Something went wrong. You can try again later.",
        # 1001: "The mobile number you entered does not match with your ID. You may need to log in via 97****906, 97****323, 97****063, 97****549.",
        # 1007: "The ID or phone number you entered is not valid. Please double-check and try again."

        # If response_msg = None That means it passed and a sms message will be sent
        try:    
            if status != 200:
                raise AlHosnNetworkERROR(status, response_msg)
        except AlHosnNetworkERROR as e:
            log.warning(e.args[1])
            return status

        if adb:
            try:
                self.otp =  self.__adb_getotp(delay)
            except AlHosnGeneralERROR as e:
                log.error(e.args[0])

        return status


    def login(self, otp:Union[int, str],phone=None, eid=None):
        """
        log in using otp, phone and eid to gather token value used by proceeding functions to work

        :param otp: otp code used to log in, gained manually of automatically using adb
        :param phone: phone number
        :param eid: eid number
        :return: status code
        """
        if phone is None:phone = self.phone
        else:self.phone = phone

        if eid is None:
            eid = self.eid
            if eid is None:sys.exit(log.error("Please provide an eid value"))
        else:self.eid = eid

        if otp is None:
            otp = self.otp
            if otp is None:sys.exit(log.warning("Please provide an OTP code or enable adb to recieve sms"
                                       " messages from your phone directly!"))
        else:
            if isinstance(otp, int) or isinstance(otp, str):
                try:
                    int(otp)
                    otp = otp
                except ValueError:
                    sys.exit(log.warning("Make sure OTP is an integer"))
            else: sys.exit(log.warning("Please provide an otp code"))

            log.info("OTP is {}".format(otp))

        loginurl = self.url.format("auth", "login")

        data = {
            "eid": eid,
            "phone": phone,
            "code": otp
        }

        try:
            response = requests.post(loginurl, json=data, headers={'User-Agent': UserAgent().random})
        except requests.exceptions.RequestException as e:
            log.error(e)
            raise SystemExit()

        if response.status_code != 200:
            raise AlHosnNetworkERROR("Can't Connect to the network")

        status = None
        for key, value in collections.OrderedDict(response.json()['responseHeader']).items():
            if key in {'msg'}:
                response_msg = value
            if key in {'status'}:
                status = value
        response_msg = None
        try:
            if status != 200:
                raise AlHosnNetworkERROR(status, response_msg)
        except AlHosnNetworkERROR as e:
            log.warning(e.args[1])
            return status

        for key, value in collections.OrderedDict(response.json()['response']).items():
            if key in {'token'}:
                self.token = value
                log.warning(self.token)
            if key in {'list'}:
                response_info = value[0]
                self.uid = response_info['uid']
                self.nameAr = response_info['nameAr']
                self.nameEn = response_info['nameEn']
                self.ut = response_info['ut']
                self.passlist = response_info['passlist']
        return status

    def result(self, display=False, save_photo:str=None):
        """
        Method used to gather result in a dictionary type, and can display content in command propmt if user wants so,
        and able to save the user photo

        :param display: used to display content in cmd
        :param save_photo: save the user photo
        :return: status code
        """

        params = {
            'eid': self.eid,
            'uid': self.uid
        }
        headers = {
            'User-Agent': UserAgent().random,
            'token': self.token
        }

        resulturl = self.url.format("pass", "results")

        try:
            response = requests.get(resulturl, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            log.error(e)
            raise SystemExit()

        print(response)

        status = None
        response_msg = None
        self.results = response.json()['response']

        for key, value in collections.OrderedDict(response.json()['responseHeader']).items():
            if key in {'msg'}:
                response_msg = value
            if key in {'status'}:
                status = value

        if response_msg is None: pass
        else: log.warning(response_msg)


        if display:
            if not self.results is None:
                log.info(json.dumps(self.results, indent=2))
            else: log.warning("There are no results")

        if not save_photo is None:
            for key, value in collections.OrderedDict(response.json()['response']).items():
                if key in {'photo'}:
                    photoname = value
                    imgdata = base64.b64decode(photoname)
                    filename = '{}.jpg'.format(save_photo)
                    with open(filename, 'wb') as f:
                        f.write(imgdata)




        return status

    def pdfout(self, pdftype: str, name = None):

        """
        output pdf files from the API
        :param pdftype: The type of pdf you want to save. either test, or vaccine
        :param name: name of pdf, the type of pdf will be used as the name if none is given
        :return: status code
        """
        if not pdftype in ["test", "vaccine"]: raise AlHosnGeneralERROR("pdf types allowed : test or vaccine")
        name = pdftype if name is None else name
        params = {
            'eid': self.eid,
            'uid': self.uid,
            'type': pdftype
        }
        headers = {
            'User-Agent': UserAgent().random,
            'token': self.token
        }

        pdfouturl = self.url.format("data", "pdf-url")

        try:
            response = requests.get(pdfouturl, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            raise AlHosnNetworkERROR("Can't Connect to the Network possible problem -->" + str(e))

        status = None
        for key, value in collections.OrderedDict(response.json()['responseHeader']).items():
            if key in {'msg'}:
                response_msg = value
            if key in {'status'}:
                status = value
        response_list = collections.OrderedDict(response.json()['response']).items()

        for key, value in response_list:
            if key in {'url'}:
                pdf_request = requests.get(value)
                file = open("{}.pdf".format(name), "wb")
                file.write(pdf_request.content)
                file.close()
        return status
