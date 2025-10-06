from app import app, db, Product, Location, ProductMovement
from datetime import datetime, timedelta

# Wrap the database operations within the app's application context
with app.app_context():
    # Drop all tables and create them again
    db.drop_all()
    db.create_all()

    # Add products and locations
    p1 = Product(product_id='P-A', name='Product A')
    p2 = Product(product_id='P-B', name='Product B')
    p3 = Product(product_id='P-C', name='Product C')
    l1 = Location(location_id='L-X', name='Warehouse X')
    l2 = Location(location_id='L-Y', name='Warehouse Y')
    l3 = Location(location_id='L-Z', name='Warehouse Z')

    # Add products and locations to session
    db.session.add_all([p1, p2, p3, l1, l2, l3])
    db.session.commit()

    # Initialize base timestamp
    base = datetime.utcnow()

    # Create product movements
    movs = []
    movs.append(ProductMovement(movement_id='M1', timestamp=base - timedelta(days=10), product_id='P-A', qty=50, from_location=None, to_location='L-X'))
    movs.append(ProductMovement(movement_id='M2', timestamp=base - timedelta(days=9), product_id='P-B', qty=30, from_location=None, to_location='L-X'))
    movs.append(ProductMovement(movement_id='M3', timestamp=base - timedelta(days=8), product_id='P-A', qty=20, from_location='L-X', to_location='L-Y'))

    # Generate more movements for products
    for i in range(4, 21):
        if i % 3 == 0:
            movs.append(ProductMovement(movement_id=f'M{i}', timestamp=base - timedelta(days=i), product_id='P-A', qty=5, from_location=None, to_location='L-Z'))
        elif i % 3 == 1:
            movs.append(ProductMovement(movement_id=f'M{i}', timestamp=base - timedelta(days=i), product_id='P-B', qty=4, from_location='L-X', to_location='L-Y'))
        else:
            movs.append(ProductMovement(movement_id=f'M{i}', timestamp=base - timedelta(days=i), product_id='P-C', qty=7, from_location=None, to_location='L-Z'))

    # Add product movements to session and commit
    db.session.add_all(movs)
    db.session.commit()

    print('Created and populated database successfully.')
