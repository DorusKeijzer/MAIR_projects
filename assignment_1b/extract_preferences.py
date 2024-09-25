import re
import Levenshtein as lev
import random
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Ensure the stopwords corpus is downloaded
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')


class PreferenceExtractor:
    """
    Extracts user preferences (price range, location, and food type) 
    from user input using pattern matching and Levenshtein distance for fuzzy matching.
    """

    def __init__(self):
        # Predefined keywords for matching preferences
        self.price_keywords = ['cheap', 'moderate', 'expensive']
        self.location_keywords = ['north', 'south', 'east', 'west', 'centre']
        self.food_keywords = [
            'british', 'modern european', 'italian', 'romanian', 'seafood', 'chinese',
            'steakhouse', 'asian oriental', 'french', 'portuguese', 'indian', 'spanish',
            'european', 'vietnamese', 'korean', 'thai', 'moroccan', 'swiss', 'fusion',
            'gastropub', 'tuscan', 'international', 'traditional', 'mediterranean',
            'polynesian', 'african', 'turkish', 'bistro', 'north american',
            'australasian', 'persian', 'jamaican', 'lebanese', 'cuban', 'japanese',
            'catalan', 'world food', 'scottish', 'corsican', 'christmas food',
            'venetian', 'kosher', 'greek', 'belgian', 'polish', 'crossover'
        ]

        # Synonym mappings for preferences
        self.price_synonyms = {
            'cheap': ['cheap', 'inexpensive', 'affordable', 'budget', 'low-cost', 'economical', 'bargain', 'value'],
            'moderate': ['moderate', 'moderately priced', 'mid-priced', 'mid-range', 'average price', 'reasonably priced', 'fair-priced', 'standard-priced'],
            'expensive': ['expensive', 'pricey', 'high-end', 'luxurious', 'costly', 'upscale', 'premium', 'deluxe', 'top-tier']
        }

        self.location_synonyms = {
            'north': ['north', 'northern', 'up north', 'north side', 'northern part'],
            'south': ['south', 'southern', 'down south', 'south side', 'southern part'],
            'east': ['east', 'eastern', 'east side', 'eastern part'],
            'west': ['west', 'western', 'west side', 'western part'],
            'centre': ['centre', 'center', 'central', 'downtown', 'city center', 'city centre', 'heart of the city', 'middle of town']
        }

        self.cuisine_synonyms = {
            'british': ['british', 'english', 'traditional'],
            'italian': ['italian', 'pasta', 'pizza', 'spaghetti', 'lasagna'],
            'chinese': ['chinese', 'noodles', 'dim sum', 'mandarin cuisine'],
            'indian': ['indian', 'curry', 'tandoori', 'biryani', 'masala'],
            'japanese': ['japanese', 'sushi', 'sashimi', 'ramen'],
            'french': ['french', 'bistro', 'brasserie', 'patisserie'],
            'thai': ['thai', 'pad thai', 'spicy noodles'],
            'spanish': ['spanish', 'tapas', 'paella'],
            'seafood': ['seafood', 'fish', 'oysters', 'shrimp'],
            'steakhouse': ['steakhouse', 'steak', 'grill', 'beef', 'meat lovers'],
            # Add more cuisines and their synonyms as needed
        }

        # Mapping of broader food categories to more specific cuisines
        self.broader_food_categories = {
            'world food': ['international', 'fusion', 'modern european'],
            'crossover': ['fusion', 'international'],
            'gastropub': ['traditional', 'british'],
            'asian oriental': ['chinese', 'japanese', 'thai', 'korean', 'vietnamese']
        }

    def extract_preferences(self, user_input: str):
        """
        Extracts preferences from user input, including food type, price range, and location.
        If broader food categories are mentioned, they are mapped to more specific food types.

        :param user_input: The input provided by the user as a string
        :return: Dictionary containing extracted preferences and a list of fallback preferences
        """
        user_input = user_input.lower()
        preferences = {}
        fallback_preferences = []

        # Extract food preference, handling broader categories
        preferences['food_type'] = self._extract_food_type(user_input)

        # Extract price range preference
        preferences['price_range'] = self._extract_price_range(user_input)

        # Extract location preference
        preferences['location'] = self._extract_location(user_input)

        # Extract fallback preferences, e.g., "How about Greek food?"
        fallback_preferences = self._extract_fallback_preferences(user_input)

        return preferences, fallback_preferences

    def _extract_food_type(self, user_input: str) -> str:
        """
        Extracts the food type preference from user input. Handles broader food categories
        by mapping them to more specific cuisines.

        :param user_input: The input provided by the user as a string
        :return: The extracted food type or None if not found
        """
        # First, check for broader food categories (e.g., 'world food')
        for broad_term, specific_cuisines in self.broader_food_categories.items():
            if broad_term in user_input:
                # Join specific cuisines with OR condition
                return '|'.join(specific_cuisines)

        # Check for cuisine synonyms
        for cuisine, synonyms in self.cuisine_synonyms.items():
            for synonym in synonyms:
                if synonym in user_input:
                    return cuisine

        # If no synonym found, attempt to match directly
        return self._match_closest(user_input, self.food_keywords, 'food type')

    def _extract_price_range(self, user_input: str) -> str:
        """
        Extracts the price range preference from user input using synonyms mapping.

        :param user_input: The input provided by the user as a string
        :return: The extracted price range or None if not found
        """
        for price_range, synonyms in self.price_synonyms.items():
            for synonym in synonyms:
                if synonym in user_input:
                    return price_range

        # If no synonym found, attempt to match directly
        return self._match_closest(user_input, self.price_keywords, 'price range')

    def _extract_location(self, user_input: str) -> str:
        """
        Extracts the location preference from user input using synonyms mapping.

        :param user_input: The input provided by the user as a string
        :return: The extracted location or None if not found
        """
        for location, synonyms in self.location_synonyms.items():
            for synonym in synonyms:
                if synonym in user_input:
                    return location

        # If no synonym found, attempt to match directly
        return self._match_closest(user_input, self.location_keywords, 'location')

    def _match_closest(self, user_input: str, keyword_list: list, preference_type: str) -> str:
        # Tokenize the user input using NLTK's word_tokenize
        words = word_tokenize(user_input)
        # Update stop words
        stop_words = set(stopwords.words('english'))
        stop_words.update(['need', 'area', 'any'])
        # Filter out stop words and short words
        words = [word for word in words if word.lower(
        ) not in stop_words and len(word) > 4]
        # Use Levenshtein distance to find the closest match among words and phrases
        closest_matches = []
        min_distance = float('inf')
        for word in words:
            for keyword in keyword_list:
                distance = lev.distance(word.lower(), keyword.lower())
                # Adjust threshold based on word length
                max_distance = 1 if len(
                    word) <= 5 else 2 if len(word) <= 8 else 3
                if distance < min_distance and distance <= max_distance:
                    min_distance = distance
                    closest_matches = [keyword]
                elif distance == min_distance and distance <= max_distance:
                    closest_matches.append(keyword)
        # Return a random match if the minimal acceptable distance is met
        if min_distance <= 3:
            return random.choice(closest_matches)
        else:
            return None

    def _extract_fallback_preferences(self, user_input: str) -> list:
        """
        Extracts fallback preferences, such as alternative food types mentioned by the user.

        :param user_input: The input provided by the user as a string
        :return: A list of fallback food preferences
        """
        # Look for phrases like "How about X food?" or "Maybe some X cuisine"
        pattern = r'how about (\w+(?: \w+)?)|maybe some (\w+(?: \w+)?)'
        matches = re.findall(pattern, user_input)
        fallbacks = []
        for match in matches:
            food = match[0] if match[0] else match[1]
            food = food.strip()
            # Map the fallback food to predefined keywords
            for cuisine, synonyms in self.cuisine_synonyms.items():
                if food in synonyms:
                    fallbacks.append(cuisine)
                    break
            else:
                fallbacks.append(food)
        return fallbacks

    def test_extract_preferences(self):
        """
        Allows the user to input sentences and displays the extracted preferences.
        """
        print("Preference Extractor Test")
        print("-------------------------")
        print("Enter a sentence to extract preferences (type 'exit' to quit):")
        while True:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting the test.")
                break
            preferences, fallbacks = self.extract_preferences(user_input)
            print(f"Extracted Preferences: {preferences}")
            if fallbacks:
                print(f"Fallback Preferences: {fallbacks}")
            print()


# Example usage
if __name__ == "__main__":
    extractor = PreferenceExtractor()
    extractor.test_extract_preferences()
