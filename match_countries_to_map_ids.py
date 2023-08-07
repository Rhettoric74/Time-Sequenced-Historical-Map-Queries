from coordinate_geometry import *
from geo_entity import GeoEntity
import json
import os

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
        # first try querying specifically for administrative feature of the country,
        # if that entry causes problems (i.e. has no coordinates), find other fclasses
        try:
            countries.append(GeoEntity(country, ["A"]))
        except:
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
             
            if overlaps_with_map_bbox(bounds, country.largest_bounding) or overlaps_with_map_bbox(country.largest_bounding, bounds):
                if country.name in countries_to_map_ids:
                    countries_to_map_ids[country.name].append(file.strip(".geojson"))
                else:
                    countries_to_map_ids[country.name] = [file.strip(".geojson")]
        files_searched += 1
        if files_searched % 100 == 0:
            print(files_searched)
    return countries_to_map_ids
global countries_to_ids_dict
with open("countries_to_map_ids.json") as fp:
    countries_to_ids_dict = json.load(fp)
if __name__ == "__main__":
    """ countries = "Afghanistan, Albania, Algeria, Andorra, Angola, Antigua and Barbuda, Argentina, Armenia, Australia, Austria, Azerbaijan, Bahamas, Bahrain, Bangladesh, Barbados, Belarus, Belgium, Belize, Benin, Bhutan, Bolivia, Bosnia and Herzegovina, Botswana, Brazil, Brunei, Bulgaria, Burkina Faso, Burundi, Côte d'Ivoire, Cabo Verde, Cambodia, Cameroon, Canada, Central African Republic, Chad, Chile, China, Colombia, Comoros, Republic of the Congo, Costa Rica, Croatia, Cuba, Cyprus, Czech Republic, Democratic Republic of the Congo, Denmark, Djibouti, Dominica, Dominican Republic, Ecuador, Egypt, El Salvador, Equatorial Guinea, Eritrea, Estonia, Swaziland, Ethiopia, Fiji, Finland, France, Gabon, Gambia, Georgia, Germany, Ghana, Greece, Grenada, Guatemala, Guinea, Guinea-Bissau, Guyana, Haiti, Holy See, Honduras, Hungary, Iceland, India, Indonesia, Iran, Iraq, Ireland, Israel, Italy, Jamaica, Japan, Jordan, Kazakhstan, Kenya, Kiribati, Kuwait, Kyrgyzstan, Laos, Latvia, Lebanon, Lesotho, Liberia, Libya, Liechtenstein, Lithuania, Luxembourg, Madagascar, Malawi, Malaysia, Maldives, Mali, Malta, Marshall Islands, Mauritania, Mauritius, Mexico, Micronesia, Moldova, Monaco, Mongolia, Montenegro, Morocco, Mozambique, Myanmar, Namibia, Nauru, Nepal, Netherlands, New Zealand, Nicaragua, Niger, Nigeria, North Korea, Macedonia, Norway, Oman, Pakistan, Palau, Panama, Papua New Guinea, Paraguay, Peru, Philippines, Poland, Portugal, Qatar, Romania, Russia, Rwanda, Saint Kitts and Nevis, Saint Lucia, Saint Vincent and the Grenadines, Samoa, San Marino, Sao Tome and Principe, Saudi Arabia, Senegal, Serbia, Seychelles, Sierra Leone, Singapore, Slovakia, Slovenia, Solomon Islands, Somalia, South Africa, South Korea, South Sudan, Spain, Sri Lanka, Sudan, Suriname, Sweden, Switzerland, Syria, Tajikistan, Tanzania, Thailand, Timor-Leste, Togo, Tonga, Trinidad and Tobago, Tunisia, Turkey, Turkmenistan, Tuvalu, Uganda, Ukraine, United Arab Emirates, United Kingdom, United States of America, Uruguay, Uzbekistan, Vanuatu, Venezuela, Vietnam, Yemen, Zambia, Zimbabwe".split(", ")

    #not_found_countries = [country for country in countries if country not in countries_to_ids_dict]
    #print(not_found_countries)
    countries_to_ids_dict = (match_countries_to_map_ids(countries, "geojson_testr_syn"))
    print(countries_to_ids_dict)
    with open("countries_to_map_ids.json", "w") as fp:
        json.dump(countries_to_ids_dict, fp) """
    import csv

    # Input CSV file path and name
    input_file = "luna_omo_metadata_56628_20220724.csv"

    # Output CSV file path and name
    output_file = "countries_added_luno_omo_metadata.csv"

    # match maps with the countries they contain
    map_ids_to_countries = {}
    for country in countries_to_ids_dict:
        ids_list = countries_to_ids_dict[country]
        for id in ids_list:
            if id in map_ids_to_countries:
                map_ids_to_countries[id].append(country)
            else:
                map_ids_to_countries[id] = [country]

    # Read the existing CSV file
    with open(input_file, 'r', errors="ignore") as csv_in, open(output_file, 'w', errors="ignore", newline="") as csv_out:
        reader = csv.DictReader(csv_in)
        # Get the header from the original file
        header = reader.fieldnames

        # Add the new column header to the header list
        header.append("countriesWithinBounds")
        writer = csv.DictWriter(csv_out, header)
        # Write the updated header to the output CSV file
        writer.writeheader()

        # Iterate through each row and add the new column data
        for row in reader:
            if row["filename"] in map_ids_to_countries:
                row["countriesWithinBounds"] = map_ids_to_countries[row["filename"]]
            writer.writerow(row)

