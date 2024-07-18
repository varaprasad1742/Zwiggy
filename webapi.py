from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session


engine = create_engine("mysql+pymysql://root:password@localhost:3306/TypeFace") # pymysql is the driver to connect mysql
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # sessionmaker is a factory for making session classes
db = scoped_session(SessionLocal) # scoped_session is a thread-local object that represents a registry of database sessions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="ui")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root(request: Request,response_class=HTMLResponse):
    return templates.TemplateResponse("home.html", {"request": request})



def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.get("/restaurant_id/{id}")
async def restaurant(request: Request,id: int, db=Depends(get_db),response_class=HTMLResponse):
    result = db.execute(text("SELECT * FROM zomato WHERE id = :id"), {"id": id})
    restaurant = result.fetchone()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    restaurant_dict = {key: value for key, value in zip(result.keys(), restaurant)}
    return templates.TemplateResponse("restaurant.html", {"restaurant": restaurant_dict, "request": request})

@app.get("/all_restaurants")
async def all_restaurants(page: int = Query(1, ge=1), db=Depends(get_db)):
    offset = (page - 1) * 50
    result = db.execute(text("SELECT id,Restaurant_Name, Address, Has_Online_delivery FROM zomato LIMIT 50 OFFSET :offset"), {"offset": offset})
    restaurants = result.fetchall()
    # print(restaurants)
    return [dict(zip(result.keys(), restaurant)) for restaurant in restaurants]


@app.get("/search")
async def search_restaurants(query: str = Query(...), db=Depends(get_db)):
    try:
        result = db.execute(
            text("SELECT id, Restaurant_Name, Aggregate_rating FROM zomato WHERE Restaurant_Name LIKE :query LIMIT 8"),
            {"query": f"{query}%"} # % is a wildcard character in MySQL
        )
        restaurants = result.fetchall()
        # print(restaurants)
        return [dict(zip(result.keys(), restaurant)) for restaurant in restaurants]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants_count")
async def restaurants_count(db=Depends(get_db)):
    result = db.execute(text("SELECT COUNT(*) FROM zomato"))
    count = result.scalar()
    return {"count": count}


@app.get("/random_restaurant")
async def random_restaurant(db=Depends(get_db)):
    result = db.execute(text("SELECT * FROM zomato ORDER BY RAND() LIMIT 1"))
    restaurant = result.fetchone()
    return dict(zip(result.keys(), restaurant))