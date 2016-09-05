# Google Sheets to AWS SNS

This is a lambda function to pull from a Google Sheets spreadsheet, compare some times in cells, and then send any that match to AWS SNS.

Specifically built for querying a medication tracking system and sending the needed medications to caregivers over SMS.

It is made to be used with this Data tracking/input Google Sheet:

For information on the complete system, checkout this blog post:

# Modifications

1) Obtain oauth2 credentials to the Google Sheets API

http://gspread.readthedocs.io/en/latest/oauth2.html

2) Copy the service account JSON you are given to the `json = {}` block on line 34

3) Replace the following on line 11 with the names from the sheet you are working with.
I have made them the default for the public sheet linked above.

```
sheet_name = "<sheet_name>"
meds_worksheet = '<meds_worksheet_name>'
meds_dashboard_worksheet = '<dashboard_worksheet_name>'
```

4) Replace `topicArn` on line 15 with the ARN of your SNS topic from the AWS SNS Console.

5) Run `./deploy` to create the AWS Lambda deployment zip file.

6) Upload to AWS Lambda and run. Make sure your lambda function has publish permissions to your SNS topic.
