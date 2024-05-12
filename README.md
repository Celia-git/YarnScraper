# Yarn Scraper
## Web scraper to pull top results from yarn.com
Command line program takes optional args: *amount*, *material*, and *weight*.  Program returns listings sorted by most inexpensive rate.  To see a list of possible args, run the application with first argument "--h" or "-help"
### Optional Argument meanings:
1. **amount**: amount of listings to return (sorted by most inexpensive listings- price per weight is calculated)
     - integer 1-100
     - default: 10
2. **material**: type of yarn to sort by ("command":"value")
     -  "all":"all", "w":"wool", "mw":"merino wool", "sw":"specialty wool", "s":"silk", "a":"acrylic/synthetic", "c":"cotton", "l":"linen", "b":"bamboo"
     -  default: all
3. **weight**: thickness of the yarn to sort by ("command":"value")
     -  integer 0-6 (or all) "all":"all", "0":"lace", "1":"superfine", "2":"fine", "3":"light", "4":"medium", "5":"bulky", "6":"superbulky"
     -  default: all
### To run on windows:
- download repository
- in terminal, navigate to **yarn_scraper**
- run `pip install -r requirements.txt`
- run the program with the command (args optional): `python yarn_scraper.py [*arg1*] [*arg2*] [*arg3*]`

