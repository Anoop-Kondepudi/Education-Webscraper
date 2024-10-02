import requests
from bs4 import BeautifulSoup
import time

# Input file with all the base URLs
input_file = "chegg_all_urls.txt"
# Output file to save the paginated URLs
output_file = "chegg_paginated_urls.txt"
# Temporary file to store remaining URLs
temp_file = "temp_chegg_urls.txt"

# Headers to mimic a regular browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://www.chegg.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

# Original cookie string
cookie_string = """CVID=00cbb724-0a15-423e-b13d-9a83e63e4ece; OneTrustWPCCPAGoogleOptOut=false; usprivacy=1YNY; _pxvid=8db8c2e9-5093-11ef-ba3b-9579c6e441ef; sbm_country=US; V=3602739b7d4640ac84a793b88151073166ad382649374c.51583585; langPreference=en-US; _lc2_fpi=cd72d4805609--01j6zmw4cwbnat98gtaq50hwse; _lc2_fpi_meta=%7B%22w%22%3A1725491450269%7D; opt-user-profile=0d5e89da-315b-4a68-a3e2-7fb2c8a859b2%252C29483130476%253A29460650305%252C26337550453%253A26325940282%252C29438490978%253A29520940603%252C30046180057%253A30012820081%252C29332770947%253A29332001059%252C28358110553%253A28401670360; country_code=US; pxcts=15d49967-6da0-11ef-ae5d-85f3a0ef3152; local_fallback_mcid=55605803149046518266855520956761453505; s_ecid=MCMID|55605803149046518266855520956761453505; mcid=55605803149046518266855520956761453505; PHPSESSID=1ee28e2d8767ec8cad012d06ece2afbc; CSessionID=4a99be16-5bab-4b34-a9e8-14e26126e020; user_geo_location=%7B%22country_iso_code%22%3A%22US%22%2C%22country_name%22%3A%22United+States%22%2C%22region%22%3A%22TX%22%2C%22region_full%22%3A%22Texas%22%2C%22city_name%22%3A%22McKinney%22%2C%22postal_code%22%3A%2275069%22%2C%22locale%22%3A%7B%22localeCode%22%3A%5B%22en-US%22%5D%7D%7D; C=0; O=0; U=0; exp=C026A; expkey=7E25DA2E4C192C75B696546C618E2645; userData=%7B%22authStatus%22%3A%22Logged%20Out%22%2C%22attributes%22%3A%7B%22uvn%22%3A%223602739b7d4640ac84a793b88151073166ad382649374c.51583585%22%7D%7D; CSID=1727040360966; schoolapi=8b1dcc48-e0c9-4de5-8ec6-4cb3476ba0a3|0.25; _li_dcdm_c=.chegg.com; sbm_a_b_test=1-control; _pxff_fp=1; _pxff_uii4=1; _pxff_tm=1; forterToken=b199a0b5e0ce4489b83625bd72455843_1727042956716_249_UDF9_13ck; _px3=16672f1b4a29fd68a2b7306dc2a2ba35d22e7eac58ca1261bc93898ac423bc3f:5Lv7u1L0O+78S2ZrF3hxAuePOiALGm17SCaonDJmKJ4mB82xcKxddfI5tdmBn3vI+Pi0SsLyiFKHwsFO7ysLmQ==:1000:L3WpYQvp8EEBVgQGnPI6EubZksXDNkqcqfBfPOuI0/fmcoHowWSOFUaiRMwNYZfkhnZM1cO0BFnGpdSzPxQw0B/hvCEFWrl6qRqNFJbLuGlp0pHRePPs6pqgqfvcwseL/wTQQsCznMI1GnpHqCIn5z4SvKv69TYzHYvnkDk5LSGPE7MGRKSuzA0iFUeal0mWMBwq9PCjTp0lgfHpEDckUsnbsD9ZJ8Azc0wYqhFSiCk=; _px=5Lv7u1L0O+78S2ZrF3hxAuePOiALGm17SCaonDJmKJ4mB82xcKxddfI5tdmBn3vI+Pi0SsLyiFKHwsFO7ysLmQ==:1000:HiHqLAvFriHtJoZ8aPKZWMeUphIoPfZzO8WEKsR2CjWORZqINjYX5y+sasakoYp/l1LVlcoOnGtykKHrsys6/ZR0ipefPiAE4Xpr+RIV7wyr0strPe34GMf38CqafnCEHeA/q7GtxQb5OWY4b6mvJ7nAFN5ejhyFvgqTI6tNjJQdRRenZRYDrEZVIAUkzI48egwagDpHfcONRz1H7qi4TsPVmJOXreqrN8wA9j/WLPPHxgSmUm+6knADnFqSBydA5wZZAwqoAIaNG2vwo/Pc8Q==; _pxde=419442d5465d969594a2419e97d97b29957fd3b85e3f671d5cbf82163dd86130:eyJ0aW1lc3RhbXAiOjE3MjcwNDI5NTk0NzV9; id_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IjYybXg1QHNteWt3Yi5jb20iLCJpc3MiOiJodWIuY2hlZ2cuY29tIiwiYXVkIjoiQ0hHRyIsImlhdCI6MTcyNzA0Mjk2MiwiZXhwIjoxNzQyNTk0OTYyLCJzdWIiOiIxYWViZDUyMC1hZTc1LTQzOWItYWM0OC03MjVkOGRkNWMwYTAiLCJyZXBhY2tlcl9pZCI6ImFwdyIsImN0eXAiOiJpZCIsImlkc2lkIjoiYmJhN2MxNzQiLCJpZHN0IjoxNzI3MDQyOTYyOTM1LCJpZHNnIjoicGFzc3dvcmQiLCJjbG5tIjoib25lYXV0aCJ9.B2X6R3ce99hf7uQ9mQlKn7KFa3-uIcdV9fQfPfdFdpiOLXqJkuCaFHARkijO82PMirnUSiWADKmAcFA6xYwpkAUks-W6Kbdg81fysNBbeEYzJLB1TUAMQPbpEvoyrFAq8nooSs2XCp1h4zsLCU4dXCnPSHAGyz5zpLcVEbMNxzPlWDWueGhfTH8kTnr9H1z9fwUNZs-ynrkl1uPjchmvrtCskdIrecxycweIChCED2uA3XbzznbxNtsIkrIkkiEAtOL406eXRivuQztCVo-TEu8YPjpszx7_e5XrNXUYXnHb8LGKCrIPerG2oAe2ZB5KMeh0nfgdfZrVQNRKOh_0fQ; access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodWIuY2hlZ2cuY29tIiwic3ViIjoiMWFlYmQ1MjAtYWU3NS00MzliLWFjNDgtNzI1ZDhkZDVjMGEwIiwiYXVkIjpbInRlc3QtY2hlZ2ciLCJodHRwczovL2NoZWdnLXByb2QuY2hlZ2cuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTcyNzA0Mjk2MiwiZXhwIjoxNzI3MDQ0NDAyLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIGFkZHJlc3MgcGhvbmUgb2ZmbGluZV9hY2Nlc3MiLCJndHkiOiJwYXNzd29yZCIsImF6cCI6IkZpcGozYW5GNFV6OE5VWUhPY2JqTE14NnE0elZLRU9lIiwicmVwYWNrZXJfaWQiOiJhcHciLCJjaGdocmQiOnRydWUsImN0eXAiOiJhY2Nlc3MifQ.RQpRNCVIjpaTImoof-Liq4GlRtrIbYB7ouWuR8JZfAFGTFwy92ZBQEt16yLDAJMaaUpLvWY0G3oevUDQukAxoXfp1LDE9i3Yu6RT-m55uDiK36d9ydH4DIGGSoYWvT7aJoaJKwUsJiUC-v6wzRurU1YqNOUnvvQngJrGiMbqEGb0XRC-ISVreSM2VlMG4Ki-Wn2C_xDpyDzL0wXLcwUaXmNhPm0fMA_TAeLDB4ejmoBeWjdZS6JrhB-1pO4oBe5Fh9-FxjqX3myDbGWi7OBCaN8lmzA4BQ5kkOUPYy5CFxhfIj1y9Idu79aHOHTvB_AbmrixoQLSookPxJ2YL1UPHw; is_new_login_mweb_to_app_expansion_modal=true; SU=YEdGJMIP3TxlIFYxHiDLaiAlO6TkzwIxV1V96wY5RZhlxtCU_TyjrSv0eNATROvFarO5KNNu_OtstejsFof-j4SwYpY7JZch-FGv2iDcBbTUxjuhcq2BcMqrHdPYil3X; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Sep+22+2024+17%3A09%3A23+GMT-0500+(Central+Daylight+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a3c3b8bb-7d64-4caa-9475-949c0b51840d&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=snc%3A1%2Cfnc%3A1%2Cprf%3A1%2CSPD_BG%3A1%2Ctrg%3A1&AwaitingReconsent=false; _sdsat_authState=Hard%20Logged%20In; _sdsat_cheggUserUUID=1aebd520-ae75-439b-ac48-725d8dd5c0a0; _px3=060373714c6a2bbadd32c356158a9836a1b616ca43d1c0b3699f312c244ef582:a6CrhF7oZfgeviE0Rn3Y4yarSAuq+feKQPJpZHcp/YC+P0fQ+NODzSY5B0SGzz5JkCDewz+wQ7FVbBB1ZjOAwA==:1000:OrzYudzOwkjJlh9LEDeqfM+u0y7+qfHGqFSw8Wj3iwqoVNPWGancgksQF3Y68QQhK8vS/wPy0nrykEN4vBvtMMUiAoWMK4Ht9ewmfq1jqYsIBlSE2Ws2Xv47ETRX/SXW2qEa+B6mkjlFd2/SEtlhSvw8HEBDlFAqC0rvmeiXhxHKu7UflPZRiUL953wNSsiw6EnNT9K8hPTRvfK9VQpUCmkMSfUzBUe5mnh5iEdmMjM=; _pxde=72f01a4264948c01836ee74ffd3fd0aaa404752a367bed1c26ab0a4bf95e603a:eyJ0aW1lc3RhbXAiOjE3MjcwNDI5Njc5NjJ9"""

# Function to parse the cookie string into a dictionary
def parse_cookies(cookie_string):
    cookies = {}
    for item in cookie_string.split('; '):
        try:
            key, value = item.split('=', 1)
            cookies[key] = value
        except ValueError:
            print(f"Skipping malformed cookie: {item}")
    return cookies

# Parse the cookie string
cookies = parse_cookies(cookie_string)

# Function to get the total number of pages from the selector
def get_total_pages(url, session):
    try:
        response = session.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the element containing the number of pages using the selector
        pages_element = soup.select_one('#eggshell-2 > ul > li:nth-child(6)')
        
        if pages_element:
            # Extract the text and convert it to an integer
            total_pages = int(pages_element.text.strip())
            return total_pages
        else:
            # If the selector is not found, return 1 as default (only the base page)
            return 1
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return -1  # Indicate an error with -1

# Function to generate and save paginated URLs
def generate_paginated_urls(input_file, output_file):
    with requests.Session() as session:
        with open(input_file, 'r') as infile, open(output_file, 'a') as outfile, open(temp_file, 'w') as temp:
            for base_url in infile:
                base_url = base_url.strip()
                total_pages = get_total_pages(base_url, session)
                
                if total_pages == -1:
                    print(f"Stopping script due to an error at {base_url}.")
                    break  # Stop the script if an error occurred
                
                # Write paginated URLs to the output file
                for page in range(1, total_pages + 1):
                    if page == 1:
                        outfile.write(f"{base_url}\n")
                    else:
                        paginated_url = f"{base_url}?page={page}"
                        outfile.write(f"{paginated_url}\n")
                
                # Print status and delay to avoid server overload
                print(f"Processed {base_url} with {total_pages} pages.")
                time.sleep(1)  # Optional delay
            
            # Write unprocessed URLs to a temporary file for later resumption
            temp.write(f"{base_url}\n")
        
    # Replace input file with the remaining URLs in temp file
    import os
    os.replace(temp_file, input_file)

# Run the function to generate paginated URLs
generate_paginated_urls(input_file, output_file)

print(f"Script completed. Processed URLs have been saved to {output_file}. Remaining URLs are in {input_file}.")
