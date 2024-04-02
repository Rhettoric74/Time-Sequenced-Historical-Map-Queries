import os
import json

corrupted_files = []
total_files = os.listdir("rumsey_57k_english")
progress_counter = 0
for file in total_files:
    progress_counter += 1
    if progress_counter % 100 == 0:
        print(progress_counter)
    try:
        with open("rumsey_57k_english/" + file, "r", encoding="utf-8") as f:
            json.load(f)
    except:
        corrupted_files.append(file)
print(len(corrupted_files))
print(corrupted_files)
print((len(total_files) - len(corrupted_files)) / len(total_files))