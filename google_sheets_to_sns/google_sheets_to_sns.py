print('Loading function');
# from oauth2client.client import OAuth2Credentials
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import gspread
import boto3

def lambda_handler(event, context):
    print('loading handler')
    # Set sheet name and get the meds from it
    sheet_name = "Medication Tracking"
    meds_worksheet = 'Medication Input'
    meds_dashboard_worksheet = 'Medication Dashboard'

    topicArn = "<sns_topic_arn>"

    meds = get_med_times_from_sheet(sheet_name, meds_worksheet, meds_dashboard_worksheet)

    # Calculate which meds should be given based on current time
    meds_to_give = find_expired_meds(meds)

    if not meds_to_give:
        message =  "No meds scheduled within the next hour."
        print message
        # sns_publish(message, topicArn)
    else:
        message = "%s These meds can now be given (within an hour of the next dose): %s" % (subtract_hour(datetime.now().time(), 5).strftime("%I:%M%p"), meds_to_give)
        print message
        sns_publish(message, topicArn)
    return

def get_med_times_from_sheet(sheet_name, meds_ws, meds_dashboard_ws):
    # build creds and auth to google
    scope = ['https://spreadsheets.google.com/feeds']
    json = {
      "type": "service_account",
      "project_id": "",
      "private_key_id": "",
      "private_key": "",
      "client_email": "",
      "client_id": "",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://accounts.google.com/o/oauth2/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": ""
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json, scope)
    gc = gspread.authorize(credentials)

    # Open sheet and meds worksheet
    sh = gc.open(sheet_name)
    ws_meds = sh.worksheet(meds_ws)

    # Get all meds from the Medication List
    meds_start = ws_meds.find('Medication List')
    meds_start_row = meds_start.row
    meds_start_col = meds_start.col
    meds_current = meds_start

    meds_names = []
    # print meds_start
    while meds_current.value is not "":
        if ws_meds.cell(meds_current.row, meds_current.col + 4).value == 'yes':
            print "Medication %s is active" % meds_current.value
            meds_names.append(meds_current.value)
        # else:
        #     print "%s is not an active medicaiton" % meds_current.value
        meds_current = ws_meds.cell(meds_current.row +1, meds_current.col)

    # print meds_names

    # make a dictionary of meds and the next time they should be given
    ws_med_timing = sh.worksheet(meds_dashboard_ws)
    meds_to_give = {}

    for k in meds_names:
        # print k
        med_cell = ws_med_timing.find(k)
        med_cell_timing_row = med_cell.row + 2
        med_cell_timing_col = med_cell.col + 1
        timing = ws_med_timing.cell(med_cell_timing_row,med_cell_timing_col).value
        # print timing
        meds_to_give[k] = datetime.strptime(timing, "%H:%M").time()

    print meds_to_give
    return meds_to_give

def find_expired_meds(meds):
    # checks all meds against the current time
    # returns array of meds to give
    meds_to_give = ''
    for k,v in meds.iteritems():
        # print k,v
        past_bound = subtract_hour(datetime.now().time(), 6)
        future_bound = subtract_hour(datetime.now().time(), 4)
        if ((future_bound > v) & (past_bound < v)):
            meds_to_give = meds_to_give + "\n" + k
        else:
            print "%s can not be given yet" % k
    return meds_to_give

def subtract_hour(tm, hour):
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate - timedelta(hours=hour)
    # print "Subtracting %s hour to current time. \n Full date: %s" % (hour, fulldate)
    return fulldate.time()

def add_hour(tm, hour):
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + timedelta(hours=hour)
    # print "Adding %s hour to current time. \n Full date: %s" % (hour, fulldate)
    return fulldate.time()

def sns_publish(message, topicArn):
    sns = boto3.client(service_name="sns")
    sns.publish(
        TopicArn = topicArn,
        Message = message
    )

# Uncomment the line below for testing locally
# lambda_handler('test', 'context')
