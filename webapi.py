from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
import requests
from PIL import Image
import os


def download_image(restaurant_name):
    # Replace spaces in restaurant name with underscores for URL compatibility
    restaurant_name = restaurant_name.replace(' ', '_')
    # Example URL for image search based on restaurant name
    search_url = f"https://example.com/images/search/{restaurant_name}"
    
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            # Create 'images' folder if it doesn't exist
            if not os.path.exists('images'):
                os.makedirs('images')
            
            # Save image to 'images' folder
            with open(f'images/{restaurant_name}.jpg', 'wb') as f:
                f.write(response.content)
            
            return f'images/{restaurant_name}.jpg'
        else:
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None



engine = create_engine("mysql+pymysql://root:password@localhost/TypeFace")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = scoped_session(SessionLocal)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust according to your requirements
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
    offset = (page - 1) * 20
    result = db.execute(text("SELECT id,Restaurant_Name, Address, Has_Online_delivery FROM zomato LIMIT 20 OFFSET :offset"), {"offset": offset})
    restaurants = result.fetchall()
    # print(restaurants)
    return [dict(zip(result.keys(), restaurant)) for restaurant in restaurants]

@app.get("/restaurants_count")
async def restaurants_count(db=Depends(get_db)):
    result = db.execute(text("SELECT COUNT(*) FROM zomato"))
    count = result.scalar()
    return {"count": count}
