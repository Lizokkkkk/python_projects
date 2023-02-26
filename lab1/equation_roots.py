a = int(input())
b = int(input())
c = int(input())

d = (b ** 2 - 4 * a * c)

if a != 0:
    if d == 0:
        print('x = ', (-b)/(2 * a))
    elif d > 0:
        print('x = ', (-b - sqrt(d)) / (2 * a))
        print('x = ', (-b + sqrt(d)) / (2 * a))
    else:
        print('Корней нет')
else:
    print('Квадратное уравнение не существует')
