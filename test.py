def phone_number() :
    number = int(input('Please enter your phone number. \n'))
    return number

def account() :
    try :
        first_name = input('Please enter your first name. \n')
        last_name = input('Please enter your last name. \n')
        phone = phone_number()
        print(f'{first_name} {last_name} \n {phone}')
    except ValueError :
        print('Incorrect phone number.')

# print(type(None))

from polynomial import Polynomial
from field import FieldElement, Field

f = Field(11)
P = Polynomial([FieldElement(f, 0), FieldElement(f, 1), FieldElement(f, 2)])
Q = Polynomial([FieldElement(f, 0), FieldElement(f, 1), FieldElement(f, 2), FieldElement(f, 3)])
print(f'P(X) = {P}')
print(f'Q(X) = {Q}')
print(f'(P+Q)(X) = {P+Q}')
print(f'(P*Q)(X) = {P*Q}')
print(f'(P**4)(X)) = {P**4}')
print(f'P(Q(X)) = {P(Q)}')
# P(ant = FieldElement(Field(9), 0))

