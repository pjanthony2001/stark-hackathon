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

from utils.polynomial import Polynomial
from utils.field import FieldElement, Field

f = Field(11)
P = Polynomial([FieldElement(f, 0), FieldElement(f, 1), FieldElement(f, 2)])
R = Polynomial([FieldElement(f, 1), FieldElement(f, 0), FieldElement(f, 0)])
S = Polynomial([FieldElement(f, 0), FieldElement(f, 1), FieldElement(f, 0)])
Q = Polynomial([FieldElement(f, 0), FieldElement(f, 1), FieldElement(f, 2), FieldElement(f, 3)])
# print(f'P(X) = {P}, deg = {P.deg()}')
# print(f'Q(X) = {Q}, deg = {Q.deg()}')
# print(f'R(X) = {R}, deg = {R.deg()}')
# print(f'Q(X) = {S}, deg = {S.deg()}')

# print(f'(P+Q)(X) = {P+Q}')
# print(f'(P*Q)(X) = {P*Q}')
# print(f'(P**4)(X)) = {P**4}')
# print(f'P(Q(X)) = {P(Q)}')
# P(ant = FieldElement(Field(9), 0))

print(f'P(3) = {P(FieldElement(f, 3))} [11]')

# a = FieldElement(f, 4)
# for exp in range(20) :
#     print(f'{a}**{exp} = {a**exp} [11]')

d1 = {'a' : 1, 'b' : 2}
d2 = {'b' : 2, 'a' : 1}
print(d1 == d2)
s = ''
s += 'a'
print(s)