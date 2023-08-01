from coordinate_geometry import *
from geo_entity import GeoEntity
import json
import os
import csv

def match_countries_to_map_ids(country_names, map_dir):
    """
    Purpose: Match each country to the ids of maps that overlap with it.
    One map can contain (and be matched with) multiple countries
    Parameters: country_names, a list of countries to match with maps, map_dir, a directory
    containing geojson files of maps to match with countries.
    Returns: A json dictionary mapping each country with a list of map_ids that contain them
    """
    countries_to_map_ids = {}
    countries = []
    for country in country_names:
        try:
            countries.append(GeoEntity(country))
        except:
            print(country, "not found in gazetteer")
    print("countries geocoded")
    files_searched = 0
    for file in os.listdir(map_dir):
        with open(map_dir + "/" + file) as json_file:
            feature_collection = json.load(json_file)
        bounds = estimate_map_bounds(feature_collection)
        for country in countries:
             
            if overlaps_with_map_bbox(bounds, country.largest_bounding):
                if country.name in countries_to_map_ids:
                    countries_to_map_ids[country.name].append(file.strip(".geojson"))
                else:
                    countries_to_map_ids[country.name] = [file.strip(".geojson")]
        files_searched += 1
        if files_searched % 100 == 0:
            print(files_searched)
    return countries_to_map_ids
if __name__ == "__main__":
    countries = "Afghanistan, Albania, Algeria, Andorra, Angola, Antigua and Barbuda, Argentina, Armenia, Australia, Austria, Azerbaijan, Bahamas, Bahrain, Bangladesh, Barbados, Belarus, Belgium, Belize, Benin, Bhutan, Bolivia, Bosnia and Herzegovina, Botswana, Brazil, Brunei, Bulgaria, Burkina Faso, Burundi, Côte d'Ivoire, Cabo Verde, Cambodia, Cameroon, Canada, Central African Republic, Chad, Chile, China, Colombia, Comoros, Republic of the Congo, Costa Rica, Croatia, Cuba, Cyprus, Czech Republic, Democratic Republic of the Congo, Denmark, Djibouti, Dominica, Dominican Republic, Ecuador, Egypt, El Salvador, Equatorial Guinea, Eritrea, Estonia, Swaziland, Ethiopia, Fiji, Finland, France, Gabon, Gambia, Georgia, Germany, Ghana, Greece, Grenada, Guatemala, Guinea, Guinea-Bissau, Guyana, Haiti, Holy See, Honduras, Hungary, Iceland, India, Indonesia, Iran, Iraq, Ireland, Israel, Italy, Jamaica, Japan, Jordan, Kazakhstan, Kenya, Kiribati, Kuwait, Kyrgyzstan, Laos, Latvia, Lebanon, Lesotho, Liberia, Libya, Liechtenstein, Lithuania, Luxembourg, Madagascar, Malawi, Malaysia, Maldives, Mali, Malta, Marshall Islands, Mauritania, Mauritius, Mexico, Micronesia, Moldova, Monaco, Mongolia, Montenegro, Morocco, Mozambique, Myanmar, Namibia, Nauru, Nepal, Netherlands, New Zealand, Nicaragua, Niger, Nigeria, North Korea, Macedonia, Norway, Oman, Pakistan, Palau, Panama, Papua New Guinea, Paraguay, Peru, Philippines, Poland, Portugal, Qatar, Romania, Russia, Rwanda, Saint Kitts and Nevis, Saint Lucia, Saint Vincent and the Grenadines, Samoa, San Marino, Sao Tome and Principe, Saudi Arabia, Senegal, Serbia, Seychelles, Sierra Leone, Singapore, Slovakia, Slovenia, Solomon Islands, Somalia, South Africa, South Korea, South Sudan, Spain, Sri Lanka, Sudan, Suriname, Sweden, Switzerland, Syria, Tajikistan, Tanzania, Thailand, Timor-Leste, Togo, Tonga, Trinidad and Tobago, Tunisia, Turkey, Turkmenistan, Tuvalu, Uganda, Ukraine, United Arab Emirates, United Kingdom, United States of America, Uruguay, Uzbekistan, Vanuatu, Venezuela, Vietnam, Yemen, Zambia, Zimbabwe".split(", ")

    not_found_countries = ["Bahamas", "Vatican City", "Singapore", "United Kingdom"]
    #countries_to_ids_dict = match_countries_to_map_ids(not_found_countries, "geojson_testr_syn")
    #print(countries_to_ids_dict)
    with open("remaining_countries_to_map_ids.json") as remaining_countries:
        with open("countries_to_map_ids.json") as countries:
            remaining_countries_to_ids_dict = json.load(remaining_countries)
            countries_to_ids_dict = json.load(countries)
            countries_to_ids_dict.update(remaining_countries_to_ids_dict)
    with open("countries_to_map_ids.json", "w") as fp:
        json.dump(countries_to_ids_dict, fp)