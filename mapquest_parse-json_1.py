import urllib.parse
import requests
import json

# Base URL for the MapQuest Directions API
main_api = "https://www.mapquestapi.com/directions/v2/route?"
key = "jdp5PLCiwuoYvff4PgVX583eK4SvGj2b"  # MapQuest API key

# Fuel price per liter (adjust as needed)
fuel_price_per_liter = 1.50  # Example price in user's currency

# Weather API configuration
weather_api = "http://api.openweathermap.org/data/2.5/weather?"
weather_key = "838ee807094594ec2cbc2a03b60e7beb"  

# Unit selection (user can switch between 'metric' and 'imperial')
units = input("Choose units (metric/imperial): ").strip().lower()
if units not in ["metric", "imperial"]:
    print("Invalid choice, defaulting to metric.")
    units = "metric"

while True:
    orig = input("Starting Location: ")
    if orig.lower() in ["quit", "q"]:
        break
    dest = input("Destination: ")
    if dest.lower() in ["quit", "q"]:
        break
    
    # Construct the API request URL
    url = main_api + urllib.parse.urlencode({"key": key, "from": orig, "to": dest, "routeType": "fastest", "alternates": "true"})
    print("URL:", url)
    
    # Send request and parse JSON response
    json_data = requests.get(url).json()
    json_status = json_data["info"]["statuscode"]
    
    if json_status == 0:
        # Output header information
        print("API Status:", json_status, "= A successful route call.\n")
        print("=============================================")
        print("Directions from", orig, "to", dest)
        
        # Loop through alternative routes if available
        for route_index, route in enumerate(json_data.get("route", {}).get("alternateRoutes", [json_data["route"]]), start=1):
            print(f"\nOption {route_index} - Route Summary:")
            print("Trip Duration:", route["formattedTime"])
            
            # Distance and fuel consumption
            distance = route["distance"]
            fuel_used = route.get("fuelUsed", None)
            if units == "metric":
                distance_km = distance * 1.61
                print("Kilometers:", "{:.2f}".format(distance_km))
                if fuel_used is not None:
                    fuel_liters = fuel_used * 3.78
                    print("Fuel Used (Ltr):", "{:.2f}".format(fuel_liters))
                    estimated_cost = fuel_liters * fuel_price_per_liter
                    print("Estimated Fuel Cost:", "{:.2f}".format(estimated_cost))
            else:
                print("Miles:", "{:.2f}".format(distance))
                if fuel_used is not None:
                    print("Fuel Used (Gal):", "{:.2f}".format(fuel_used))
                    estimated_cost = fuel_used * fuel_price_per_liter / 3.78
                    print("Estimated Fuel Cost:", "{:.2f}".format(estimated_cost))
            
            # Traffic delay information
            traffic_delay = route.get("realTime", None)
            if traffic_delay:
                print("Traffic Delay:", f"{traffic_delay // 60} minutes")
            print("=============================================\n")

            # Display each maneuver in the route
            print("Directions:")
            for each in route["legs"][0]["maneuvers"]:
                distance_maneuver = each["distance"]
                if units == "metric":
                    distance_maneuver *= 1.61
                    print(each["narrative"], "(", "{:.2f}".format(distance_maneuver), "km)")
                else:
                    print(each["narrative"], "(", "{:.2f}".format(distance_maneuver), "mi)")
            print("=============================================\n")

        # Get current weather at destination
        weather_url = weather_api + urllib.parse.urlencode({"q": dest, "appid": weather_key, "units": "metric" if units == "metric" else "imperial"})
        weather_data = requests.get(weather_url).json()
        if weather_data.get("cod") == 200:
            print("Current Weather at Destination:")
            print(f"Temperature: {weather_data['main']['temp']}°{'C' if units == 'metric' else 'F'}")
            print("Weather:", weather_data["weather"][0]["description"])
            print("Humidity:", weather_data["main"]["humidity"], "%")
            print("=============================================\n")
        else:
            print("Weather information could not be retrieved.")
        
        # Save route information to file if user wants
        save_option = input("Would you like to save the route details? (yes/no): ").strip().lower()
        if save_option == "yes":
            filename = f"route_from_{orig.replace(' ', '_')}_to_{dest.replace(' ', '_')}.txt"
            with open(filename, "w") as file:
                file.write(f"Directions from {orig} to {dest}\n")
                file.write("=============================================\n")
                for route_index, route in enumerate(json_data.get("route", {}).get("alternateRoutes", [json_data["route"]]), start=1):
                    file.write(f"\nOption {route_index} - Route Summary:\n")
                    file.write(f"Trip Duration: {route['formattedTime']}\n")
                    file.write(f"Distance: {'{:.2f}'.format(route['distance'] * 1.61) if units == 'metric' else '{:.2f}'.format(route['distance'])} {'km' if units == 'metric' else 'mi'}\n")
                    if fuel_used is not None:
                        file.write(f"Fuel Used: {'{:.2f}'.format(route['fuelUsed'] * 3.78) if units == 'metric' else '{:.2f}'.format(route['fuelUsed'])} {'Ltr' if units == 'metric' else 'Gal'}\n")
                    if traffic_delay:
                        file.write(f"Traffic Delay: {traffic_delay // 60} minutes\n")
                    file.write("Directions:\n")
                    for each in route["legs"][0]["maneuvers"]:
                        distance_maneuver = each["distance"]
                        distance_str = "{:.2f}".format(distance_maneuver * 1.61 if units == "metric" else distance_maneuver)
                        file.write(f"{each['narrative']} ({distance_str} {'km' if units == 'metric' else 'mi'})\n")
                file.write("=============================================\n")
            print(f"Route details saved to {filename}")
        print("=============================================\n")
    
    elif json_status == 402:
        print("**********************************************")
        print("Status Code:", json_status, "; Invalid user inputs for one or both locations.")
        print("**********************************************\n")
    
    elif json_status == 611:
        print("**********************************************")
        print("Status Code:", json_status, "; Missing an entry for one or both locations.")
        print("**********************************************\n")
    
    else:
        print("************************************************************************")
        print("For Status Code:", json_status, "; Refer to:")
        print("https://developer.mapquest.com/documentation/directions-api/status-codes")
        print("************************************************************************\n")
