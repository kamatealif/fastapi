from fastapi import FastAPI

items_db = [{'item_name': 'Foo'}, {'item_name': 'Bar'}, {'item_name': 'Baz'}]]

app = FastAPI()

@app.get("/items/")
async def read_items(skip = 0, limit = 10):
    return items_db[skip: skip + limit]