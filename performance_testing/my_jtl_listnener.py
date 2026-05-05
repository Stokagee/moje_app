from locust import events
import time
import requests
import os

jtl_file = None
jtl_filename = None

# JTL Reporter konfigurace
JTL_REPORTER_URL = os.environ.get("JTL_REPORTER_URL", "http://localhost:5000")
JTL_API_TOKEN = os.environ.get("JTL_API_TOKEN", "at-00632fb9-8b18-43d1-ab79-63a015d8df56")
JTL_PROJECT = os.environ.get("JTL_PROJECT", "Test_project")
JTL_SCENARIO = os.environ.get("JTL_SCENARIO", "test #1")
JTL_ENVIRONMENT = os.environ.get("JTL_ENVIRONMENT", "test")

@events.test_start.add_listener
def on_test_start(**kwargs):
    global jtl_file, jtl_filename
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    jtl_filename = f"locust_test_{timestamp}.jtl"
    jtl_file = open(jtl_filename, "w")
    # JMeter formát pro JTL Reporter
    jtl_file.write("timeStamp,elapsed,label,responseCode,responseMessage,dataType,success,bytes,sentBytes,grpThreads,allThreads,Latency,IdleTime,Connect,Hostname,failureMessage\n")
    print("Test začíná!")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    global jtl_file
    ts = int(time.time() * 1000)
    elapsed = str(int(response_time))
    label = name
    response_code = kwargs.get("response", None)
    response_code_str = str(response_code.status_code) if response_code else "0"
    response_message = response_code.reason if response_code and hasattr(response_code, "reason") else ""
    data_type = "unknown"
    success = "false" if exception else "true"
    bytes_received = str(response_length)
    bytes_sent = "0"
    grp_threads = str(kwargs.get("context", {}).get("user_count", 0)) if kwargs.get("context") else "0"
    all_threads = grp_threads
    latency = "0"
    idle_time = "0"
    connect = "0"
    hostname = "localhost"
    failure_message = str(exception).replace('"', '""') if exception else ""

    line = f'{ts},{elapsed},"{label}",{response_code_str},"{response_message}",{data_type},{success},{bytes_received},{bytes_sent},{grp_threads},{all_threads},{latency},{idle_time},{connect},"{hostname}","{failure_message}"\n'
    jtl_file.write(line)
    jtl_file.flush()

    if exception:
        print(f"Požadavek {request_type} {name} selhal s výjimkou: {exception}")
    else:
        print(f"Požadavek {request_type} {name} trval {response_time} ms a vrátil {response_length} bajtů")

@events.test_stop.add_listener
def on_test_stop(**kwargs):
    global jtl_file, jtl_filename
    if jtl_file:
        jtl_file.close()

    # Automatický upload do JTL Reporter
    if JTL_API_TOKEN and jtl_filename:
        try:
            upload_to_jtl_reporter(jtl_filename)
        except Exception as e:
            print(f"Chyba při uploadu do JTL Reporter: {e}")

    print("Test končí!")

def upload_to_jtl_reporter(filename):
    """Nahraje JTL soubor do JTL Reporter."""
    import urllib.parse
    url = f"{JTL_REPORTER_URL}/api/projects/{JTL_PROJECT}/scenarios/{urllib.parse.quote(JTL_SCENARIO)}/items"

    with open(filename, 'rb') as f:
        files = {
            'kpi': f,
            'environment': (None, JTL_ENVIRONMENT),
            'status': (None, '1')
        }
        headers = {'x-access-token': JTL_API_TOKEN}

        response = requests.post(url, files=files, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ JTL úspěšně nahrán! Item ID: {result.get('itemId')}")
        else:
            print(f"❌ Upload selhal: {response.status_code} - {response.text}")
    
