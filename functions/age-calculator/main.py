import functions_framework
import base64
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

@functions_framework.cloud_event
def calculate_age_pubsub(cloud_event):
    """
    Cloud Event Function (Pub/Sub) to calculate age.
    Expects a Pub/Sub message with a JSON body containing 'birth_date' in 'YYYY-MM-DD' format.
    """
    try:
        # Extract and decode Pub/Sub data
        pubsub_data = base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8')
        request_json = json.loads(pubsub_data)
        
        if not request_json or 'birth_date' not in request_json:
            print("Error: Please provide 'birth_date' in YYYY-MM-DD format in the Pub/Sub message.")
            return

        birth_date_str = request_json['birth_date']
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        today = datetime.now()
        
        if birth_date > today:
            print(f"Error: Birth date {birth_date_str} cannot be in the future.")
            return

        # Calculate totals
        diff = today - birth_date
        total_days = diff.days
        total_weeks = total_days // 7
        
        # Calculate years and months using relativedelta
        rdelta = relativedelta(today, birth_date)
        total_years = rdelta.years
        total_months = (rdelta.years * 12) + rdelta.months

        result = {
            "birth_date": birth_date_str,
            "age_summary": {
                "years": total_years,
                "months": total_months,
                "weeks": total_weeks,
                "days": total_days
            },
            "detailed_breakdown": {
                "years": rdelta.years,
                "months": rdelta.months,
                "days": rdelta.days
            }
        }

        print(f"Calculation Successful for {birth_date_str}:")
        print(json.dumps(result, indent=2))

    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        print(f"Error: {str(e)}")
