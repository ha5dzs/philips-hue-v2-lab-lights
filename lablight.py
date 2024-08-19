# This is a script that interacts with the Hue bridge.
import os # File banging
import json # Because we are working in json
import urllib3 # To disable the warning about SSL
import requests # The Hue API v2 is over http requests.
import time # For the delay in setting the lights
import sys # For processing input arguments

# Input variables. D65 illuminant, max intensity
cie_x = 0.31272
cie_y = 0.2903
intensity = 100 # in percent


# From: https://stackoverflow.com/questions/15445981/how-do-i-disable-the-security-certificate-check-in-python-requests
# Suppress only the single warning from urllib3.
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

# From: https://www.delftstack.com/howto/python/set-maximum-retries-for-requests-in-python/
requests.adapters.DEFAULT_RETRIES = 256

# If you don't know your bridge's IP address, then check here: https://discovery.meethue.com/
local_ip = "192.168.11.50"

# We will overwrite these programmatically.
username = "Bruce Wayne"
client_key = "Gotham Bank Account 262144"

# Process input arguments
if(len(sys.argv) != 4):
    #print(len(sys.argv))
    print("Incorrect number of input arguments detected, defaulting to D65 and 100% intensity.\n")
else:
    # We can now process the input arguments
    input_arguments_accepted = True

    if(float(sys.argv[1]) > 1 or float(sys.argv[1]) < 0):
        print("CIE 1931 x-coordinate value incorrect, defaulting to D65 and 100% intensity.\n")
        input_arguments_accepted = False

    if(float(sys.argv[2]) > 1 or float(sys.argv[2]) < 0):
        print("CIE 1931 y-coordinate value incorrect, defaulting to D65 and 100% intensity.\n")
        input_arguments_accepted = False

    if(float(sys.argv[3]) > 100 or float(sys.argv[3]) < 0):
        print("Brightness value is incorrect, defaulting to D65")
        input_arguments_accepted = False

    if(input_arguments_accepted == True):
        cie_x = float(sys.argv[1])
        cie_y = float(sys.argv[2])
        intensity = float(sys.argv[3])


# Check for the client config file:
client_details_file_present = False;
if(os.path.exists("client_details.json")):
    client_details_file_present = True;
    # Load the local client file, validate it. If not valid, get it from the gateway.
    fp = open("client_details.json", "r")
    try:
        client_file_as_json = json.load(fp)
        fp.close()
    except:
        print("\nWarning: Unable to parse the client details file. Overwriting.")
        client_details_file_present = False;


# We need to generate the client file.
if( not client_details_file_present):
    we_wait_for_link_button = True
    initial_request_url = "https://" + local_ip + "/api"
    initial_request_json_object = {"devicetype" : "app_name#instance_name", "generateclientkey" : True}

    while(we_wait_for_link_button):
        # The certificate is self-signed, and this will fail by default.
        try:
            initial_response = requests.post(initial_request_url, json = initial_request_json_object, verify = False)
        except requests.ConnectionError:
            # If we got here, the connection wasn't successful. The Hue gateway should be on the local network.
            print("Error: the Hue gateway at the specified IP address did not respond in time.\n\t-Is it connected?\n\t-Is it on?\n\t-Can you ping it from this computer?\n")
            quit() # Nothing else to do.

        # If everything went well, then the gateway will respond this initially:
        # [{"error":{"type":101,"address":"","description":"link button not pressed"}}]
        if(initial_response.text == '[{"error":{"type":101,"address":"","description":"link button not pressed"}}]'):
            # I am lazy :D
            input('Press the link button in on the gateway, and then press ENTER in the terminal to continue.\n')
            we_wait_for_link_button = True # so I would remember what we are setting here.
        else:
            we_wait_for_link_button = False

    # If we got here, we have a valid response from the Hue gateway, and we need to save this to a file.
    initial_response_as_json = json.loads(initial_response.text)
    fp = open("client_details.json", "w")
    fp.write(json.dumps(initial_response_as_json, indent = 4, separators=(",", ": "))) # Save the converted string to a file
    fp.close()
    # Populate this so we can get what we want out later-on.
    client_file_as_json = initial_response_as_json

# Get these out form the json object. First dimension is singleton in this case.
client_username = client_file_as_json[0]["success"]["username"]
client_key = client_file_as_json[0]["success"]["clientkey"]

# Every command needs at least the username, and every subsequent request can be appended to this.
http_headers = { "hue-application-key" : client_username }

# Check what lights have we got.
device_list_request_url = "https://" + local_ip + "/clip/v2/resource/light"
try:
    my_lights_response = requests.get(device_list_request_url, headers = http_headers, verify = False)
except:
    print(my_lights_response.reason + "\n")
    print("Error: Device list could not be requested from the Hue gateway. This should never happen.\n\tIs it working at all with the Hue app?\n")
    quit()

# If we got here, then we have a valid response for the lights. Save these.
my_lights_response_as_json = json.loads(my_lights_response.text)
fp = open("my_lights.json", "w")
fp.write(json.dumps(my_lights_response_as_json, indent = 4, separators = (",", ": ")))
fp.close()


# Now we find the light IDs, and save them to a string array.
no_of_lights = len(my_lights_response_as_json["data"]) # See my_lights.json, "data" field
light_ids = [None] * no_of_lights # empty array, preinitialised

for light_address in range(0, no_of_lights):
    # json creates the addresses as such: my_lights_response_as_json["data"][<lamp sequential number>]["id"]
    #light_ids[light_address] = my_lights_response_as_json["data"][light_address]["owner"]["rid"]
    light_ids[light_address] = my_lights_response_as_json["data"][light_address]["id"]


# For each light, set the intensity and chromaticity values. These are the same, so we can assemble the control command manually.

light_control_properties = {
     "on": { "on": True },
     "dimming": { "brightness": intensity },
     "color":   {"xy":  {
                            "x": cie_x,
                            "y": cie_y
                        }
                },
    "powerup": {"preset": "custom",
                "mode": "color",
                "xy":   {
                            "x": cie_x,
                            "y": cie_y
                        }
                }
}

for light_id in range(0, no_of_lights):
    try:
        # assemble the URL form the light ID
        device_url = device_list_request_url + "/" + light_ids[light_id]
        #print(device_url)
        chroma_set_response = requests.put(device_list_request_url + "/" + light_ids[light_id], headers = http_headers, data = json.dumps(light_control_properties), verify = False)

    except:
        print(chroma_set_response.reason + "\n")
        print("Error: Device list could not be requested from the Hue gateway. This should never happen.\n\tIs it working at all with the Hue app?\n")
        quit()
    # Super dirty thing: When it works, we can see that it's OK, because it's a light. But, when something is wrong, all we see that it's not working
    # The simplest way is to check the length of the reponse. The IDs will be different, but the lengths will be not. I am getting 87 byte long responses. So:

    if(len(chroma_set_response.text) > 88 ):
        print("Abnormal response detected from the gateway:\n")
        print(chroma_set_response.text)
        quit()

    time.sleep(0.05)
