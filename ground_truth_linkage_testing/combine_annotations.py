import json
import os
all_data = []
with open("img-names-updated_icdar24-test-png-annotations.json", "r") as test_file:
    all_data += json.load(test_file)
with open("icdar24-val-png/annotations.json", "r") as val_file:
    all_data += json.load(val_file)
with open("icdar24-train-png/annotations.json", "r") as train_file:
    all_data += json.load(train_file)
with open("all_annotations.json", "w") as output_file:
    json.dump(all_data, output_file)