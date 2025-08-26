from typing import List, Dict

class LocationManager:
    """Manages location mapping and variants for different job platforms"""
    
    def __init__(self):
        self.polish_cities = {
            "warsaw": {
                "en": "Warsaw",
                "pl": "Warszawa",
                "glassdoor_id": "3089098",
                "region": "Mazowieckie"
            },
            "krakow": {
                "en": "Krakow", 
                "pl": "Kraków",
                "glassdoor_id": "3089171",
                "region": "Małopolskie"
            },
            "wroclaw": {
                "en": "Wroclaw",
                "pl": "Wrocław",
                "glassdoor_id": "3089235",
                "region": "Dolnośląskie"
            },
            "poznan": {
                "en": "Poznan",
                "pl": "Poznań", 
                "glassdoor_id": "3089197",
                "region": "Wielkopolskie"
            },
            "gdansk": {
                "en": "Gdansk",
                "pl": "Gdańsk",
                "glassdoor_id": "3089093",
                "region": "Pomorskie"
            },
            "lodz": {
                "en": "Lodz",
                "pl": "Łódź",
                "glassdoor_id": "3089181",
                "region": "Łódzkie"
            },
            "katowice": {
                "en": "Katowice",
                "pl": "Katowice",
                "glassdoor_id": "3089154",
                "region": "Śląskie"
            },
            "szczecin": {
                "en": "Szczecin",
                "pl": "Szczecin",
                "glassdoor_id": "3089219",
                "region": "Zachodniopomorskie"
            },
            "lublin": {
                "en": "Lublin",
                "pl": "Lublin",
                "glassdoor_id": "3089175",
                "region": "Lubelskie"
            },
            "bydgoszcz": {
                "en": "Bydgoszcz",
                "pl": "Bydgoszcz",
                "glassdoor_id": "3089054",
                "region": "Kujawsko-pomorskie"
            }
        }
    
    def get_search_locations(self, location: str, include_remote: bool = True) -> List[str]:
        """Get list of locations to search based on input"""
        location_lower = location.lower().strip()
        
        if location_lower == "poland":
            # Search all major cities
            locations = [city["en"] + ", Poland" for city in self.polish_cities.values()]
            locations.append("Poland")
            
            if include_remote:
                locations.extend(["Remote Poland", "Poland Remote"])
            
            return locations
        
        elif location_lower in self.polish_cities:
            # Search specific city
            city_data = self.polish_cities[location_lower]
            locations = [
                f"{city_data['en']}, Poland",
                city_data["pl"]
            ]
            
            if include_remote:
                locations.append(f"Remote {city_data['en']}")
            
            return locations
        
        else:
            # Use location as provided
            locations = [location]
            if include_remote and "remote" not in location.lower():
                locations.append(f"Remote {location}")
            
            return locations
    
    def get_glassdoor_id(self, location: str) -> str:
        """Get Glassdoor location ID for a city"""
        location_lower = location.lower().replace(", poland", "").strip()
        
        if location_lower in self.polish_cities:
            return self.polish_cities[location_lower]["glassdoor_id"]
        
        # Default to Poland
        return "2616"
    
    def get_pracuj_location(self, location: str) -> str:
        """Get Pracuj.pl location format"""
        location_lower = location.lower().replace(", poland", "").strip()
        
        if location_lower == "poland":
            return ""  # Empty = all Poland
        elif location_lower in self.polish_cities:
            return self.polish_cities[location_lower]["pl"].lower()
        
        return location_lower
    
    def get_supported_locations(self) -> List[str]:
        """Get list of all supported location names"""
        locations = ["Poland"]
        locations.extend([city["en"] for city in self.polish_cities.values()])
        return sorted(locations)
    
    def format_location_display(self, location: str) -> str:
        """Format location for display purposes"""
        location_lower = location.lower()
        
        if location_lower == "poland":
            return "🇵🇱 All of Poland"
        elif location_lower in self.polish_cities:
            city_data = self.polish_cities[location_lower]
            return f"🏙️ {city_data['en']} ({city_data['region']})"
        
        return f"📍 {location}"