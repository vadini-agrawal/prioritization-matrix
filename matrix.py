import tokens

from notion.client import NotionClient
from notion.block import TextBlock, TodoBlock, SubheaderBlock

def calculate_distance(urgency, importance, origin):
    dist = ((urgency - origin[0])**2 + (importance-origin[1])**2)**.5 
    return dist

def sort_scores(values, indices, origin):
    current = dict(indices)
    for ind in current:
        current[ind] = calculate_distance(values[ind]["urgency"], values[ind]["importance"], origin)
    output = [i[0] for i in sorted(current.items(), key=lambda x: x[1], reverse=True)]
    return output

if __name__ == "__main__":
    client = NotionClient(token_v2=tokens.token_v2)

    db = client.get_collection_view("https://www.notion.so/vadini12345678/a91966c1e8514085a52d0d37c9fa9955?v=5fc930601e0a42f3a8daac9b53f2d425")
    page = client.get_block("https://www.notion.so/vadini12345678/Framework-68c880edb57c4c40ae775862615448d8")

    for child in page.children:
        if type(child) == TodoBlock or type(child) == SubheaderBlock:
            child.remove()

    values = {}
    index = 0

    do_next = {}
    do_now = {}
    do_last = {}
    do_never = {}

    error_block = page.children.add_new(TextBlock, title="")
    error_block.remove()

    for row in db.collection.get_rows():
        if row.urgency < 0 or row.urgency > 10 or row.importance < 0 or row.importance > 10:
            error_block.title = "Oops! Make sure your values are between 0 and 10."
        else:
            values[index] = {"name": row.task, "urgency": row.urgency, "importance": row.importance}
            if row.urgency > 5 and row.importance > 5:
                do_now[index] = 0
            elif row.urgency >= 5 and row.importance <= 5:
                do_last[index] = 0
            elif row.urgency < 5 and row.importance > 5:
                do_next[index] = 0
            elif row.urgency <= 5 and row.importance <= 5:
                do_never[index] = 0
            index += 1

    do_now = sort_scores(values, do_now, (5, 5))
    do_last = sort_scores(values, do_last, (5, 0))
    do_next = sort_scores(values, do_next, (0, 5))
    do_never = sort_scores(values, do_never, (0, 0)) 

    error_block.remove()

    do_now_title = page.children.add_new(SubheaderBlock, title="Do Now")
    for i in do_now:
        page.children.add_new(TodoBlock, title=values[i]["name"])
    page.children.add_new(SubheaderBlock, title="Do Next")
    for i in do_next:
        page.children.add_new(TodoBlock, title=values[i]["name"])
    page.children.add_new(SubheaderBlock, title="Do Last")
    for i in do_last:
        page.children.add_new(TodoBlock, title=values[i]["name"])
    page.children.add_new(SubheaderBlock, title="Do Never")
    for i in do_never:
        page.children.add_new(TodoBlock, title=values[i]["name"])
    
