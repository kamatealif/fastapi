from fastapi import FastAPI

items_db = [{'item_name': 'Foo'}, {'item_name': 'Bar'}, {'item_name': 'Baz'}]

app = FastAPI()

@app.get("/user/{user_id}/items/{item_id}")
async def read_items(user_id: str, item_id: str , q: str | None =  None, short: bool = False):
    item = {"item_id": item_id, "Owner id " : user_id}
    if q:
        item.update({"q": q})
    if not short:
         item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item 
    
    
    
@app.get('/items/{item_id}')
async def read_item(item_id: str, needy: str, skip=0, limit=10):
    item = {"item_id": item_id, "needy":  needy, "skip": skip, "limit": limit}
    return item