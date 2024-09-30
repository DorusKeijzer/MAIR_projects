# add_new_properties.py
import pandas as pd
import random
import os

def add_new_properties(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    # Possible values for the new properties
    food_quality_options = ['good', 'bad']
    crowdedness_options = ['busy', 'not busy']
    length_of_stay_options = ['long', 'short']

    # Assign random values to each restaurant
    df['food_quality'] = [random.choice(food_quality_options) for _ in range(len(df))]
    df['crowdedness'] = [random.choice(crowdedness_options) for _ in range(len(df))]
    df['length_of_stay'] = [random.choice(length_of_stay_options) for _ in range(len(df))]

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv, index=False)
    print(f"New properties added to {output_csv}")

if __name__ == '__main__':
    input_csv = os.path.join("MAIR_projects/assignment_1b/data/restaurant_info.csv")
    output_csv = os.path.join("MAIR_projects/data/restaurant_info_extended.csv")
    add_new_properties(input_csv, output_csv)
