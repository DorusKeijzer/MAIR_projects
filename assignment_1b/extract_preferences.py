import re
import random
import assignment_1c.config
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import Levenshtein as lev

# Ensure the stopwords corpus is downloaded
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)


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
            'moderate': ['moderate', 'mid-priced', 'mid-range', 'average price', 'reasonably priced', 'standard-priced'],
            'expensive': ['expensive', 'pricey', 'high-end', 'luxurious', 'costly', 'upscale', 'premium', 'deluxe']
        }

        # Specific phrases indicating no preference for each category
        self.no_food_preference_phrases = ['any food', 'no preference for food', 'any cuisine', 'any type of food', "don't care about food", "doesn't matter for food"]
        self.no_price_preference_phrases = ['any price', 'no preference for price', 'any price is ok', 'any price is fine', "don't care about price", "doesn't matter for price"]
        self.no_location_preference_phrases = ['any location', 'no preference for location', 'any area', 'any place', "don't care about location", "doesn't matter where"]

        self.location_synonyms = {
            'north': ['north', 'northern', 'up north', 'north side', 'northern part'],
            'south': ['south', 'southern', 'down south', 'south side', 'southern part'],
            'east': ['east', 'eastern', 'east side', 'eastern part'],
            'west': ['west', 'western', 'west side', 'western part'],
            'centre': ['centre', 'center', 'central', 'downtown', 'city center', 'city centre', 'heart of the city']
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

        # Additional requirements keywords
        self.additional_requirements_keywords = ['romantic', 'touristic', 'children', 'assigned seats']

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

        preferences['food_type'] = self._extract_food_type(user_input)
        preferences['price_range'] = self._extract_price_range(user_input)
        preferences['location'] = self._extract_location(user_input)

        # Extract fallback preferences
        fallback_preferences = self._extract_fallback_preferences(user_input)

        return preferences, fallback_preferences

    def _extract_food_type(self, user_input: str) -> str:
        # First, check for phrases indicating no preference
        if any(phrase in user_input for phrase in self.no_food_preference_phrases):
            return 'any'

        # Check for broader food categories
        for broad_term, specific_cuisines in self.broader_food_categories.items():
            if broad_term in user_input:
                return '|'.join(specific_cuisines)

        # Check for cuisine synonyms
        for cuisine, synonyms in self.cuisine_synonyms.items():
            for synonym in synonyms:
                if synonym in user_input:
                    return cuisine

        # If no synonym found, attempt to match directly
        return self._match_closest(user_input, self.food_keywords)

    def _extract_price_range(self, user_input: str) -> str:
        # Check for phrases indicating no preference
        if any(phrase in user_input for phrase in self.no_price_preference_phrases):
            return 'any'

        for price_range, synonyms in self.price_synonyms.items():
            for synonym in synonyms:
                if synonym in user_input:
                    return price_range

        # If no synonym found, attempt to match directly
        return self._match_closest(user_input, self.price_keywords)

    def _extract_location(self, user_input: str) -> str:
        # Check for phrases indicating no preference
        if any(phrase in user_input for phrase in self.no_location_preference_phrases):
            return 'any'

        for location, synonyms in self.location_synonyms.items():
            for synonym in synonyms:
                if synonym in user_input:
                    return location

        # If no synonym found, attempt to match directly
        return self._match_closest(user_input, self.location_keywords)

    def _match_closest(self, user_input: str, keyword_list: list) -> str:
        if assignment_1c.config.levenshtein:
            # Use Levenshtein distance for fuzzy matching
            words = word_tokenize(user_input)
            stop_words = set(stopwords.words('english'))
            stop_words.update(['need', 'area', 'any', 'price', 'pricerange'])
            words = [word for word in words if word.lower() not in stop_words and len(word) > 4]
            closest_matches = []
            min_distance = float('inf')
            for word in words:
                for keyword in keyword_list:
                    distance = lev.distance(word.lower(), keyword.lower())
                    max_distance = 1 if len(word) <= 5 else 2 if len(word) <= 8 else 3
                    if distance < min_distance and distance <= max_distance:
                        min_distance = distance
                        closest_matches = [keyword]
                    elif distance == min_distance and distance <= max_distance:
                        closest_matches.append(keyword)
            if min_distance <= 3:
                return random.choice(closest_matches)
            else:
                return None
        else:
            # Use exact matching
            for keyword in keyword_list:
                if keyword.lower() in user_input:
                    return keyword
            return None

    def _extract_fallback_preferences(self, user_input: str) -> list:
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

    def extract_additional_requirements(self, user_input: str) -> dict:
        user_input = user_input.lower()
        additional_requirements = {}

        words = word_tokenize(user_input)
        words_set = set(words)

        for keyword in self.additional_requirements_keywords:
            if keyword in words_set:
                additional_requirements[keyword] = True

        return additional_requirements
