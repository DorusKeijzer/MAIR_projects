import pandas as pd
import os
import random


class RestaurantLookup:
    """
    Class to handle restaurant lookups based on user preferences.
    It loads the restaurant data and filters it based on price range, location, and food type.
    """

    def __init__(self, csv_path=None):
        """
        Initializes the class by loading the restaurant data from a CSV file.

        :param csv_path: The path to the restaurant CSV data file. If None, uses the default path.
        """
        # Load CSV file
        if csv_path is None:
            csv_path = os.path.join(
                'assignment_1b', 'data', 'restaurant_info.csv')
        self.restaurant_data = pd.read_csv(csv_path)

    def lookup(self, preferences: dict):
        """
        Looks up restaurants in the CSV data based on the user's extracted preferences.

        :param preferences: Dictionary containing 'price_range', 'location', and 'food_type' preferences.
        :return: A single restaurant based on the best match or a message if no match is found.
        """
        filtered_data = self.restaurant_data.copy()
        # Apply filters based on the preferences
        filtered_data = self._filter_by_price(
            filtered_data, preferences.get('price_range'))
        filtered_data = self._filter_by_location(
            filtered_data, preferences.get('location'))
        filtered_data = self._filter_by_food_type(
            filtered_data, preferences.get('food_type'))

        # If no matches, return a message
        if filtered_data.empty:
            return "No matching restaurants found"

        # Score the restaurants and select the best one
        scored_restaurants = self._score_restaurants(
            filtered_data, preferences)
        selected_restaurant, _ = self._select_best_restaurant(
            scored_restaurants)

        return selected_restaurant

    def _filter_by_price(self, data: pd.DataFrame, price_range: str) -> pd.DataFrame:
        """
        Filters the restaurant data by price range.

        :param data: The DataFrame containing restaurant data.
        :param price_range: The desired price range ('cheap', 'moderate', 'expensive') or 'unknown'.
        :return: The filtered DataFrame.
        """
        if price_range and price_range:
            return data[data['pricerange'].str.lower() == price_range.lower()]
        return data

    def _filter_by_location(self, data: pd.DataFrame, location: str) -> pd.DataFrame:
        """
        Filters the restaurant data by location.

        :param data: The DataFrame containing restaurant data.
        :param location: The desired location ('north', 'south', 'center', etc.) or 'unknown'.
        :return: The filtered DataFrame.
        """
        if location and location:
            return data[data['area'].str.lower() == location.lower()]
        return data

    def _filter_by_food_type(self, data: pd.DataFrame, food_type: str) -> pd.DataFrame:
        """
        Filters the restaurant data by food type.

        :param data: The DataFrame containing restaurant data.
        :param food_type: The desired food type or 'unknown'. Supports broader food categories.
        :return: The filtered DataFrame.
        """
        if food_type and food_type:
            # Check if the food_type contains multiple cuisines (e.g., 'fusion|international')
            food_types = food_type.split(
                '|') if '|' in food_type else [food_type]
            return data[data['food'].str.lower().str.contains('|'.join(food_types), na=False)]
        return data

    def _score_restaurants(self, restaurants: pd.DataFrame, preferences: dict):
        """
        Scores the restaurants based on how many preferences they match.

        :param restaurants: DataFrame containing restaurant matches.
        :param preferences: Dictionary containing 'price_range', 'location', and 'food_type' preferences.
        :return: List of tuples (restaurant_row, score), where score indicates how many preferences were matched.
        """
        scored_restaurants = []

        for idx, restaurant in restaurants.iterrows():
            score = 0

            # Check how many preferences are matched
            if restaurant['pricerange'].lower() == preferences['price_range'].lower():
                score += 1
            if restaurant['area'].lower() == preferences['location'].lower():
                score += 1
            if preferences['food_type'].lower() in restaurant['food'].lower():
                score += 1

            # Store the restaurant and its score
            scored_restaurants.append((restaurant, score))

        return scored_restaurants

    def _select_best_restaurant(self, scored_restaurants):
        """
        Selects the restaurant with the highest score. If there are multiple restaurants
        with the same highest score, one is chosen randomly.

        :param scored_restaurants: List of tuples (restaurant_row, score).
        :return: The selected restaurant and the list of remaining restaurants.
        """
        # Find the highest score
        max_score = max(scored_restaurants, key=lambda x: x[1])[1]
        # Filter restaurants with the highest score
        best_matches = [restaurant for restaurant,
                        score in scored_restaurants if score == max_score]

        # Pick one at random if there are multiple best matches
        selected_restaurant = random.choice(best_matches) if len(
            best_matches) > 1 else best_matches[0]

        # Store the remaining restaurants for future suggestions
        remaining_restaurants = [restaurant for restaurant,
                                 score in scored_restaurants if restaurant is not selected_restaurant]

        return selected_restaurant[0], remaining_restaurants

    def test_lookup(self):
        """
        Runs a test lookup using predefined preferences.
        """
        example_preferences = {
            'price_range': 'moderate',
            'location': 'west',
            'food_type': 'british'
        }

        # Perform the lookup based on example preferences
        print(f"Preferences: {example_preferences}")
        matched_restaurants = self.lookup(example_preferences)
        print(f"Matched Restaurant: \n{matched_restaurants}\n")


# Example usage and test case
if __name__ == "__main__":
    # Initialize the RestaurantLookup class
    lookup_service = RestaurantLookup()

    # Run the test case
    lookup_service.test_lookup()
