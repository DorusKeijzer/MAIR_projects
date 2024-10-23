import pandas as pd
import os
import random
from assignment_1c.reasoner import InferenceEngine, Literal, rules


class RestaurantLookup:
    def __init__(self, csv_path=None):
        if csv_path is None:
            csv_path = os.path.join(
                os.getcwd(),"data", "restaurant_info_extended.csv")
        self.restaurant_data = pd.read_csv(csv_path)
        print(f"DEBUG: Loaded {len(self.restaurant_data)} restaurants from CSV")
        self.inference_engine = InferenceEngine(rules)

    def get_candidates(self, preferences: dict):
        print(f"DEBUG: Getting candidates for preferences: {preferences}")
        filtered_data = self.restaurant_data.copy()
        print(f"DEBUG: Total restaurants before filtering: {len(filtered_data)}")
        
        filtered_data = self._filter_by_price(
            filtered_data, preferences.get('price_range'))
        print(f"DEBUG: Restaurants after price filter: {len(filtered_data)}")
        
        filtered_data = self._filter_by_location(
            filtered_data, preferences.get('location'))
        print(f"DEBUG: Restaurants after location filter: {len(filtered_data)}")
        
        filtered_data = self._filter_by_food_type(
            filtered_data, preferences.get('food_type'))
        print(f"DEBUG: Restaurants after food type filter: {len(filtered_data)}")

        if filtered_data.empty:
            return pd.DataFrame()  # Return empty DataFrame if no candidates found

        return filtered_data

    def apply_inference_and_select(self, candidates: pd.DataFrame, additional_requirements: dict):
        print(f"DEBUG: Applying inference and selecting from {len(candidates)} candidates")
        print(f"DEBUG: Additional requirements: {additional_requirements}")

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
            inferred, explanations = self.inference_engine.inference(
                known_properties)
            print(f"DEBUG: Restaurant: {restaurant['restaurantname']}")
            print(f"DEBUG: Inferred properties: {inferred}")

            # Check if restaurant meets additional requirements
            meets_requirements = True
            for req_property, req_value in additional_requirements.items():
                inferred_value = inferred.get(req_property)
                if inferred_value == 'contradictory' or inferred_value != req_value:
                    meets_requirements = False
                    print(f"DEBUG: Restaurant doesn't meet requirement: {req_property}={req_value}")
                    break

            if meets_requirements:
                # Store both inferred facts and explanations
                restaurant['inferred'] = inferred
                restaurant['explanations'] = explanations
                matching_restaurants.append(restaurant)

        print(f"DEBUG: Number of matching restaurants: {len(matching_restaurants)}")

        if not matching_restaurants:
            return "No matching restaurants found with your additional requirements"

        # Randomly select a restaurant from the matching ones
        selected_restaurant = random.choice(matching_restaurants)
        print(f"DEBUG: Selected restaurant: {selected_restaurant['restaurantname']}")
        return {
            'restaurant': selected_restaurant,
            'inferred': selected_restaurant['inferred'],
            'explanations': selected_restaurant['explanations']
        }

    def generate_reasoning(self, selected_restaurant_data: dict, additional_requirements: dict) -> str:
        reasoning = []
        restaurant = selected_restaurant_data['restaurant']
        inferred_props = selected_restaurant_data.get('inferred', {})
        explanations = selected_restaurant_data.get('explanations', {})

        # Add reasoning for primary preferences
        if 'food' in restaurant:
            reasoning.append(f"it offers {restaurant['food']} cuisine")
        if 'area' in restaurant:
            reasoning.append(f"it's located in the {restaurant['area']} area")
        if 'pricerange' in restaurant:
            reasoning.append(f"it has {restaurant['pricerange']} prices")

        # Add reasoning for additional requirements
        for req, value in additional_requirements.items():
            if req in inferred_props:
                if inferred_props[req] == value:
                    explanation = explanations.get(req, f"it is {req}")
                    if req == 'touristic':
                        reasoning.append(f"it's popular among tourists because {explanation.lower()}")
                    elif req == 'romantic':
                        reasoning.append(f"it has a romantic atmosphere because {explanation.lower()}")
                    elif req == 'children':
                        reasoning.append(f"it's suitable for children because {explanation.lower()}")
                    elif req == 'assigned_seats':
                        reasoning.append(f"it has assigned seating because {explanation.lower()}")
                    else:
                        reasoning.append(f"it is {req} because {explanation.lower()}")
                else:
                    reasoning.append(f"however, it might not be {req}")
            else:
                reasoning.append(f"I don't have information about whether it's {req}")

        # Combine reasons
        if len(reasoning) > 1:
            reasoning_str = ", ".join(reasoning[:-1]) + f", and {reasoning[-1]}"
        else:
            reasoning_str = reasoning[0] if reasoning else ""

        return reasoning_str.capitalize() + "."

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
            food_types = food_type.split(
                '|') if '|' in food_type else [food_type]
            pattern = '|'.join(food_types)
            return data[data['food'].str.lower().str.contains(pattern, na=False)]
        return data
