from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine("mysql+pymysql://root:password@localhost/TypeFace")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = scoped_session(SessionLocal)

app = FastAPI()


def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.get("/restaurant_id/{id}")
async def restaurant(id: int, db=Depends(get_db)):
    result = db.execute(text("SELECT * FROM zomato WHERE id = :id"), {"id": id})
    restaurant = result.fetchone()
    # print(restaurant)
    # print(result)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    # Convert Row object to dictionary
    restaurant_dict = {key: value for key, value in zip(result.keys(), restaurant)}
    return restaurant_dict

@app.get("/all_restaurants")
async def all_restaurants(db=Depends(get_db)):
    result = db.execute(text("SELECT * FROM zomato"))
    restaurants = result.fetchall()
    # print(restaurants)
    # print(result);
    return [dict(zip(result.keys(), restaurant))["Restaurant_Name"] for restaurant in restaurants]
