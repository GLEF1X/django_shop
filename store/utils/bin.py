# qs1 = Order.objects.select_related('user').defer('user__email').prefetch_related(
#     'product'
# ).defer('product__description', 'product__created_at').filter(
#     ~Q(user__first_name__exact='Youra')
#     &
#     ~Q(order_date__year=2020)).annotate(Count('user'))
# qs2 = User.objects.select_related('order__order_date').first()#.values('first_name', 'last_name', 'email').first()
# orders = await first_command()
# annotate(order_price=Sum(F('unit_price') * F('quantity'), output_field=DecimalField()))
# -------------------------------------------Users------------------------------------------------------------------
# user1 = User(
#     first_name='Глеб',
#     last_name='Гаранин',
#     email='glebgar567@gmail.com',
# ).save()
# user2 = User(
#     first_name='Даниил',
#     last_name='Плоцких',
#     email='daniilplotskih@gmail.com',
# ).save()
# user3 = User(
#     first_name='Александр',
#     last_name='Шеметун',
#     email='aleksandrshemetun@gmail.com',
# ).save()

# Category(
#     slug='clothes',
#     name='Одежда'
# ).save()
# Product.objects.filter().delete()
# Product.objects.bulk_create([
#     Product(product_name='Футболка', category_id=1, quantity=50, unit_price=170, size='S',
#             description='Простая футболка'),
#     Product(product_name='Куртка', category_id=1, quantity=40, unit_price=254, size='M',
#             description='Куртка из новой колекции'),
#     Product(product_name='Шапка', category_id=1, quantity=14, unit_price=120, size='M',
#             description='Шапка из моей колекции'),
# ])
# Order().save_(
#     product_id=4,
#     user_id=1,
#     quantity=10
# )
# Order().save_(
#     product_id=5,
#     user_id=2,
#     quantity=5
# )
# Order().save_(
#     product_id=6,
#     user_id=3,
#     quantity=1
#
