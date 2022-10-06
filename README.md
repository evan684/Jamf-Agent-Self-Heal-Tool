Jamf-Agent-Self-Heal-Tool
=========================
Example CLI tool for utilizing Jamf Pro's self healing functionaility which is only avalible via the API.

Setting up Dependencies
-------------------------

1. Ensure ``pip`` and ``pipenv`` are installed.
2. Clone repositiory: ``git clone git@github.com:evan684/Jamf-Agent-Self-Heal-Tool.git``
2. ``cd`` into the repository.
4. Fetch development dependencies ``make install``
5. Activate virtualenv: ``pipenv shell``

Usage
-----

Edit the script and set your jamf URL in the jamfURL var.

Run set the script as executable
::

    $ chmod u+x jamf_self_heal.py
  
Run the script
::
 
    $ ./jamf_self_heal.py
  
The script will prompt you for your jamf username and password to access the API. 

Use the --help menu for parameter more info aboout usage and optional parameters.
