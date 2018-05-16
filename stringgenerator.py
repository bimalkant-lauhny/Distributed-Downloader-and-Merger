import random

class NameGenerator:

    """To generate a random alpha nuumerical name"""

    def __init__(self):
        self.alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g','h', 'i', 'j', 'k',
        'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u','v', 'w', 'x', 'y', 
        'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1',
        '2', '3', '4', '5', '6', '7', '8', '9', '0'];
        self.max_length = 62

    # function for generating a random name string
    def generateName(self, length):
        name = '';
        index = random.randint(0,37273729);

        for key in range(length):
            index = (index + 6268282) % self.max_length
            name += self.alphabets[index];
            
        return name	
