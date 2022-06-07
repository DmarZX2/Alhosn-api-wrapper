# Alhosn-api-wrapper :cowboy_hat_face:	
A simple and easy to use wrapper which is able to access user information on Alhosn API using user credentials

Written in Python 

**_[:warning:	It is prohibited to use this wrapper for malicious intent in any shape or form.:warning:	]_**


Installation
------------

The first way to install the latest version is from the GitHub repository:

    pip install git+https://github.com/DmarZX2/Alhosn-api-wrapper.git
    
    
The second way is using git:

    git clone https://github.com/DmarZX2/Alhosn-api-wrapper.git
    
    cd Alhosn-api-wrapper
    
    pip install .
    
    
    
    
    
## Quickstart

### Start
```python
from Alhosn import * # Importing Alhosn class

A = Alhosn() # To make it easier for ourselves, define Alhosn and use it anywhere.

A.phone = "Phone number, starts with +***" # Defining a phone number, you can do it here or from Alhosn class directly.
A.eid = "eid number without Hyphens" # Defining an eid number, you can do it here or from Alhosn class directly.

A.sendsms() # Will send an OTP to your phone which needed to be entered to other methods
```

### Activating ADB

    If you have an android device and want to automate the procedure
    of inserting your otp, you can activate the ADB module, using the
    Following steps:

1) Downloading the files from [This link](https://dl.google.com/android/repository/platform-tools-latest-windows.zip)
2) Extract the files to a folder called "adb" where your script are,
   or using environment variables.
3) You can put all the files in the adb folder or just
   "adb.exe" and "AdbWinApi.dll" are enough
4) Connect your phone to your pc, and enable usb debugging
5) When calling sendsms() method, make adb True


### Using ADB

```python
from Alhosn import * 

A = Alhosn() 

A.phone = "Phone number, starts with +***" 
A.eid = "eid number without Hyphens" 

phone, eid = A.phone, A.eid # Creating variables to access any attributes from Alhosn class for later use.
A.sendsms(adb=True, delay=5) # It's recommended to use a delay between 3-5 seconds
                             # Because recieving sms's messages takes some time

 ```

### Optimal use and recieving results

```python
from Alhosn import *

A = Alhosn()

A.phone = "Phone number, starts with +***"
A.eid = "eid number without Hyphens"


phone, eid = A.phone, A.eid
A.sendsms(adb=True, delay=5)

A.login(otp=A.otp)  # The login method will take the otp code and the rest of info given
                    # Previously and will generate a Token, for future use.

                    
A.result(display=True,
   save_photo="name")    # The main method, used to recieve the results of the user
                         # which in return can be saved as a variable to parse it
                         # you can also save the photo of the person and specify
                         # the name, also the ability to view it in console.

results = A.results # Saving the results in a variable

A.pdfout(pdftype="test",
   name="test-pdf")     # Save either the user test or vaccination vaccine
                        # You can also specify the name or leave it, and
                        # it will be called as the type



```
