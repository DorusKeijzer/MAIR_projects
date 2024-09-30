# restaurant_lookup.py

import pandas as pd
import os
import random
from assignment_1c.reasoner import InferenceEngine, Literal, rules


class RestaurantLookup:
    def __init__(self, csv_path=None):
        if csv_path is None:
            csv_path = os.path.join("MAIR_projects", "data", "restaurant_info_extended.csv")
        self.restaurant_data = pd.read_csv(csv_path)
        self.inference_engine = InferenceEngine(rules)

    def get_candidates(self, preferences: dict):
        # Filter restaurants based on user preferences
        filtered_data = self.restaurant_data.copy()
        filtered_data = self._filter_by_price(filtered_data, preferences.get('price_range'))
        print(f"Total restaurants after price filter: {len(filtered_data)}")
        filtered_data = self._filter_by_location(filtered_data, preferences.get('location'))
        print(f"Total restaurants after location filter: {len(filtered_data)}")
        filtered_data = self._filter_by_food_type(filtered_data, preferences.get('food_type'))
        print(f"Total restaurants after food type filter: {len(filtered_data)}")

        if filtered_data.empty:
            return pd.DataFrame()  # Return empty DataFrame if no candidates found

        return filtered_data

    def apply_inference_and_select(self, candidates: pd.DataFrame, additional_requirements: dict):
        if candidates.empty:
            return "No matching restaurants found"

        matching_restaurants = []
        for _, restaurant in candidates.iterrows():
            # Create literals for known properties
            known_properties = [
                Literal('pricerange', restaurant['pricerange']),
                Literal('food_quality', restaurant['food_quality']),
                Literal('food', restaurant['food']),
                Literal('crowdedness', restaurant['crowdedness']),
                Literal('length_of_stay', restaurant['length_of_stay']),
            ]

            # Apply inference engine and unpack the results
            inferred, explanations = self.inference_engine.inference(known_properties)

            # Debug statements
            print(f"Restaurant: {restaurant['restaurantname']}")
            print(f"Inferred: {inferred}")
            print(f"Explanations: {explanations}")

            # Check if restaurant meets additional requirements
            meets_requirements = True
            for req_property, req_value in additional_requirements.items():
                inferred_value = inferred.get(req_property)
                if inferred_value == 'contradictory' or inferred_value != req_value:
                    meets_requirements = False
                    break

            if meets_requirements:
                # Store both inferred facts and explanations
                restaurant['inferred'] = inferred
                restaurant['explanations'] = explanations
                matching_restaurants.append(restaurant)
        print(f"Number of matching restaurants: {len(matching_restaurants)}")

        if not matching_restaurants:
            return "No matching restaurants found with your additional requirements"

        # Randomly select a restaurant from the matching ones
        selected_restaurant = random.choice(matching_restaurants)
        return {
            'restaurant': selected_restaurant,
            'inferred': selected_restaurant['inferred'],
            'explanations': selected_restaurant['explanations']
        }


    def generate_reasoning(self, selected_restaurant_data: dict, additional_requirements: dict) -> str:
        reasoning = ""
        inferred_props = selected_restaurant_data.get('inferred', {})
        explanations = selected_restaurant_data.get('explanations', {})
        for req in additional_requirements:
            if req in inferred_props:
                value = inferred_props[req]
                if value == 'contradictory':
                    reasoning += f"The property '{req}' has contradictory inferences.\n"
                elif value is True:
                    explanation = explanations.get(req, f"The restaurant is {req} based on our inference rules.")
                    reasoning += explanation + "\n"
                elif value is False:
                    reasoning += f"The restaurant is not {req} based on our inference rules.\n"
        return reasoning.strip()

    # Filtering methods
    def _filter_by_price(self, data: pd.DataFrame, price_range: str) -> pd.DataFrame:
        if price_range and price_range.lower() != 'any':
            return data[data['pricerange'].str.lower().str.contains(price_range.lower(), na=False)]
        return data

    def _filter_by_location(self, data: pd.DataFrame, location: str) -> pd.DataFrame:
        if location and location.lower() != 'any':
            return data[data['area'].str.lower().str.contains(location.lower(), na=False)]
        return data

    def _filter_by_food_type(self, data: pd.DataFrame, food_type: str) -> pd.DataFrame:
        if food_type and food_type.lower() != 'any':
            food_types = food_type.split('|') if '|' in food_type else [food_type]
            pattern = '|'.join(food_types)
            return data[data['food'].str.lower().str.contains(pattern, na=False)]
        return data
